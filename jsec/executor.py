#!/usr/bin/env python
import configparser
import copy
import importlib
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

# import deepdiff

from jsec.gppw import GlobalPlatformProWrapper
from jsec.settings import PROJECT_ROOT
from jsec.utils import SDKVersion, cd
from jsec.utils import AttackConfigParser

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


class CommonStage:
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
        self.aids = configparser.ConfigParser()
        self.uninstall_stages = []

        self.config = AttackConfigParser(strict=False)
        self.installed_applets = []
        self.stages = None

        self._load_config()
        try:
            self.sdks = self.config.get_sdk_versions("BUILD", "versions")
        except KeyError:
            self.sdks = None

    def _load_config(self) -> None:
        self.config.read(self.workdir / "config.ini")

    def _load_aids(self) -> None:
        self.aids.read(self.workdir / "aids.ini")

    def get_stages(self) -> List[dict]:
        # TODO should we double check the content of th STAGES before
        # proceeding? e.g. the types of the entries
        # first load stages from `<attackname>`.py
        stages = self.import_stages()
        if stages is not None:
            return copy.deepcopy(stages)

        module_file = self.workdir / (self.attack_name + ".py")
        raise ValueError(
            "Cannot load Scenario.STAGES from %s. Does it exist?" % module_file
        )

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
            stages = getattr(importlib.import_module(relative_module_path), "Scenario",)
            return stages.STAGES
        except (ModuleNotFoundError, AttributeError):
            pass

        return None

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
                uninstall_stage = {"name": "uninstall", "path": path, "installed": True}
            else:
                # when the installation is not successful we still want to add uninstall stage
                # and mark it as skipped
                uninstall_stage = {
                    "name": "uninstall",
                    "path": path,
                    "installed": False,
                }
            self.uninstall_stages.append(uninstall_stage)

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

    def _prepare_uninstall(self, *args, **kwargs):
        pass

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
        rid = bytes.fromhex(self.aids["BUILD"]["pkg.rid"])
        pix = bytes.fromhex(self.aids["BUILD"]["applet.pix"])
        aid = rid + pix

        return aid

    def _prepare_send(self, *args, **kwargs):
        pass

    def _send(self, *args, payload: str, **kwargs):
        # TODO prepare payload
        aid = self.construct_aid()
        # TODO payload may be of varying kinds of hexa/int values values
        payload = self._parse_payload(payload)
        return self.gp.apdu(payload, aid)

    def _assess_send(self, result, *args, expected: str = "9000", **kwargs):
        command_apdu = self._parse_payload(kwargs["payload"]).hex().upper()
        success = True
        if result["returncode"] != 0:
            success = False
        # TODO verify expected
        # by default we expect 9000 status word
        try:
            if result["communication"][command_apdu]["status"] != expected:
                success = False
        except KeyError:
            success = False

        result["success"] = success
        # FIXME maybe adding all kwargs is too much
        result.update(kwargs)
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
        """
        Returns the intersection of SDKVersions the attack can be build for
        and the ones supported by the Card
        """
        attack_sdk_versions = SDKVersion.from_list(
            self.config["BUILD"]["versions"], sep=","
        )
        return list(set(attack_sdk_versions).intersection(set(self.card.sdks)))

    def _determine_version(self) -> "SDKVersion":
        # determine the newest SDK version supported both by the card and the attack
        attack_versions = SDKVersion.from_list(self.config["BUILD"]["versions"])
        try:
            newest = list(set(attack_versions).intersection(set(self.card.sdks)))[-1]
        except IndexError:
            newest = attack_versions[0]
            log.warning(
                "Could not determine SDK Version, defaulting to '%s'", str(newest)
            )
        return newest

    def execute(self, sdk_version=None, **kwargs) -> list:
        self._load_aids()
        stages = self.get_stages()
        self.report = []

        n_stages = self.get_stages_len(stages)
        x = 1
        # FIXME print successes of stages
        # FIXME stop on SCARD_NO_TRANSANCT in STDOUT/STDERR
        for i, stage_data in enumerate(stages):
            stage = stage_data.pop("name")
            result = self._run_stage(
                stage, **stage_data, sdk_version=sdk_version, **kwargs
            )
            try:
                success = "pass" if result["success"] else "fail"
            except KeyError:
                success = ""
            print("    [%2d/%2d] %s: %s" % (x, n_stages, stage, success))
            x += 1

            result["name"] = stage
            result["skipped"] = False
            # if i:
            #     result["diff-state"] = deepdiff.DeepDiff(
            #         result["state"], self.report[-1]["state"]
            #     ).to_dict()
            # else:
            #     result["diff-state"] = {}
            self.report.append(result)
            if not self.optional_stage(stage, stage_data) and not result["success"]:
                break

        # fill in the rest of the stages, that were not executed
        for stage_data in stages[i + 1 :]:
            stage = stage_data.pop("name")
            print("    [%2d/%2d] %s: skip" % (x, n_stages, stage))
            x += 1
            # print(stage)
            result = {
                "name": stage,
                "success": False,
                "skipped": True,
                # "state": None,
                # "diff-state": None,
            }
            try:
                # in case we skip, we just copy the previous state - assuming, that skipping
                # a stage cannot change the data on the card
                result["state"] = self.report[-1]["stage"]
            except KeyError:
                result["state"] = None

            self.report.append(result)

        while self.uninstall_stages:
            # FIXME add 'pass' 'fail' to the print
            stage_data = self.uninstall_stages.pop()
            stage = stage_data.pop("name")
            print("    [%2d/%2d] %s" % (x, n_stages, stage), end="")
            x += 1
            if stage_data["installed"]:
                result = self._run_stage(
                    stage, **stage_data, sdk_version=sdk_version, **kwargs
                )
                result["skipped"] = False
                if result["success"]:
                    print(" pass")
                else:
                    print(" fail")
            else:
                result = copy.deepcopy(stage_data)
                result["skipped"] = True
                print(" skip")

            result["name"] = stage
            # if self.report[-1]["state"] is not None:
            #     result["diff-state"] = deepdiff.DeepDiff(
            #         result["state"], self.report[-1]["state"]
            #     ).to_dict()
            # else:
            #     result["diff-state"] = {}
            #     try:
            #         # in case we skip, we just copy the previous state - assuming, that skipping
            #         # a stage cannot change the data on the card
            #         result["state"] = self.report[-1]["stage"]
            #     except KeyError:
            #         result["state"] = None
            self.report.append(result)

        # FIXME add also the short description of the attacks
        return self.report

    @staticmethod
    def optional_stage(stage: str, stage_data: dict) -> bool:
        try:
            return stage_data["optional"]
        except KeyError:
            if stage == CommonStage.install:
                # install is required by default
                return False
            elif stage == CommonStage.uninstall:
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
            log.info("Cannot find stage method '%s'", prepare_stage)

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

    @staticmethod
    def get_stages_len(stages):
        """
        The actual number of stages unknown before runtime, because the `uninstall`
        stages are called only in case of successful installation.
        """
        length = len(stages)
        install_stages = [1 for stage in stages if stage["name"] == "install"]
        length += sum(install_stages)
        return length


if __name__ == "__main__":
    pass
