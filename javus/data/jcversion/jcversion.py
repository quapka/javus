#!/usr/bin/env python

import configparser
from pathlib import Path

from javus.executor import BaseAttackExecutor
from javus.settings import DATA
from javus.utils import JCVersion, SDKVersion, cd, load_versions


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
            if report[1]["success"]:
                # TODO this is quite cumbersome
                version_str = report[1]["communication"]["8004000002"]["payload"]
                return JCVersion.from_str(version_str)

        return JCVersion.from_str("")


class Scenario:
    STAGES = [
        {
            "name": "install",
            "path": "build/{version}/javacardversion-{version}.cap",
            "optional": False,
        },
        {
            # the apdu for reading the version, without the select
            "name": "send",
            "payload": "80 04 00 00 02",
            "comment": "empty",
            "optional": True,
        },
        # {
        #     "name": "uninstall",
        #     "path": "build/{version}/javacardversion-{version}.cap",
        #     "optional": True,
        # },
    ]


if __name__ == "__main__":
    executor = JCVersionExecutor()
    print(executor.get_jcversion())
