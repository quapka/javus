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

# TODO consider importing only toplevel module
import smartcard
from smartcard.ATR import ATR
from smartcard.CardConnection import CardConnection
from smartcard.CardConnectionDecorator import CardConnectionDecorator
from smartcard.System import readers

from jsec.builder import BaseBuilder
from jsec.card import Card
from jsec.data.jcversion.jcversion import JCVersionExecutor
from jsec.executor import AbstractAttackExecutor, BaseAttackExecutor
from jsec.gppw import GlobalPlatformProWrapper
from jsec.settings import ATTACKS, DATA
from jsec.utils import (
    CommandLineApp,
    Error,
    JCVersion,
    MongoConnection,
    SDKVersion,
    cd,
    load_versions,
    get_user_consent,
)
from jsec.viewer import app


# FIXME handle error on gp --list
# flake8: noqa [WARN] GPSession - GET STATUS failed for 80F21000024F0000 with 0x6A81 (Function not supported e.g. card Life Cycle State is CARD_LOCKED)

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


def detect_cards() -> List[CardConnectionDecorator]:
    """
    Detect all the JavaCards, that are currently inserted
    in the readers.
    """
    cards = []
    for reader in readers():
        con = reader.createConnection()
        try:
            con.connect()
            cards.append(con)
        except (
            smartcard.Exceptions.NoCardException,
            smartcard.Exceptions.CardConnectionException,
        ):
            pass

    return cards


class PreAnalysisManager:
    # TODO handle pcscd not running exception smartcard.pcsc.PCSCExceptions.EstablishContextException
    def __init__(self, card: "Card", gp: "GlobalPlatformProWrapper"):
        self.card = card
        self.gp = gp

    def single_card_inserted(self) -> bool:
        r"""We need to ensure, that one and only one card is inserted in all of the readers
        when doing the analysis.
        """
        self.cards = detect_cards()
        single_card = True
        number_of_cards = len(self.cards)
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
            sys.exit(1)
        else:
            # now we know, that there is exactly one card connected and we can record its' ATR
            self.card.atr = ATR(self.cards[0].getATR())
            self.card.reader = self.cards[0].getReader()
        builder = BaseBuilder(gp=self.gp, workdir=DATA / "jcversion")
        builder.execute(BaseBuilder.COMMANDS.build)
        used_aids = self.card.get_current_aids()
        if not builder.uniq_aids(used_aids):
            builder.uniqfy(used_aids)
            builder.execute(BaseBuilder.COMMANDS.build)
        print("WARNING: Manually setting JCVersion for Card A!!!")
        self.card.jcversion = JCVersion.from_str("0300")
        # FIXME don't hardcode it for a card!  put JCVersion into a used-config.ini
        # FIXME getting the jc version still seems to cause troubles
        # self.card.jcversion = self.get_jc_version()
        self.card.sdks = self.card.jcversion.get_sdks()
        report["JCVersion"] = self.card.jcversion
        report["SDKs"] = self.card.sdks

        return report

    def get_jc_version(self):
        version = JCVersionExecutor(
            card=self.card, gp=self.gp, workdir=DATA / "jcversion", sdk=None
        ).get_jcversion()
        return version


class App(CommandLineApp):
    APP_DESCRIPTION = """
[DISCLAIMER] Running the analysis can potentially dammage (brick/lock) your card!
By using this tool you acknowledge this fact and use the tool at your on risk.
This tool is meant to be used for analysis and research on spare JavaCards in order
to infer something about the level of the security of the JavaCard Virtual Machine
implementation it is running.
    """.strip()

    def __init__(self):
        # FIXME sort self arguments and parameters
        self.config = None
        self.config_file = None
        self.gp: Optional[GlobalPlatformProWrapper] = None
        self.card: Optional[Card] = None
        self.list = False
        super().__init__()
        self.setup_logging(log)
        self._system = platform.system()

    def add_subparsers(self):
        self.subparsers = self.parser.add_subparsers(
            title="Available commands",
            description=(
                "Here follows the list of sub-commands, that you can execute. "
                "Use: %s <sub-command> -h/--help "
                "to get help about the subcommands"
            ),
            dest="sub_command",
        )
        self.subparsers.required = True
        self.add_web_parser()
        self.add_run_parser()
        self.add_list_parser()

    def add_web_parser(self):

        web_parser = self.subparsers.add_parser(
            "web", help="Start a local webserver to view the analysis results"
        )
        web_parser.add_argument("--host", type=str, default="localhost")
        web_parser.add_argument("--port", type=int, default="5000")

    def add_list_parser(self):
        list_parser = self.subparsers.add_parser(
            "list", help="List all the registered attacks."
        )

    def add_run_parser(self):
        run_parser = self.subparsers.add_parser(
            "run",
            help="Execute the attacks on a real JavaCard. ",
            description=self.APP_DESCRIPTION,
        )
        run_parser.add_argument(
            "-c", "--config-file", type=self.validate_config,
        )
        run_parser.add_argument(
            "-n",
            "--dry-run",
            default=False,
            action="store_true",
            help="No external programs are called, useful when developing the analyzer",
        )
        run_parser.add_argument(
            "-o",
            "--output-dir",
            default=Path("jsec-analysis-result"),
            help="A directory, that will store the results of the analysis",
        )

        run_parser.add_argument(
            "-m",
            "--message",
            type=str,
            default="",
            help="A message/comment, that will be saved together with this analysis run.",
        )
        run_parser.add_argument(
            "-w", "--web", action="store_true", help="Start the web application"
        )
        # FIXME localhost won't work in Docker!
        run_parser.add_argument(
            "--web-host",
            type=str,
            default="localhost",
            help="Hostname for the web application",
        )
        run_parser.add_argument(
            "--web-port", type=str, default="5000", help="Port for the web application",
        )
        run_parser.add_argument(
            "-r",
            "--riskit",
            help=(
                "By setting this flag the user of the tool agrees to use "
                "this tool at his/her own risk and he/she understands the risks "
                "mentioned in the [DISCLAIMER]."
            ),
            action="store_true",
        )

        # TODO implement execution of a single attack
        run_parser.add_argument(
            "--attack",
            type=self.validate_attack_name,
            help="execute only this particular attack",
        )

        # TODO add -t/--tag for tagging analysis runs?
        # TODO def add options attempting to uninstall all applets, that were installed
        # TODO add argument to dump to json file intead of MongoDB

    def validate_attack_name(self, value):
        raise NotImplementedError(
            "Execution of a single attack is not implemented at the moment."
        )
        registry = self.load_attacks()
        valid = True

        attack_names = []
        for section in registry.sections():
            for key in registry[section]:
                if key != "module":
                    attack_names.append(key)

        if value not in attack_names:
            valid = False

        if not valid:
            raise argparse.ArgumentTypeError(
                "The attack '%s' is not registered. The list of registered attacks is: %s."
                % (value, ", ".join(attack_names))
            )
        return value

    @property
    def web_subcommand(self):
        return self.args.sub_command == "web"

    @property
    def run_subcommand(self):
        return self.args.sub_command == "run"

    @property
    def list_subcommand(self):
        return self.args.sub_command == "list"

    def parse_options(self):
        super().parse_options()
        if self.web_subcommand:
            self.web_host = self.args.host
            self.web_port = self.args.port

        elif self.run_subcommand:
            if self.args.config_file is not None:
                self.config_file = self.args.config_file

            self.dry_run = self.args.dry_run
            if self.dry_run:
                print(
                    "[Note] '--dry-run' was set, no external commands are called "
                    "and no report is created."
                )
            self.message = self.args.message
            # options for the web application
            self.start_web = self.args.web
            self.web_host = self.args.web_host
            self.web_port = self.args.web_port
            self.attack_name = self.args.attack
            self.riskit = self.args.riskit

    def validate_config(self, value: str) -> Path:
        if not os.path.exists(value):
            raise argparse.ArgumentTypeError(
                "\nError: Can't open the configuration file '{}'. "
                "Does it exists and do you have the permission to read it?".format(
                    value
                )
            )
        return Path(value)

    def in_docker(self):
        r"""Based on answer from: https://stackoverflow.com/a/20012536
        """
        docker = False
        # TODO technically we won't ever be inside Windows container, therefore
        # we only need to check for "Linux" systems
        if self._system == "Linux":
            with open("/proc/1/cgroup", "r") as f:
                for line in f.readlines():
                    if "docker" in line:
                        docker = True
        return docker

    # TODO unify load_configuration and load_config
    def load_configuration(self):
        self.config = configparser.ConfigParser()
        if self.config_file:
            self.config.read(self.config_file)
        else:
            pass

    def load_db_configuration(self):
        try:
            self.database = self.config["DATABASE"]["name"]
        except KeyError:
            self.database = "javacard-analysis"

        try:
            self.db_host = self.config["DATABASE"]["host"]
        except KeyError:
            self.db_host = "localhost"

        try:
            self.db_port = self.config["DATABASE"]["port"]
        except KeyError:
            self.db_port = "27017"

    def add_attack_to_db(self, attack_name, attack_results):
        """
        Adds the attack results to the database
        """
        key = "analysis-results.%s" % attack_name
        value = attack_results
        with MongoConnection(
            database=self.database, host=self.db_host, port=self.db_port
        ) as con:
            con.col.update_one({"_id": self.report_id}, {"$set": {key: value}})

    def prepare(self):
        self.load_configuration()
        self.load_db_configuration()

        self.gp = GlobalPlatformProWrapper(
            config=self.config, dry_run=self.dry_run, log_verbosity=self.verbosity,
        )
        self.card = Card(gp=self.gp)
        self.gp.card = self.card

    def load_attacks(self) -> configparser.ConfigParser:
        registry = configparser.ConfigParser()
        registry_file = Path(DATA / "registry.ini")
        if not registry_file.exists():
            log.error("Missing registry file '%s'", registry_file)
            # TODO how to handle clean exit?
        # FIXME does not fail on missing file, check it before
        registry.read(registry_file)
        return registry

    def print_attack_list(self):
        # TODO print also the section names?
        registry = self.load_attacks()
        print("List of registered attacks.")
        enabled = []
        disabled = []
        for section in registry.sections():
            for attack, value in registry[section].items():
                if attack == "module":
                    continue
                if registry.getboolean(section, attack):
                    enabled.append(attack)
                else:
                    disabled.append(attack)
        # TODO nicer way of printig?
        print("enabled:\n    ", end="")
        print("\n    ".join(enabled))
        print("\ndisabled:\n    ", end="")
        print("\n    ".join(disabled))

    def start_webserver(self):
        app.run(host=self.web_host, port=self.web_port)

    def handle_user_consent(self):
        if not self.riskit:
            if not get_user_consent(
                self.APP_DESCRIPTION,
                "Do you agree, that you continue at your own risk?",
            ):
                print(
                    "For future runs you can agree with the disclaimer by using "
                    "the '--riskit' flag."
                )
                print("No attacks were executed.")
                sys.exit(0)

    def run(self):
        # FIXME --dry-run
        if self.web_subcommand:
            self.start_webserver()

        elif self.run_subcommand:
            self.handle_user_consent()

            start_time = time.time()
            self.prepare()

            print("Running the pre-analysis..")
            prem = PreAnalysisManager(self.card, self.gp)
            prem_results = prem.run()

            start_report = {
                "start-time": start_time,
                # set end-time and duration, so that the analysis can be viewed mid run
                "end-time": "",
                "duration": "",
                "message": self.message,
                "card": self.card.get_report(),
                "pre-analysis-results": prem_results,
            }
            with MongoConnection(
                database=self.database, host=self.db_host, port=self.db_port
            ) as con:
                self.report_id = con.col.insert_one(start_report).inserted_id

            print("Running the analysis..")
            anam = AnalysisManager(
                self.card, self.gp, self.config, update_attack=self.add_attack_to_db
            )
            anam_results = anam.run()

            print("Running the post-analysis..")
            end_time = time.time()

            end_report = {
                "end-time": end_time,
                "duration": end_time - start_time,
            }
            with MongoConnection(
                database=self.database, host=self.db_host, port=self.db_port
            ) as con:
                con.col.update_one({"_id": self.report_id}, {"$set": end_report})

            # self.save_record()
            if self.start_web:
                self.start_webserver()

        elif self.list_subcommand:
            self.print_attack_list()


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
        # TODO attempt to --delete all the applets, that have not been
        # uninstalled during the analysis. This is quite cruel - some
        # dependence might prevent that, but better than nothing I suppose


class AnalysisManager:
    def __init__(
        self,
        card: Card,
        gp: GlobalPlatformProWrapper,
        config: configparser.ConfigParser,
        update_attack,
    ):
        self.card = card
        self.gp = gp
        self.config = config
        self.attacks: Optional[configparser.ConfigParser] = None
        self.updater = update_attack

    def load_attacks(self) -> configparser.ConfigParser:
        registry = configparser.ConfigParser()
        registry_file = Path(DATA / "registry.ini")
        if not registry_file.exists():
            log.error("Missing registry file '%s'", registry_file)
            # TODO how to handle clean exit?
        # FIXME does not fail on missing file, check it before
        registry.read(registry_file)
        return registry

    # TODO implement execution of a single attack
    # def execute_attack(
    #     self, attack, module, version,
    # ):
    #     AttackExecutor = self.get_executor(attack_name=attack, module=module)
    #     executor = AttackExecutor(card=self.card, gp=self.gp, workdir=ATTACKS / attack)
    #     if self.attacks.getboolean(section, attack):
    #         for version in executor.sdks:
    #             print("%s (SDK: %s)" % (attack, version.raw))
    #             AttackBuilder = self.get_builder(attack_name=attack, module=module)
    #             builder = AttackBuilder(
    #                 gp=self.gp, workdir=ATTACKS / attack, version=version
    #             )
    #             # FIXME when to build the attacks?
    #             builder.execute(BaseBuilder.COMMANDS.build)
    #             if not builder.uniq_aids(self.card.get_current_aids()):
    #                 builder.uniqfy(used=self.card.get_current_aids())
    #                 # rebuild the applet
    #                 # TODO or call build directly? much nicer..
    #                 builder.execute(BaseBuilder.COMMANDS.build)
    #             self.report[attack + "-" + version.raw] = {
    #                 "results": executor.execute(sdk_version=version),
    #                 "sdk_version": version.raw,
    #             }
    #     else:
    #         print("%s: skip" % attack)
    #         # report[attack]["sdk-version"] = version

    def run(self):
        self.attacks = self.load_attacks()
        report = {}
        for section in self.attacks.sections():
            print("Executing attacks from %s" % section)
            log.info("Executing attacks from '%s'", section)

            module = self.attacks[section]["module"]
            for attack, value in self.attacks[section].items():
                # TODO this is ugly and not easy to extend in the future, maybe ditch the
                # idea of ini files and get json? - that is not possible as long as the config
                # is share with ant
                if attack == "module":
                    continue
                AttackExecutor = self.get_executor(attack_name=attack, module=module)
                executor = AttackExecutor(
                    card=self.card, gp=self.gp, workdir=ATTACKS / attack
                )
                if self.attacks.getboolean(section, attack):
                    for version in executor.sdks:
                        print("%s (SDK: %s)" % (attack, version.raw))
                        AttackBuilder = self.get_builder(
                            attack_name=attack, module=module
                        )
                        builder = AttackBuilder(
                            gp=self.gp, workdir=ATTACKS / attack, version=version
                        )
                        # FIXME when to build the attacks?
                        builder.execute(BaseBuilder.COMMANDS.build)
                        if not builder.uniq_aids(self.card.get_current_aids()):
                            builder.uniqfy(used=self.card.get_current_aids())
                            # rebuild the applet
                            # TODO or call build directly? much nicer..
                            builder.execute(BaseBuilder.COMMANDS.build)
                        result = executor.execute(sdk_version=version)
                        key_name = attack + "-" + version.raw
                        x = {
                            "results": result,
                            "sdk_version": version.raw,
                        }
                        # save the result of this attack into the database immediately
                        self.update_report(key_name, report=x)
                        # the attack can lock/block, continueing attacks makes no sense
                        if self.card_not_working(result=result):
                            print(
                                "It seems, that the card stopped working during the execution of"
                                "the attack %s\nYou can try replugging the card/reader (and "
                                "wait a few minutes, before the card starts working again) and "
                                "start the analysis again or maybe skip this attack."
                                % attack
                            )
                            sys.exit(0)
                else:
                    print("%s: skip" % attack)
        return report

    def update_report(self, attack_name, report):
        """
        """
        self.updater(attack_name, report)

    def card_not_working(self, result):
        """
        """
        for stage in result:
            try:
                out = stage["stdout"]
            except KeyError:
                out = ""

            try:
                err = stage["stderr"]
            except KeyError:
                err = ""

            error_constansts = ["SCARD_E_NOT_TRANSACTED", "SCARD_W_UNPOWERED_CARD"]
            works = True
            for err_const in error_constansts:
                if err_const in out or err_const in err:
                    works = False
                    if not works:
                        break

            if not works:
                cards = detect_cards()
                if not cards:
                    return True
                # TODO it is of question, whether to return True on else or not
                # but for now we won't do it

        return False

    # FIXME finish loading the builder
    def get_builder(self, attack_name: str, module: str):
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
                importlib.import_module(f"jsec.data.attacks.{module}"), "AttackBuilder",
            )
            return builder
        except AttributeError:
            pass
        except ModuleNotFoundError:
            # FIXME handle this
            pass

        return BaseBuilder

    def get_executor(self, attack_name: str, module: str) -> AbstractAttackExecutor:
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
                importlib.import_module(f"jsec.data.attacks.{module}"),
                "AttackExecutor",
            )
            # TODO maybe add ModuleNotFoundError, but if it is in config.ini it is actually an
            # error - either missing module or should not be in config
            return executor
        except (ModuleNotFoundError, AttributeError):
            pass

        # then fallback to the type of the attack executor
        # finally base executor, that can (un)install and send APDUs
        return BaseAttackExecutor


if __name__ == "__main__":
    app = App()
    app.run()
