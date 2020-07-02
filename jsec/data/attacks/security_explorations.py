#!/usr/bin/env python

import argparse
import configparser
import os
import subprocess
from pathlib import Path

from jsec.builder import BaseBuilder
from jsec.executor import BaseAttackExecutor
from jsec.settings import ATTACKS
from jsec.utils import cd


class AttackBuilder(BaseBuilder):
    r"""Attacks from SecurityExploration have similar pattern, therefore they can
    share the AttackBuilder
    """

    def __init__(self, workdir, save=False, *args, **kwargs):
        super().__init__(workdir=workdir, *args, **kwargs)
        # FIXME validate, that the attack is known
        self.workdir = Path(workdir).resolve()
        self.save = save

        self.config = None
        self.ready = False

    def _prepare(self):
        super()._prepare()
        self.load_aids()

    def save_aids(self):
        with cd(self.workdir):
            with open("aids.ini", "w") as aids_file:
                self.aids.write(aids_file)

    def _build(self):
        # we can reuse the existing build process
        super()._build()
        # but we also need to generate some files after the build
        if self.version is None:
            self._generate_all_versions()
        else:
            self._generate_version(version=self.version)

    def _generate_all_versions(self):
        versions = self.config.get_sdk_versions("BUILD", "versions")
        for version in versions:
            self._generate_version(version=version)

    def _generate_version(self, version=None):
        r"""Generate the vulns.new.cap file for the given version"""
        vulns_dir = os.path.realpath(
            os.path.join(
                self.workdir, "build", version.raw, "com", "se", "vulns", "javacard",
            )
        )

        cap_file = os.path.realpath(os.path.join(vulns_dir, "vulns.cap"))
        exp_file = os.path.realpath(os.path.join(vulns_dir, "vulns.exp"))
        new_cap_file = os.path.realpath(os.path.join(vulns_dir, "vulns.new.cap"))

        # TODO this is probably not cross-platform, and other subprocess calls as well :/
        with cd(ATTACKS / "_gen"):
            cmd = [
                "java",
                "Gen",
                cap_file,
                exp_file,
                new_cap_file,
                # GENIDX,
                self.config["BUILD"]["genidx"],
                # GENARG,
                self.config["BUILD"]["genarg"],
            ]
            output = subprocess.check_output(cmd).decode("utf8")

    def uniqfy(self, used=None):
        if used is None:
            used = []

        if not self.ready:
            self._prepare()

        while not self.uniq_aids(used):
            rid = self.aids["BUILD"]["pkg.rid"]
            self.aids["BUILD"]["pkg.rid"] = hex(int(rid, 16) + 1).replace("0x", "")

        self.save_aids()

    def uniq_aids(self, used):
        if not self.ready:
            self._prepare()

        pkg_rid = self.aids["BUILD"]["pkg.rid"]
        vulns_pix = self.aids["BUILD"]["vulns.pix"]
        pkg_pix = self.aids["BUILD"]["pkg.pix"]
        applet_pix = self.aids["BUILD"]["applet.pix"]

        aids = [pkg_rid + vulns_pix, pkg_rid + pkg_pix, pkg_rid + applet_pix]
        aids = [aid.upper() for aid in aids]

        return set(aids).intersection(set(used)) == set()


class AttackExecutor(BaseAttackExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aids = None

    def load_aids(self):
        aids = configparser.ConfigParser()
        with cd(self.workdir):
            aids.read("aids.ini")

        self.aids = aids
        return

    def construct_aid(self) -> bytes:
        # FIXME this is so weird and ugly, each send should somehow define to which applet
        # it sends its data
        if self.aids is None:
            self.load_aids()
        rid = self.aids["BUILD"]["pkg.rid"]
        pix = self.aids["BUILD"]["applet.pix"]
        return bytes.fromhex(rid + pix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name")
    parser.add_argument("-v", "--version")
    parser.add_argument("-c", "--cmd")

    args = parser.parse_args()

    if args.name is not None:
        attack_name = args.name
    else:
        attack_name = "arraycopy"

    if args.version is not None:
        version = args.version
    else:
        version = None

    if args.cmd is not None:
        cmd = BaseBuilder.COMMANDS[args.cmd]
    else:
        cmd = BaseBuilder.COMMANDS.build

    se = AttackBuilder(workdir=attack_name, version=version)
    se.execute(cmd=cmd)
