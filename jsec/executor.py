#!/usr/bin/env python
import configparser
import logging
import re
import copy
from abc import ABC, abstractmethod
from pathlib import Path
import importlib

from typing import List, Optional

from jsec.gppw import GlobalPlatformProWrapper
from jsec.utils import SDKVersion, cd
from jsec.settings import PROJECT_ROOT

# TODO add some log initializer
log = logging.getLogger(__file__)
# TODO add handler for printing
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class AbstractAttackExecutor(ABC):
    @abstractmethod
    def execute(self):
        pass


class BaseStages:
    install = "install"
    send = "send"
    uninstall = "uninstall"


class BaseAttackExecutor(AbstractAttackExecutor):
    def __init__(
        self,
        card: "Card",
        gp: GlobalPlatformProWrapper,
        workdir: Path,
        sdk: SDKVersion = None,
    ):
        self.card = card
        self.gp = gp
        self.workdir = Path(workdir).resolve()
        # FIXME
        self.attack_name = self.workdir.name

        self.config = configparser.ConfigParser(strict=False)
        self.installed_applets = []
        self.stages = None

        self._load_config()

    def _load_config(self) -> None:
        self.config.read(self.workdir / "config.ini")

    def get_stages(self) -> List[dict]:
        # first load stages from `<attackname>`.py
        stages = self.import_stages()
        if stages is not None:
            return copy.deepcopy(stages)
        stages = self.parse_config_stages()
        if stages is not None:
            return copy.deepcopy(stages)

        raise ValueError("Cannot load attack stages")

    def import_stages(self) -> Optional[List[dict]]:
        # the module name can be inferred from the paths
        # TODO getting the module path feels a bit hackish - wonder if that works from other
        # folders as well - it does
        module_name = self.workdir.name
        relative_module_path = (
            str(self.workdir.relative_to(PROJECT_ROOT)).replace("/", ".")
            + "."
            + module_name
        )
        try:
            stages = getattr(importlib.import_module(relative_module_path), "Stages",)
            return stages.STAGES
        except (ModuleNotFoundError, AttributeError):
            pass

        return None

    def parse_config_stages(self) -> List[dict]:
        stages = []
        for key, values in self.config["STAGES"].items():
            for value in [x.strip() for x in values.splitlines() if x]:
                stages.append({key: value})

        return stages

    def _prepare_install(self, *args, **kwargs):
        pass

    def _install(self, path: str, sdk_version: SDKVersion, *args, **kwargs):
        # value is a path/string, that can include {version} for differentiating between
        # different versions
        if sdk_version is None:
            self.sdk_version = self._determine_version()
        else:
            self.sdk_version = sdk_version

        path = path.format(version=self.sdk_version.raw)
        log.info("Attempt to install applet: %s", path)
        with cd(self.workdir):
            result = self.gp.install(path)
            if result["returncode"] == 0:
                self.uninstall_stages.append({"name": "uninstall", "path": path})

        return result

    def _assess_install(self, result, *args, **kwargs):
        success = True
        # FIXME few naive checks, but we can also use --dump on install command
        # and make sure e.g. the status words are 9000
        if result["returncode"] != 0:
            success = False

        if "CAP loaded" not in result["stdout"]:
            success = False

        # make sure it is in the CardState after the installation
        result["success"] = success
        return result

    def _uninstall(self, path: str, sdk_version: SDKVersion, *args, **kwargs):
        # result = []
        # setting SDKVersion is done in _install, that is kinda weird
        path = path.format(version=self.sdk_version.raw)
        # if self.installed_applets is not None:
        #     # attemp to uninstall the installed applets in reversed order
        #     while self.installed_applets:
        # path = self.installed_applets.pop()
        with cd(self.workdir):
            result = self.gp.uninstall(path)

        return result

    def _assess_uninstall(self, result, *args, **kwargs):
        success = True
        if result["returncode"] != 0:
            success = False

        if "deleted" not in result["stdout"]:
            success = False

        result["success"] = success
        return result

    def construct_aid(self) -> bytes:
        # FIXME this method is a gimmick to be overriden by the custom Executors
        rid = bytes.fromhex(self.config["BUILD"]["pkg.rid"])
        pix = bytes.fromhex(self.config["BUILD"]["applet.pix"])
        aid = rid + pix

        return aid

    def _send(self, *args, payload: str, **kwargs):
        # TODO prepare payload
        aid = self.construct_aid()
        # TODO payload may be of varying kinds of hexa/int values values
        payload = self._parse_payload(payload)
        return self.gp.apdu(payload, aid)

    def _assess_send(self, result, *args, **kwargs):
        sucess = True
        result["success"] = True
        return result

    def _parse_payload(self, raw: str) -> bytes:
        clean = self._clean_payload(raw)
        if not clean:
            return b""

        separated = self._separate_payload(clean)
        if separated:
            try:
                return bytes([int(x, 16) for x in separated])
            except ValueError:
                pass

            try:
                return bytes([int(x) for x in separated])
            except ValueError:
                pass
        else:
            # first assume it is hexadecimal string without spaces and 0x prefix
            try:
                return bytes.fromhex(clean)
            except ValueError:
                pass

        # FIXME should raise some internal error, that it cannot continue with the attack
        # TODO log it
        raise RuntimeError("Cannot create a valid payload")

    @staticmethod
    def _separate_payload(raw: str) -> list:
        comma_separated = raw.split(",")
        if [raw] != comma_separated:
            return [x.strip() for x in comma_separated]

        space_separated = raw.split()
        if [raw] != space_separated:
            return [x.strip() for x in space_separated]
        return []

    @staticmethod
    def _clean_payload(raw: str) -> str:
        # remove excess whitespace
        stripped = raw.strip()
        # reduce whitespace
        reduced = re.sub(r"\s+", " ", stripped)
        return reduced

    def possible_versions(self) -> List["SDKVersion"]:
        r"""Returns the intersection of SDKVersions the attack can be build for
        and the ones supported by the Card"""
        attack_sdk_versions = SDKVersion.from_list(
            self.config["BUILD"]["versions"], sep=","
        )
        return list(set(attack_sdk_versions).intersection(set(self.card.sdks)))

    def _determine_version(self) -> "SDKVersion":
        # determine the newest SDK version supported both by the card and the attack
        attack_versions = SDKVersion.from_list(self.config["BUILD"]["versions"])
        newest = list(set(attack_versions).intersection(set(self.card.sdks)))[-1]
        print(newest)
        return newest

    def execute(self, sdk_version=None, **kwargs) -> list:
        stages = self.get_stages()
        report = []

        # FIXME perform next stage only if the previous one was successful
        for i, stage_data in enumerate(stages):
            stage = stage_data.pop("name")
            result = self._run_stage(
                stage, **stage_data, sdk_version=sdk_version, **kwargs
            )

            report.append({stage: result})
            if not self.optional_stage(stage, stage_data) and not result["success"]:
                break

        # fill in the rest of the stages, that were not executed
        for stage_data in stages[i + 1 :]:
            stage = stage_data.pop("name")
            report.append({stage: {"success": False, "skipped": True}})

        for i, stage_data in enumerate(self.uninstall_stages[:-1]):
            stage = stage_data.pop("name")
            result = self._run_stage(
                stage, **stage_data, sdk_version=sdk_version, **kwargs
            )

            report.append({stage: result})

        return report

    @staticmethod
    def optional_stage(stage: str, stage_data: dict) -> bool:
        try:
            return stage_data["optional"]
        except KeyError:
            if stage == BaseStages.install:
                # install is required by default
                return False
            elif stage == BaseStages.uninstall:
                # uninstall stage is optional as it makes sense to continue uninstalling
                # applets even if some cannot be uninstalled
                return True
        # any other stage is deemed required
        return False

    def _run_stage(self, raw_stage: str, *args, **kwargs):
        stage = self._create_stage_name(raw_stage)
        prepare_stage = "_prepare_" + stage
        try:
            prepare_method = getattr(self, prepare_stage)
        except AttributeError:
            log.warning("Cannot find stage method '%s'", prepare_stage)

            # prepare_method is optional and lambda cannot use *args, **kwargs
            def prepare_method(*args, **kwargs):
                pass

        try:
            stage_method = getattr(self, "_" + stage)
        except AttributeError:
            log.error("Cannot find stage method '%s'", stage)
            # TODO this method is not optional

        assess_stage = "_assess_" + stage
        try:
            assess_method = getattr(self, assess_stage)
        except AttributeError:
            log.error("Cannot find stage method '%s'", assess_stage)
            # TODO this method is not optional

        prepare_method(*args, **kwargs)
        result = stage_method(*args, **kwargs)
        result = assess_method(result, *args, **kwargs)
        result["skipped"] = False
        return result

    @staticmethod
    def _create_stage_name(stage: str) -> str:
        stage = stage.strip().lower()
        stage = re.sub(r" ", "_", stage)
        stage = re.sub(r"\s+", "", stage)

        if not stage:
            raise RuntimeError("'stage' name cannot be empty")
        return stage


if __name__ == "__main__":
    pass
