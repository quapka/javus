#!/usr/bin/env python

import abc
import argparse
import configparser
import importlib
import enum
import logging
import os
import subprocess
from pathlib import Path

# sort imports
from javus.utils import CommandLineApp, cd, AttackConfigParser

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class AbstractAttackBuilder(abc.ABC):
    @abc.abstractmethod
    def uniqfy(self):
        # TODO maybe have default aids in config.ini and rewrite only aids.ini
        pass


# FIXME add tests
class CommandLineBuilder(CommandLineApp):
    def __init__(self):
        self.workdir = None
        self.version = None
        self.cmd = None

        super().__init__()

    def add_options(self):
        super().add_options()
        # TODO improve help
        # FIXME validate the path
        self.parser.add_argument(
            "cmd", type=self.validate_cmd,
        )

        self.parser.add_argument(
            "--working-dir",
            help="The working directory to use for building",
            default=Path(".").resolve(),
            type=Path,
        )

        self.parser.add_argument(
            "--temp-dir",
            help="The temporary directory to copy the attack files to",
            type=Path,
        )
        # TODO validate default and passed value
        self.parser.add_argument(
            "--version", default="jc211",
        )

    def parse_options(self):
        super().parse_options()
        if self.args.working_dir is not None:
            self.workdir = self.args.working_dir

        if self.args.version is not None:
            self.version = self.args.version

        self.cmd = self.args.cmd

    def validate_cmd(self, value):
        value = value.lower()

        try:
            value = BaseAttackBuilder.COMMANDS[value]
        except KeyError:
            raise argparse.ArgumentTypeError(
                "Unknown command '{cmd}'".format(cmd=value)
            )

        return value

    def run(self):
        builder = BaseAttackBuilder(
            workdir=self.workdir, dry_run=False, version=self.version
        )
        builder.execute(self.cmd)


class BaseAttackBuilder(AbstractAttackBuilder):
    class COMMANDS(enum.Enum):
        clean = enum.auto()
        boostrap = enum.auto()
        build = enum.auto()

    def __init__(self, gp, workdir, dry_run=False, version=None, tempdir=None):
        self.workdir = Path(workdir).resolve()
        self.dry_run = dry_run
        self.version = version
        self.tempdir = tempdir
        self.gp = gp

        self.config = None
        self.supported_versions = None
        self.unsupported_versions = None
        self.cmd = None

        self.ready = False

        self.aids = configparser.ConfigParser()
        self.aids.add_section("BUILD")

    def _prepare(self):
        self._load_config()
        self._set_versions()
        self.load_aids()

        if self.version is not None and self.version not in self.supported_versions:
            log.warning("Unsupported version '%s' set.", self.version.raw)

        self._validate_workdir()

        self.ready = True

    def _load_config(self):
        config = AttackConfigParser(strict=False)
        with cd(self.workdir):
            config.read("config.ini")

        self.config = config

    def _set_versions(self):
        self.supported_versions = self.config.get_sdk_versions("BUILD", "versions")
        self.unsupported_versions = self.config.get_sdk_versions(
            "BUILD", "unsupported.versions"
        )

    @staticmethod
    def _parse_versions(raw):
        return [x.strip() for x in raw.split(",")]

    def _ant(self, options=None):
        # TODO add logging
        # env_copy = os.environ.copy()
        cmd = ["ant"]
        if options is not None:
            cmd.extend(options)

        with cd(self.workdir):
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)

        try:
            proc.check_returncode()
            # TODO should not print in case this is not called as
            # command line application
            log.info("The command '%s' was successful.", self.cmd.name)
        except subprocess.CalledProcessError:
            log.error("Command ended with non-zero error")

        return proc

    def _validate_workdir(self):
        # TODO add to call pipeline
        with cd(self.workdir):
            if not os.path.exists("build.xml"):
                log.error(
                    "Cannot find 'build.xml'. Have you set working directory correctly?"
                )

    def _clean(self):
        if self.version is None:
            options = ["clean-all-versions"]
        else:
            # TODO setting value for -Dversion= is problematic when used with quotes
            options = [
                "clean-version",
                "-Dversion={version}".format(version=self.version),
            ]

        return self._ant(options=options)

    def _build(self):
        if self.version is None:
            options = ["build-all-versions"]
        else:
            options = [
                "build-version",
                "-Dversion={version}".format(version=self.version),
            ]

        return self._ant(options=options)

    def execute_attack(self, detailed=False):
        pass

    def set_default_aids(self):
        self.aids["BUILD"]["pkg.rid"] = "0011223344"
        self.aids["BUILD"]["applet.pix"] = "AABB"

    def load_aids(self):
        with cd(self.workdir):
            read = self.aids.read("aids.ini")

        if not read:
            self.set_default_aids()
            self.save_aids()

    def save_aids(self):
        with cd(self.workdir):
            with open("aids.ini", "w") as aids_file:
                self.aids.write(aids_file)

    def uniqfy(self, used: list = None):
        if used is None:
            used = []

        if not self.ready:
            self._prepare()

        while not self.uniq_aids(used):
            rid = self.aids["BUILD"]["pkg.rid"]
            self.aids["BUILD"]["pkg.rid"] = (int(rid, 16) + 1).to_bytes(5, "big").hex()

        self.save_aids()

    def uniq_aids(self, used):
        if not self.ready:
            self._prepare()

        pkg_rid = self.aids["BUILD"]["pkg.rid"]
        applet_pix = self.aids["BUILD"]["applet.pix"]

        aids = [pkg_rid + applet_pix]

        return set(aids).intersection(set(used)) == set()

    def execute(self, cmd):
        if not self.ready:
            self._prepare()

        self.cmd = cmd
        if cmd == self.COMMANDS.clean:
            result = self._clean()
        elif cmd == self.COMMANDS.boostrap:
            raise NotImplementedError
        elif cmd == self.COMMANDS.build:
            result = self._build()
        else:
            log.error("Attempt to execute unrecognized command '%s'", cmd)

        return result


# FIXME finish loading the builder
def get_builder(attack_name: str, module: str):
    # TODO add logging
    try:
        builder = getattr(
            importlib.import_module(f"javus.data.attacks.{attack_name}.{attack_name}"),
            "AttackBuilder",
        )
        return builder
    except (ModuleNotFoundError, AttributeError):
        pass

    try:
        builder = getattr(
            importlib.import_module(f"javus.data.attacks.{module}"), "AttackBuilder",
        )
        return builder
    except AttributeError:
        pass
    except ModuleNotFoundError:
        # FIXME handle this
        pass

    return BaseAttackBuilder


if __name__ == "__main__":
    pass
