#!/usr/bin/env python

from jsec.attack import Attack
from jsec.utils import cd
import configparser
from pathlib import Path


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


class SecurityExploration(Attack):
    # attacks from SecurityExploration have similar pattern, therefore they can be
    # under one umbrella
    def __init__(self, attack, workdir, save=False):
        self.attack = attack
        self.workdir = Path(workdir).resolve()
        self.save = save

        self.config = None
        self.ready = False

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

    def _prepare(self):
        self.load_config()
        self.load_aids()
        self.ready = True

    def save_aids(self):
        with cd(self.workdir):
            with open("aids.ini", "w") as aids_file:
                self.aids.write(aids_file)

    def uniqfy(self, used=None):
        if used is None:
            used = []

        if not self.ready:
            self._prepare()

        while not self.uniq_aids(used):
            rid = self.aids["BUILD"]["pkg.pix"]
            self.aids["BUILD"]["pkg.pix"] = hex(int(rid, 16) + 1).replace("0x", "")

        self.save_aids()

    def uniq_aids(self, used):
        pkg_rid = self.aids["BUILD"]["pkg.rid"]
        vulns_pix = self.aids["BUILD"]["vulns.pix"]
        pkg_pix = self.aids["BUILD"]["pkg.pix"]
        applet_pix = self.aids["BUILD"]["applet.pix"]

        aids = [pkg_rid + vulns_pix, pkg_rid + pkg_pix, pkg_rid + applet_pix]

        return set(aids).intersection(set(used)) == set()


if __name__ == "__main__":
    se = SecurityExploration("ArrayCopy", "arraycopy")
    se.uniqfy()
