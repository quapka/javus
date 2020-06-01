#!/usr/bin/env python

import argparse
import configparser
import enum
import logging
import os
import subprocess
from pathlib import Path

from jsec.attack import Attack

# sort imports
from jsec.utils import CommandLineApp, cd

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


# FIXME add tests
class CommandLineBuilder(CommandLineApp):
    def __init__(self):
        self.wd = None
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
            self.wd = self.args.working_dir

        if self.args.version is not None:
            self.version = self.args.version

        self.cmd = self.args.cmd

    def validate_cmd(self, value):
        value = value.lower()

        try:
            value = BaseBuilder.COMMANDS[value]
        except KeyError:
            raise argparse.ArgumentTypeError(
                "Unknown command '{cmd}'".format(cmd=value)
            )

        return value

    def run(self):
        builder = BaseBuilder(workdir=self.wd, dry_run=False, version=self.version)
        builder.execute(self.cmd)


class BaseBuilder(Attack):
    class COMMANDS(enum.Enum):
        clean = enum.auto()
        boostrap = enum.auto()
        build = enum.auto()

    def __init__(self, gp, workdir, dry_run=False, version=None, tempdir=None):
        self.wd = Path(workdir).resolve()
        self.dry_run = dry_run
        self.version = version
        self.tempdir = tempdir
        self.gp = gp

        self.config = None
        self.supported_versions = None
        self.unsupported_versions = None
        self.cmd = None

        self.ready = False

    def _prepare(self):
        self._load_config()
        self._set_versions()

        if self.version is not None and self.version not in self.supported_versions:
            log.warning("Unsupported version '%s' set.", self.version)

        self._validate_workdir()

        self.ready = True

    def _load_config(self):
        config = configparser.ConfigParser()
        with cd(self.wd):
            config.read("config.ini")

        self.config = config

    def _set_versions(self):
        self.supported_versions = self._parse_versions(self.config["BUILD"]["versions"])
        self.unsupported_versions = self._parse_versions(
            self.config["BUILD"]["unsupported.versions"]
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

        with cd(self.wd):
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)

        try:
            proc.check_returncode()
            # TODO should not print in case this is not called as
            # command line application
            print("The command '{cmd}' was successful.".format(cmd=self.cmd.name))
        except subprocess.CalledProcessError:
            log.error("Command ended with non-zero error")

        return proc

    def _validate_workdir(self):
        # TODO add to call pipeline
        with cd(self.wd):
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

    # def uniqfy(self):
    #     # TODO add explanation of uniqfy method - unique AIDs
    #     raise NotImplementedError(
    #         "BaseBuilder does not implement uniqfy method. "
    #         "Your builder must implement it's own version."
    #     )

    # FIXME unify self.wd and self.workidr etc
    def load_aids(self):
        aids = configparser.ConfigParser()
        with cd(self.wd):
            aids.read("aids.ini")

        self.aids = aids

    def save_aids(self):
        with cd(self.wd):
            with open("aids.ini", "w") as aids_file:
                self.aids.write(aids_file)

    def uniqfy(self, used: list = None):
        if used is None:
            used = []

        if not self.ready:
            self._prepare()

        while not self.uniq_aids(used):
            rid = self.aids["BUILD"]["pkg.rid"]
            self.aids["BUILD"]["pkg.rid"] = hex(int(rid, 16) + 1).replace("0x", "")

        self.save_aids()

    def uniq_aids(self, used):
        pkg_rid = self.aids["BUILD"]["pkg.rid"]
        vulns_pix = self.aids["BUILD"]["vulns.pix"]
        pkg_pix = self.aids["BUILD"]["pkg.pix"]
        applet_pix = self.aids["BUILD"]["applet.pix"]

        aids = [pkg_rid + vulns_pix, pkg_rid + pkg_pix, pkg_rid + applet_pix]

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


if __name__ == "__main__":
    pass
