#!/usr/bin/env python

from jsec.attack import BaseAttackExecutor
from jsec.settings import DATA
from jsec.utils import load_versions
from jsec.utils import JCVersion
from pathlib import Path
from jsec.utils import cd
import configparser


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

        # for version in versions:
        for version in versions:
            # FIXME setting versions like so is quite a weird thing
            self.version = version
            report = self.execute()
            if report[2]["SEND_READ_VERSION"]["status"] == "9000":
                return JCVersion.from_str(report[2]["SEND_READ_VERSION"]["payload"])

        return JCVersion.from_str("")


if __name__ == "__main__":
    executor = JCVersionExecutor()
    print(executor.get_jcversion())
