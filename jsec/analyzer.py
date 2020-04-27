#!/usr/bin/env python

from jcvmutils.utils import MongoConnection
from jcvmutils.utils import CommandLineApp

from jsec.jsec.gppw import GlobalPlatformProWrapper
import configparser
import os
import argparse

import subprocess
import platform
import sys
import enum
import logging
import re

from jsec.cards.jcversion import config

from pathlib import Path

DATA_PATH = Path(__file__) / "data"


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

# TODO might not work properly for future Python versions
# subprocess .run has changed in 3.7
PY_VERSION_TUPLE = platform.python_version_tuple()
PY_VERSION = platform.python_version()

if int(PY_VERSION[0]) < 3:
    print("Unsupported python version: {}".format(PY_VERSION))
    print("Try using Python 3.6")
    sys.exit(Erorr.UNSUPPORTED_PYTHON_VERSION)


class PreAnalysisManager(object):
    # make sure, that all the attacks are build
    # and have the scenario.py or whatever to run them
    def __init__(sefl, card, gp):
        self.gp = gp
        self.card = card

    def run(self, card):
        # install the JCVersion applet
        # save the version somewhere
        pass

    def get_jc_version(self, card):
        # ordered from the newests
        config = configparser.ConfigParser()
        config.read(DATA_PATH / "jcversion/config")

        card.execute_steps(config["STAGES"])


class AnalysisManager(CommandLineApp):
    APP_DESCRIPTION = """
    [DISCLAIMER] Running this analysis can potentially dammage (brick/lock) your card!
    By using this tool you acknowledge this fact and use the tool on your on risk.
    This tool is meant to be used for analysis and research on spare JavaCards in order
    to infer something about the level of the security of the JavaCard Virtual Machine
    implementation it is running.
    """

    def __init__(self):
        self.config = None
        self.config_file = None
        self.gp = None
        self.card = None
        super().__init__()
        self.setup_logging(log)

    def add_options(self):
        # TODO add option for making copy of the attack CAP files for later investigation
        super().add_options()
        self.parser.add_argument(
            "-c", "--config-file", default="config.ini", type=self.validate_config,
        )
        self.parser.add_argument(
            "-r",
            "--rebuild",
            default=False,
            action="store_true",
            help=(
                "When set, each used applet will be rebuild before installing and "
                "running. If no card is present this effectively rebuilds all attacks."
            ),
        )
        self.parser.add_argument(
            "-l",
            "--long-description",
            default=False,
            action="store_true",
            help="Will display long description of the tool and end.",
        )

    def parse_options(self):
        super().parse_options()
        if self.args.config_file is not None:
            self.config_file = self.args.config_file

    def validate_config(self, value):
        if not os.path.exists(value):
            raise argparse.ArgumentTypeError(
                "Can't open the configuration file '{}'. "
                "Does it exists or do you have the right permission?".format(value)
            )

    def load_configuration(self):
        config = configparser.ConfigParser(self.config_file)

    def run(self):
        self.gp = GlobalPlatformProWrapper(log_verbosity=self.verbosity)
        # TODO make sure we only have one card in the reader
        self.card = Card(gp=self.gp)
        sel.get_jc_version(self.card)

    def run_attack(self):
        for attack in self.active_attacks:
            pass


class PostAnalysisManager(object):
    pass


# TODO add logging everywhere
class CardState(object):
    # basically a parsed output from `gp --list`
    def __init__(self, raw):
        self.raw = raw
        self.isds = []
        self.pkgs = []
        self.applets = []
        self._items = None
        self.parseable = False

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

    def process(self):
        # parse the raw output of `gp --list`
        try:
            self._parse_raw()
            self.parseable = True
        except Exception:
            log.warning("The card state coult not be parsed properly")
            self.parseable = False

        # FIXME the next few lines are ugly, but will do for now
        for item in self._items:
            if list(item.keys()) == ["APP"]:
                self.applets.append(item)
            if list(item.keys()) == ["PKG"]:
                self.pkgs.append(item)
            if list(item.keys()) == ["ISD"]:
                self.isds.append(item)


class Card(object):
    # object representing a card during the analysis
    # basically a card can go from one state to another if a GlobalPlatformCall is performed on it. E.g. listing, installing etc.
    # Being defensies and cautious we can, hopefully log each weird behaviour
    # TODO
    # install an applet
    # execute applet/attack steps
    def __init__(self):
        self.states = None
        self.jcversion = None

    def update(self, state):
        if self.states is None:
            self.states = [state]
        else:
            self.states.append(state)


class AppManager(object):
    def __init__(self):
        pass

    def run(self):
        card = Card()

        PreAnalysisManager(gp, card)


if __name__ == "__main__":
    app = AnalysisManager()
