#!/usr/bin/env python

import configparser
from pathlib import Path

from jsec.executor import BaseAttackExecutor
from jsec.settings import DATA
from jsec.utils import JCVersion, SDKVersion, cd, load_versions


class JCVersionExecutor(BaseAttackExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # workdir is fixed here
        self.workdir = Path(DATA / "jcversion").resolve()

    def get_jcversion(self) -> "JCVersion":
        # TODO add better splitter, that handles spaces etc.
        self.config = configparser.ConfigParser()
        self.config.read(self.workdir / "config.ini")
        with cd(self.workdir):
            versions = self.config["BUILD"]["versions"].split(",")
        versions = load_versions(versions)

        for version in versions:
            # FIXME setting versions like so is quite a weird thing
            version = SDKVersion.from_str(version)
            report = self.execute(sdk_version=version)
            # FIXME after changing gppw the version cannot be read like this probably
            if report[2]["SEND_READ_VERSION"]["status"] == "9000":
                return JCVersion.from_str(report[2]["SEND_READ_VERSION"]["payload"])

        return JCVersion.from_str("")


class Stages:
    STAGES = [
        {
            "name": "install",
            "path": "build/{version}/javacardversion-{version}.cap",
            "optional": False,
        },
        {
            # the apdu for reading the version, without the select
            "name": "send",
            "payload:": "80 04 00 00 02",
            "comment": "empty",
            "optional": True,
        },
        {
            "name": "uninstall",
            "path": "build/{version}/javacardversion-{version}.cap",
            "optional": True,
        },
    ]


if __name__ == "__main__":
    executor = JCVersionExecutor()
    print(executor.get_jcversion())
