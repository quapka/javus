#!/usr/bin/env python
from abc import ABC, abstractmethod
import re
from pathlib import Path

from jsec.gppw import GlobalPlatformProWrapper
from jsec.utils import cd
import configparser
import logging

# TODO add some log initializer
log = logging.getLogger(__file__)
# TODO add handler for printing
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class Attack(ABC):
    @abstractmethod
    def uniqfy(self):
        # TODO maybe have default aids in config.ini and rewrite only aids.ini
        pass


class AbstractAttackExecutor(ABC):
    @abstractmethod
    def execute(self):
        pass


class BaseAttackExecutor(AbstractAttackExecutor):
    def __init__(self, gp: GlobalPlatformProWrapper, workdir: Path, version: str):
        self.gp = gp
        self.workdir = Path(workdir).resolve()
        self.version = version

        self.config = configparser.ConfigParser()
        self.installed_applets = None
        self.stages = None

        self._load_config()

    def _load_config(self) -> None:
        self.config.read(self.workdir / "config.ini")

    def get_stages(self):
        return self.config["STAGES"]

    def _install(self, value: str):
        # value is a path/string, that can include {version} for differentiating between
        # different versions
        path = value.format(version=self.version)
        log.info("Attempt to install applet: %s", path)
        with cd(self.workdir):
            return self.gp.install(path)

    def _uninstall(self, value: str):
        if self.installed_applets is not None:
            for path in self.installed_applets[::-1]:
                with cd(self.workdir):
                    self.gp.uninstall(path)

    def construct_aid(self) -> bytes:
        # FIXME this method is a gimmick to be overriden by the custom Executors
        return bytes.fromhex(self.config["BUILD"]["aid"])

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

    def execute(self) -> list:
        stages = self.get_stages()
        report = []

        for stage, value in stages.items():
            stage = stage.strip().upper()
            if stage == "INSTALL":
                result = self._install(value)
            elif stage.startswith("SEND"):
                result = self._send(value)
            elif stage == "UNINSTALL":
                result = self._uninstall(value)

            report.append({stage: result})
        return report


if __name__ == "__main__":
    pass
