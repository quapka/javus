#!/usr/bin/env python

# sort imports
from jsec.utils import cd
from jsec.utils import CommandLineApp
from pathlib import Path
import configparser
import argparse
import os
import enum
import logging

import subprocess

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
            default=".",
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
            value = Builder.COMMANDS[value]
        except KeyError:
            raise argparse.ArgumentTypeError(
                "Unknown command '{cmd}'".format(cmd=value)
            )

        return value

    def run(self):
        builder = Builder(workdir=self.wd, dry_run=False, version=self.version)
        builder.execute(self.cmd)


class Builder:
    class COMMANDS(enum.Enum):
        clean = enum.auto()
        boostrap = enum.auto()
        build = enum.auto()

    def __init__(self, workdir, dry_run=False, version=None):
        self.wd = workdir
        self.dry_run = dry_run
        self.version = version

        self.config = None
        self.supported_versions = None
        self.unsupported_versions = None
        self.cmd = None

        self.ready = False

    def _prepare(self):
        self._load_config()
        self._set_versions()

        if self.version not in self.supported_versions:
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
            # TODO should not print in case this is not called as command line application
            print("The command '{cmd}' was successful.".format(cmd=self.cmd.name))
        except subprocess.CalledProcessError:
            log.error("Command ended with non-zero error")

    def _validate_workdir(self):
        # TODO add to call pipeline
        with cd(self.wd):
            if not os.path.exists("build.xml"):
                log.error(
                    "Cannot find 'build.xml'. Have you set working directory correctly?"
                )

    def clean(self):
        if self.version is None:
            options = ["clean-all-versions"]
        else:
            # TODO setting value for -Dversion= is problematic when used with quotes
            options = [
                "clean-version",
                "-Dversion={version}".format(version=self.version),
            ]

        self._ant(options=options)

    def build(self):
        if self.version is None:
            options = ["build-all-versions"]
        else:
            options = [
                "build-version",
                "-Dversion={version}".format(version=self.version),
            ]

        self._ant(options=options)

    # def set_unique_aid(self, forbidden=None):
    #     # changes the AIDs for the specific build to make them unique from an existing set
    #     # one way is to open a config and change it's AID
    #     rid = None
    #     aids = []
    #     for name, value in self.config["BUILD"].items():
    #         if name.endswith("pix"):
    #             aids.append(rid + value)
    #         if name.endswith("rid"):
    #             rid = value
    #             aids = []

    #     print(aids)

    def make_temporary(self):
        # in order to prevent changing the source files each attack is copied to
        # temporary directory
        pass

    def execute(self, cmd):
        if not self.ready:
            self._prepare()

        # self.set_unique_aid()

        self.cmd = cmd
        if cmd == self.COMMANDS.clean:
            self.clean()
        elif cmd == self.COMMANDS.boostrap:
            raise NotImplementedError
        elif cmd == self.COMMANDS.build:
            self.build()
        else:
            log.error("Attempt to execute unrecognized command '%s'", cmd)


if __name__ == "__main__":
    pass
