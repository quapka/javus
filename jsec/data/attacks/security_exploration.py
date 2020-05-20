#!/usr/bin/env python

import argparse
import configparser
import os
import subprocess
from pathlib import Path

# from jsec.attack import Attack
from jsec.builder import BaseBuilder
from jsec.settings import ATTACKS
from jsec.utils import cd

# Exemplar config.ini:
# [BUILD]
# # TODO what about jc212
# versions = jc221,jc222,jc303,jc304,jc305u1,jc305u2,jc305u3
# unsupported.versions = jc211,jc310b43
# genidx = 1
# genarg = 0
# # those are the default values, however during the analysis those values might be altered
# # because an applet/package with the same AID can already be installed
# # TODO test rid is always before pix
# pkg.rid = A000000065
# vulns.pix = 03010C02
# pkg.pix = 03010C01
# applet.pix = 03010C0101


class AttackBuilder(BaseBuilder):
    # attacks from SecurityExploration have similar pattern, therefore they can be
    # under one umbrella
    def __init__(self, workdir, save=False, *args, **kwargs):
        super().__init__(workdir=workdir, *args, **kwargs)
        # FIXME validate, that the attack is known
        self.workdir = Path(workdir).resolve()
        self.save = save

        self.config = None
        self.ready = False

    # FIXME redundant - already in the BaseBuilder
    def load_config(self):
        config = configparser.ConfigParser()
        with cd(self.workdir):
            config.read("config.ini")

        self.config = config

    def load_aids(self):
        aids = configparser.ConfigParser()
        with cd(self.workdir):
            aids.read("aids.ini")

        self.aids = aids

    # FIXME redundant - already in the BaseBuilder
    def _prepare(self):
        self.load_config()
        self.load_aids()
        self.ready = True

    def save_aids(self):
        with cd(self.workdir):
            with open("aids.ini", "w") as aids_file:
                self.aids.write(aids_file)

    def _build(self):
        # we can reuse the existing build process
        super()._build()
        # but we also need to generate some files after the build
        self._generate()

    def _generate(self):
        import pudb

        pudb.set_trace()
        vulns_dir = os.path.realpath(
            os.path.join(
                self.workdir, "build", self.version, "com", "se", "vulns", "javacard",
            )
        )

        cap_file = os.path.realpath(os.path.join(vulns_dir, "vulns.cap"))
        exp_file = os.path.realpath(os.path.join(vulns_dir, "vulns.exp"))
        new_cap_file = os.path.realpath(os.path.join(vulns_dir, "vulns.new.cap"))

        # go to _gen
        # wd = os.getcwd()
        # os.chdir("../_gen")
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
            print(output)
            # os.chdir(wd)

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
        pkg_rid = self.aids["BUILD"]["pkg.rid"]
        vulns_pix = self.aids["BUILD"]["vulns.pix"]
        pkg_pix = self.aids["BUILD"]["pkg.pix"]
        applet_pix = self.aids["BUILD"]["applet.pix"]

        aids = [pkg_rid + vulns_pix, pkg_rid + pkg_pix, pkg_rid + applet_pix]

        return set(aids).intersection(set(used)) == set()


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
