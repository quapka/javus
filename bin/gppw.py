#!/usr/bin/env python

from jcvmutils.utils import MongoConnection
from jcvmutils.utils import CommandLineApp

# from jcvmutils.utils import LOG_LEVELS
import configparser

import subprocess
import enum
import logging

log = logging.getLogger(__file__)
# TODO add handler for printing
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class Error(enum.Enum):
    UNSUPPORTED_PYTHON_VERSION = -1


class LogLevels(enum.Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Diversifier(enum.Enum):
    # TODO what about other diversifiers
    # see: https://www.notinventedhere.org/articles/python/how-to-use-strings-as-name-aliases-in-python-enums.html
    UNDETECTED = enum.auto()
    EMV = enum.auto()
    VISA2 = enum.auto()
    NONE = enum.auto()
    KDF3 = enum.auto()

    @classmethod
    def get_flag(cls, diversifier):
        if diversifier == cls.NONE:
            return ""
        if diversifier == cls.UNDETECTED:
            return ""
        if diversifier == cls.EMV:
            return "--emv"
        if diversifier == cls.VISA2:
            return "--visa2"
        if diversifier == cls.KDF3:
            return "--kdf3"


class GlobalPlatformProWrapper(object):
    def __init__(self, config, dry_run=False, log_verbosity=logging.CRITICAL):
        self.verbose = True
        self.debug = True
        self.config = config
        self.diversifier = Diversifier.UNDETECTED
        # path to the GlobalPlatformPro.jar
        self.gp_path = None
        self.dry_run = dry_run
        self.version = None

        log.setLevel(log_verbosity)

    def gp_prefix(self, add_diversifier=True):
        cmd = [
            "java",
            "-jar",
            self.gp_path,
        ]
        # TODO add the diversifier here, it is probably the safest option
        if add_diversifier:
            cmd += [Diversifier.get_flag(self.diversifier)]
        return cmd

    def process_config(self):
        self.gp_path = self.config["PATHS"]["gp.jar"]
        self.load_diversifier_from_config()

    def load_diversifier_from_config(self):
        try:
            value = self.config["CARD"]["diversifier"]
        except KeyError:
            log.debug("Config does not contain a value for diversifier.")
            # don't set diversifier since we haven't found it in the config
            return

        value = value.strip()
        value = value.upper()
        try:
            diversifier = Diversifier[value]
        except KeyError:
            log.warning(
                "The value '{}' is not recognized as valid diversifier.".format(value)
            )

    def run_gp_command(self, commands):
        cmd = self.gp_prefix()
        # def add_flags(self):
        if self.verbose:
            cmd += ["--verbose"]
        if self.debug:
            cmd += ["--debug"]
        if self.diversifier:
            pass

    def determine_diversifier(self):
        # try to avoid bricking the card in case the diversifier
        # has been already detected!
        if self.diversifier != Diversifier.UNDETECTED:
            log.debug(
                "Card diversifier already detected ({}). Not detecting it again.".format(
                    self.diversifier.name
                )
            )
            return
        # TODO load know ATRs for EMV and VISA2
        # FIXME finish!

        # first try EMV diversifier
        cmd = self.gp_prefix()
        cmd += ["--list", "--emv"]

        proc = subprocess.check_output(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if proc.returncode == 0:
            log.debug("Card diversifier assumed to be EMV.")
            # safe to assume, that the card uses EMV diversifier
            self.diversifier = Diversifier.EMV
            return

    def read_gp_version(self):
        cmd = self.gp_prefix(add_diversifier=False)
        cmd += ["--version"]

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # the version of GlobalPlatformPro used during the analysis has a bug in the CLI
        # more information at: https://github.com/martinpaljak/GlobalPlatformPro/issues/217
        if proc.returncode in [0, 1]:
            self.version = proc.stdout.decode("utf8").split("\n")[0]


if __name__ == "__main__":
    pass
