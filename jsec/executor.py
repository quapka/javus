#!/usr/bin/env python
import configparser
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
import importlib

from typing import List

from jsec.gppw import GlobalPlatformProWrapper
from jsec.utils import SDKVersion, cd

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
            return stages
        stages = self.parse_config_stages()
        if stages is not None:
            return stages

        raise ValueError("Cannot load attack stages")

    def import_stages(self):
        try:
            stages = getattr(
                importlib.import_module(
                    f"jsec.data.attacks.{self.attack_name}.{self.attack_name}"
                ),
                "Stages",
            )
        except (ModuleNotFoundError, AttributeError):
            pass

        return stages.STAGES

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

        path = path.format(version=self.sdk_version.raw)
        log.info("Attempt to install applet: %s", path)
        with cd(self.workdir):
            result = self.gp.install(path)
            # if result["returncode"] == 0:
            #     self.installed_applets.append(path)

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

    def _send(self, payload: str, *args, **kwargs):
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

    def _determine_version(self) -> "SDKVersion":
        # determine the newest SDK version supported both by the card and the attack
        attack_versions = SDKVersion.from_list(self.config["BUILD"]["versions"])
        return list(set(attack_versions).intersection(set(self.card.sdks)))[-1]

    def execute(self, sdk_version=None, **kwargs) -> list:
        stages = self.get_stages()
        report = []

        # FIXME perform next stage only if the previous one was successful
        for stage_data in stages:
            stage = stage_data.pop("name")
            result = self._run_stage(
                stage, **stage_data, sdk_version=sdk_version, **kwargs
            )
            # if stage == "INSTALL":
            #     result = self._install(value, sdk_version=sdk_version)
            # elif stage.startswith("SEND"):
            #     result = self._send(value)
            # elif stage == "UNINSTALL":
            #     result = self._uninstall(value)

            report.append({stage: result})

        return report

    def _run_stage(self, raw_stage: str, *args, **kwargs):
        stage = self._create_stage_name(raw_stage)
        prepare_stage = "_prepare_" + stage
        try:
            prepare_method = getattr(self, prepare_stage)
        except AttributeError:
            log.error("Cannot find stage method '%s'", prepare_stage)

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
