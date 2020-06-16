#!/usr/bin/env python


import argparse

# TODO add docstrings
# pylint: disable = missing-class-docstring, missing-function-docstring, invalid-name, fixme
# FIXME use isort
import configparser
import importlib
import logging
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import List, Optional

import smartcard
from smartcard.CardConnection import CardConnection
from smartcard.CardConnectionDecorator import CardConnectionDecorator
from smartcard.System import readers

from jsec.builder import BaseBuilder
from jsec.card import Card
from jsec.data.jcversion.jcversion import JCVersionExecutor
from jsec.executor import AbstractAttackExecutor, BaseAttackExecutor
from jsec.gppw import GlobalPlatformProWrapper
from jsec.settings import ATTACKS, DATA
from jsec.utils import CommandLineApp, Error, JCVersion, cd, load_versions
from jsec.utils import MongoConnection

# from jsec.data.jcversion import

# FIXME use flake8 as --dev dependency and remove some pylints
# FIXME handle error on gp --list
# flake8: noqa [WARN] GPSession - GET STATUS failed for 80F21000024F0000 with 0x6A81 (Function not supported e.g. card Life Cycle State is CARD_LOCKED)

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
    def __init__(self, card: "Card", gp: "GlobalPlatformProWrapper"):
        self.card = card
        self.gp = gp

    def detect_cards(self,) -> List[CardConnectionDecorator]:
        r"""Detect all the JavaCards, that are currently inserted
        in the readers.
        """
        cards = []
        for reader in readers():
            con = reader.createConnection()
            try:
                con.connect()
                cards.append(con)
            except smartcard.Exceptions.NoCardException:
                pass

        return cards

    def single_card_inserted(self) -> bool:
        r"""We need to ensure, that one and only one card is inserted in all of the readers
        when doing the analysis.
        """
        cards = self.detect_cards()
        single_card = True
        number_of_cards = len(cards)
        if number_of_cards < 1:
            log.error("No JavaCards have been detected.")
            print("No JavaCards have been detected, please, insert one.")
            single_card = False

        if number_of_cards > 1:
            log.error("Too many cards ('%s') have been detected", number_of_cards)
            print(
                "Detected %s cards, that is too many, insert only single card."
                % number_of_cards
            )
            single_card = False

        return single_card

    def run(self):
        report = {}
        if not self.single_card_inserted():
            # TODO is it worth having custom errors?
            sys.exit(1)
        # FIXME don't hardcode it for a card!
        # put JCVersion into a types.ini
        # print("WARNING: Manually setting JCVersion for Card A!!!")
        # self.card.jcversion = JCVersion.from_str("0300")
        builder = BaseBuilder(gp=self.gp, workdir=DATA / "jcversion")
        builder.execute(BaseBuilder.COMMANDS.build)
        used_aids = self.card.get_current_aids()
        if not builder.uniq_aids(used_aids):
            builder.uniqfy(used_aids)
            builder.execute(BaseBuilder.COMMANDS.build)
        self.card.jcversion = self.get_jc_version()
        self.card.sdks = self.card.jcversion.get_sdks()
        report["JCVersion"] = self.card.jcversion
        report["SDKs"] = self.card.sdks

        return report

    def get_jc_version(self):
        version = JCVersionExecutor(
            card=self.card, gp=self.gp, workdir=DATA / "jcversion", sdk=None
        ).get_jcversion()
        return version


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
        # FIXME sort self arguments and parameters
        self.config = None
        self.config_file = None
        self.gp: Optional[GlobalPlatformProWrapper] = None
        self.card: Optional[Card] = None
        self.report: dict = {}
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
        # TODO test if argparse defaults are validated
        self.parser.add_argument(
            "-o",
            "--output-dir",
            default=Path("jsec-analysis-result"),
            help="A directory, that will store the results of the analysis",
        )

        self.parser.add_argument(
            "-m",
            "--message",
            type=str,
            default="",
            help="A message/comment, that will be saved together with this analysis run.",
        )
        self.parser.add_argument(
            "-j",
            "--json",
            type=self.validate_json_flag,
            default=Path("javacard-analysis.json"),
            help="Save the results as JSON into the specified file.",
        )
        # FIXME probably go with subcommands
        self.parser.add_argument(
            "-w", "--web", action="store_true", help="Start the web application"
        )
        # TODO add -t/--tag for tagging analysis runs?
        # TODO def add options attempting to uninstall all applets, that were installed
        # TODO add argument to dump to json file intead of MongoDB
        # but this should be the implicit behaviour

    def validate_json_flag(self, value):
        # FIXME finish
        return value

    def parse_options(self):
        super().parse_options()
        if self.args.config_file is not None:
            self.config_file = self.args.config_file

        self.dry_run = self.args.dry_run
        if self.dry_run:
            print(
                "[Note] '--dry-run' was set, no external commands are called "
                "and no report is created."
            )
        self.message = self.args.message
        self.json = self.args.json

    def validate_config(self, value: str) -> Path:
        if not os.path.exists(value):
            raise argparse.ArgumentTypeError(
                "\nError: Can't open the configuration file '{}'. "
                "Does it exists and do you have the permission to read it?".format(
                    value
                )
            )
        return Path(value)

    # TODO unify load_configuration and load_config
    def load_configuration(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    def save_record(self) -> None:
        if self.dry_run:
            return
        database = self.config["DATABASE"]["name"]
        host = self.config["DATABASE"]["host"]
        port = self.config["DATABASE"]["port"]

        with MongoConnection(database=database, host=host, port=port) as con:
            con.col.insert_one(self.report)

    def prepare(self):
        self.load_configuration()

        self.gp = GlobalPlatformProWrapper(
            config=self.config, dry_run=self.dry_run, log_verbosity=self.verbosity,
        )
        self.card = Card(gp=self.gp)
        self.gp.card = self.card

    def run(self):
        start_time = time.time()
        self.prepare()

        print("Running the pre-analysis..")
        prem = PreAnalysisManager(self.card, self.gp)
        prem_results = prem.run()

        print("Running the analysis..")
        anam = AnalysisManager(self.card, self.gp, self.config)
        anam_results = anam.run()

        print("Running the post-analysis..")
        end_time = time.time()

        self.report.update(
            {
                "start-time": start_time,
                "end-time": end_time,
                "duration": end_time - start_time,
                "message": self.message,
                "pre-analysis-results": prem_results,
                "analysis-results": anam_results,
            }
        )
        self.save_record()


class PostAnalysisManager:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def create_output_dir(self) -> Path:
        suffix = 0
        while True:
            if suffix:
                self.output_dir += "-{}".format(suffix)
            try:
                os.mkdir(self.output_dir)
            except FileExistsError:
                log.debug(
                    "The directory '%s' already exists. Updating and adding a suffix",
                    self.output_dir,
                )
                suffix += 1

        return self.output_dir

    def run(self):
        self.create_output_dir()


class AnalysisManager:
    def __init__(
        self,
        card: Card,
        gp: GlobalPlatformProWrapper,
        config: configparser.ConfigParser,
    ):
        self.card = card
        self.gp = gp
        self.config = config
        self.attacks: Optional[configparser.ConfigParser] = None

    def load_attacks(self) -> configparser.ConfigParser:
        registry = configparser.ConfigParser()
        registry_file = Path(DATA / "registry.ini")
        if not registry_file.exists():
            log.error("Missing registry file '%s'", registry_file)
            # TODO how to handle clean exit?
        # FIXME does not fail on missing file, check it before
        registry.read(registry_file)
        return registry

    def run(self):
        self.attacks = self.load_attacks()
        report = {}
        for section in self.attacks.sections():
            log.info("Executing attacks from '%s'", section)
            builder_module = self.attacks[section]["builder"]
            for attack, value in self.attacks[section].items():
                # TODO this is ugly and not easy to extend in the future, maybe ditch the
                # idea of ini files and get json?
                if attack == "builder":
                    continue
                if self.attacks.getboolean(section, attack):
                    AttackBuilder = self.get_builder(
                        attack_name=attack, builder_module=builder_module
                    )
                    builder = AttackBuilder(gp=self.gp, workdir=ATTACKS / attack)
                    # FIXME when to build the attacks?
                    builder.execute(BaseBuilder.COMMANDS.build)
                    if not builder.uniq_aids(self.card.get_current_aids()):
                        builder.uniqfy(used=self.card.get_current_aids())
                        # rebuild the applet
                        # TODO or call build directly? much nicer..
                        builder.execute(BaseBuilder.COMMANDS.build)
                    AttackExecutor = self.get_executor(
                        attack_name=attack, builder_module=builder_module
                    )
                    executor = AttackExecutor(
                        card=self.card, gp=self.gp, workdir=ATTACKS / attack
                    )
                    report[attack] = executor.execute()
        return report

    # FIXME finish loading the builder
    def get_builder(self, attack_name: str, builder_module: str):
        try:
            builder = getattr(
                importlib.import_module(
                    f"jsec.data.attacks.{attack_name}.{attack_name}"
                ),
                "AttackBuilder",
            )
            return builder
        except (ModuleNotFoundError, AttributeError):
            pass

        try:
            builder = getattr(
                importlib.import_module(f"jsec.data.attacks.{builder_module}"),
                "AttackBuilder",
            )
            return builder
        except AttributeError:
            pass
        except ModuleNotFoundError:
            # FIXME handle this
            pass

        return BaseBuilder

    def get_executor(
        self, attack_name: str, builder_module: str
    ) -> AbstractAttackExecutor:
        # first load the executor from the directory of the attack
        try:
            executor = getattr(
                importlib.import_module(
                    # TODO this way we cannot test this method, since the load path is
                    # hardcoded
                    f"jsec.data.attacks.{attack_name}.{attack_name}"
                ),
                "AttackExecutor",
            )
            return executor
        except (ModuleNotFoundError, AttributeError):
            pass

        try:
            executor = getattr(
                importlib.import_module(f"jsec.data.attacks.{builder_module}"),
                "AttackExecutor",
            )
            # TODO maybe add ModuleNotFoundError, but if it is in config.ini it is actually an
            # error - either missing module or should not be in config
            return executor
        except AttributeError:
            pass

        # then fallback to the type of the attack executor
        # finally base executor, that can (un)install and send APDUs
        return BaseAttackExecutor


if __name__ == "__main__":
    app = App()
    app.run()
