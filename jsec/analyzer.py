#!/usr/bin/env python


# TODO add docstrings
# pylint: disable = missing-class-docstring, missing-function-docstring, invalid-name, fixme
# FIXME use isort
import configparser
import os
import argparse

import platform
import sys
import logging
import re

from pathlib import Path


from jsec.settings import DATA
from jsec.gppw import GlobalPlatformProWrapper
from jsec.utils import CommandLineApp
from jsec.utils import cd
from jsec.utils import Error
from jsec.utils import load_versions

# FIXME use flake8 as --dev dependency and remove some pylints
# FIXME handle error on gp --list
# [WARN] GPSession - GET STATUS failed for 80F21000024F0000 with 0x6A81 (Function not supported e.g. card Life Cycle State is CARD_LOCKED)

# TODO determine the level of defensive approach? E.g. when guessing emv

# FIXME think through the hierarchy of the different loggers
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
    sys.exit(Error.UNSUPPORTED_PYTHON_VERSION)


class PreAnalysisManager:
    # make sure, that all the attacks are build
    # and have the scenario.py or whatever to run them
    def __init__(self, card, gp):
        self.gp = gp
        self.card = card

    def run(self):
        # install the JCVersion applet
        # save the version somewhere
        self.get_jc_version()

    def get_jc_version(self):
        # ordered from the newests
        config = configparser.ConfigParser()
        path = DATA / "jcversion/config.ini"
        config.read(path)

        versions = config["BUILD"]["versions"].split(",")
        versions = load_versions(versions)

        for version in versions:
            scenario = ScenarioHandler(config, self.gp, workdir=DATA / "jcversion")
            scenario.execute_stages(version)


# FIXME give disclaimer and ask about consent
class App(CommandLineApp):
    APP_DESCRIPTION = """
    [DISCLAIMER] Running this analysis can potentially dammage (brick/lock) your card!
    By using this tool you acknowledge this fact and use the tool on your on risk.
    This tool is meant to be used for analysis and research on spare JavaCards in order
    to infer something about the level of the security of the JavaCard Virtual Machine
    implementation it is running.
    """

    def __init__(self):
        # FIXME group self.args according to meaning
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
            "-c", "--config-file", default="user-config.ini", type=self.validate_config,
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

        self.parser.add_argument(
            "-n",
            "--dry-run",
            default=False,
            action="store_true",
            help="No external programs are called, useful when developing the analyzer",
        )

    def parse_options(self):
        super().parse_options()
        if self.args.config_file is not None:
            self.config_file = self.args.config_file

        if self.args.dry_run is not None:
            print(
                "[Note] --dry-run was set, no external commands are called "
                "and no report is created"
            )
            self.dry_run = self.args.dry_run

    def validate_config(self, value):
        if not os.path.exists(value):
            raise argparse.ArgumentTypeError(
                "\nError: Can't open the configuration file '{}'. "
                "Does it exists and do you have the permission to read it?".format(
                    value
                )
            )
        return Path(value)

    def load_configuration(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    def run(self):
        self.load_configuration()

        self.gp = GlobalPlatformProWrapper(
            config=self.config, dry_run=self.dry_run, log_verbosity=self.verbosity,
        )
        # FIXME make sure we only have one card in the reader
        self.card = Card()
        prem = PreAnalysisManager(self.card, self.gp)
        prem.run()
        # sel.get_jc_version(self.card)

    # def run_attack(self):
    #     for attack in self.active_attacks:
    #         pass


class PostAnalysisManager:
    pass


# TODO add logging everywhere
class CardState:
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


class Card:
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


# class AppManager():
#     def __init__(self):
#         pass

#     def run(self):
#         card = Card()
#         gp = GlobalPlatformProWrapper()
#         PreAnalysisManager(gp, card)


class ScenarioHandler:
    def __init__(self, config, gp, workdir):
        self.stages = config["STAGES"]
        self.gp = gp
        self.workdir = workdir
        self.installed_version = None

    def execute_stages(self, version):
        self.installed_version = None
        for stage, value in self.stages.items():
            stage = stage.upper()
            if stage == "INSTALL":
                log.info("Attempt to install version: %s", version)
                with cd(self.workdir):
                    self.gp.install(value.format(version=version))
            if stage.startswith("SEND"):
                pass
            if stage == "UNINSTALL":
                if version == self.installed_version:
                    with cd(self.workdir):
                        log.info("Uninstall version: %s", version)
                        self.gp.uninstall(value.format(version=version))
                log.warning(
                    "Attempt to uninstall version '%s', that was not installed.",
                    version,
                )


if __name__ == "__main__":
    app = App()
    app.run()
