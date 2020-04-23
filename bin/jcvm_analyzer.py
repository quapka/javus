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
import re


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




class CardState(object):
    # basically a parsed output from `gp --list`
    def __init__(self, raw):
        self.raw = raw
        self.pkgs = None
        self.applets = None
        self._items = None

    def _parse_raw(self):
        if self._items is not None:
            # cannot parse again!
            return
        self._items = []

        # fmt: off
        tag = re.compile(
            r"(?P<type>ISD|APP|PKG):\s*"
            r"(?P<aid>[A-Z0-9]+)\s*"
            r"\((?P<state>\w+)\)"
        )
        prop = re.compile(
            r"(?P<name>Privs|Version|Applet):\s*"
            r"(?P<value>.*)"
        )
        # fmt: on

        item = {}
        flag = False
        for line in self.raw.strip().split("\n"):
            line = line.strip()

            if not line:
                continue

            tag_match = tag.match(line)
            if tag_match is not None:
                _type = tag_match.group("type")
                aid = tag_match.group("aid")
                state = tag_match.group("state")

                if flag:
                    item = {}
                item[_type] = {
                    "AID": aid,
                    "STATE": state,
                    "ITEMS": {"Privs": [], "Version": [], "Applet": [],},
                }
                self._items.append(item)
                flag = not flag
                continue

            prop_match = prop.match(line)
            if prop_match is not None:
                name = prop_match.group("name")
                value = prop_match.group("value")
                if name == "Privs":
                    # if prop_match.group("value"):
                    values = [x.strip() for x in value.split(",")]
                    item[_type]["ITEMS"][name].extend(values)
                else:
                    item[_type]["ITEMS"][name].append(value)


if __name__ == "__main__":
    app = AnalysisManager()
