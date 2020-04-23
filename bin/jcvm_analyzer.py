#!/usr/bin/env python

from jcvmutils.utils import MongoConnection
from jcvmutils.utils import CommandLineApp

from gppw import GlobalPlatformProWrapper
import configparser
import os
import argparse

import subprocess
import platform
import sys
import enum
import logging


# FIXME handle error on gp --list
# [WARN] GPSession - GET STATUS failed for 80F21000024F0000 with 0x6A81 (Function not supported e.g. card Life Cycle State is CARD_LOCKED)
# TODO determine the level of defensive approach? E.g. when guessing emv

# TODO put into separate file config
log = logging.getLogger(__file__)
# TODO add handler for printing
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# FIXME move to enum
LOG_LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
]


# TODO might not work properly for future Python versions
# subprocess .run has changed in 3.7
PY_VERSION_TUPLE = platform.python_version_tuple()
PY_VERSION = platform.python_version()

if int(PY_VERSION[0]) < 3:
    print("Unsupported python version: {}".format(PY_VERSION))
    print("Try using Python 3.6")
    sys.exit(Erorr.UNSUPPORTED_PYTHON_VERSION)


class PreAnalysis(object):
    def __init__(self):
        pass


class AnalysisManager(CommandLineApp):
    def __init__(self):
        self.config = None
        self.config_file = None
        self.gpw = None
        super().__init__()

    def add_options(self):
        super().add_options()
        self.parser.add_argument(
            "-c", "--config-file", default="config.ini", type=self.validate_config,
        )

    def parse_options(self):
        super().parse_options()
        if self.args.config_file is not None:
            self.config_file = self.args.config_file

    def validate_config(self, value):
        if not os.path.exists(value):
            raise argparse.ArgumentParserError(
                "Can't open the configuration file '{}'. "
                "Does it exists or do you have the right permission?".format(value)
            )

    def load_configuration(self):
        config = configparser.ConfigParser(self.config_file)

    def run(self):
        self.gp = GlobalPlatformProWrapper(log_verbosity=self.verbosity)


if __name__ == "__main__":
    app = AnalysisManager()
