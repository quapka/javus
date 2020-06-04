#!/usr/bin/env python
from abc import ABC, abstractmethod
import re
from pathlib import Path

from jsec.gppw import GlobalPlatformProWrapper
from jsec.utils import cd
from jsec.utils import SDKVersion
import configparser
import logging

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

        self.config = configparser.ConfigParser(strict=False)
        self.installed_applets = []
        self.stages = None

        self._load_config()

    def _load_config(self) -> None:
        self.config.read(self.workdir / "config.ini")

    def get_stages(self):
        return self.config["STAGES"]

    def _install(self, value: str, sdk_version: SDKVersion):
        # value is a path/string, that can include {version} for differentiating between
        # different versions
        if sdk_version is None:
            sdk_version = self._determine_version()

        path = value.format(version=sdk_version.raw)
        log.info("Attempt to install applet: %s", path)
        with cd(self.workdir):
            result = self.gp.install(path)
            if result.returncode == 0:
                self.installed_applets.append(path)

        return result

    def _uninstall(self, value: str):
        if self.installed_applets is not None:
            # attemp to uninstall the installed applets in reversed order
            while self.installed_applets:
                path = self.installed_applets.pop()
                with cd(self.workdir):
                    self.gp.uninstall(path)

    def construct_aid(self) -> bytes:
        # FIXME this method is a gimmick to be overriden by the custom Executors
        rid = bytes.fromhex(self.config["BUILD"]["pkg.rid"])
        pix = bytes.fromhex(self.config["BUILD"]["applet.pix"])
        aid = rid + pix

        return aid

    def _send(self, raw_payload: str):
        # TODO prepare payload
        aid = self.construct_aid()
        # TODO payload may be of varying kinds of hexa/int values values
        payload = self._parse_payload(raw_payload)
        return self.gp.apdu(payload, aid)

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

    def execute(self, sdk_version=None) -> list:
        stages = self.get_stages()
        report = []

        # perform next stage only if the previous one was successful
        for stage, value in stages.items():
            stage = stage.strip().upper()
            if stage == "INSTALL":
                result = self._install(value, sdk_version=sdk_version)
            elif stage.startswith("SEND"):
                result = self._send(value)
            elif stage == "UNINSTALL":
                result = self._uninstall(value)

            report.append({stage: result})
        return report


if __name__ == "__main__":
    pass
