from javus.executor import BaseAttackExecutor
from javus.builder import BaseAttackBuilder
import random
import subprocess
import random
import pyradamsa
from javus.utils import cd, proc_to_dict
from javus.settings import SUBMODULES_DIR

from javus.components import confuse_import_component, ImportComponent, get_import_path
import zipfile
import tempfile
import shutil

import os

import pathlib


class AttackBuilder(BaseAttackBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # fix seed for every build
        self.seed = random.randint(0, 2**32)
        self.rad = pyradamsa.Radamsa()

    def _build(self):
        super()._build()
        if self.version is None:
            self.confuse_all_versions()
        else:
            self.confuse_version(version=self.version)

    def confuse_all_versions(self):
        # TODO versions could be changed to self.versions
        versions = self.config.get_sdk_versions("BUILD", "versions")
        for version in versions:
            self.confuse_version(version=version)

    # def confuse_version(self, version):
    #     with cd(self.workdir):
    #         # open the original non-malicious CAP file and fuzz it
    #         orig_file = pathlib.Path(self.workdir / "build" / version.raw / "orig.cap")
    #         confused_file = pathlib.Path(
    #             self.workdir / "build" / version.raw / "confused.cap"
    #         )

    #         confuse_import_component(orig_file, confused_file)

    def confuse_version(self, version):
        # with cd(self.workdir):
        # open the original non-malicious CAP file and fuzz it
        orig_file = pathlib.Path(self.workdir / "build" / version.raw / "orig.cap")

        zf = zipfile.ZipFile(orig_file)
        with tempfile.TemporaryDirectory() as tempdir:
            zf.extractall(tempdir)
            import_path = get_import_path(tempdir)

            with open(import_path, "rb") as handle:
                ic = ImportComponent.parse(handle)

            for i, pkg in enumerate(ic.packages):
                pkg.increment_minor_version()
                confused_file = pathlib.Path(
                    self.workdir / "build" / version.raw / f"confused-{i+1}-min+1.cap"
                )
                with open(import_path, "wb") as handle:
                    handle.write(ic.collect())

                shutil.make_archive(confused_file, "zip", tempdir)
                shutil.move(str(confused_file) + ".zip", confused_file)
                # >>

                # NOTE decrement twice to restore
                pkg.decrement_minor_version()
                pkg.decrement_minor_version()
                confused_file = pathlib.Path(
                    self.workdir / "build" / version.raw / f"confused-{i+1}-min-1.cap"
                )
                with open(import_path, "wb") as handle:
                    handle.write(ic.collect())
                shutil.make_archive(confused_file, "zip", tempdir)
                shutil.move(str(confused_file) + ".zip", confused_file)
                # >>

                pkg.increment_major_version()
                confused_file = pathlib.Path(
                    self.workdir / "build" / version.raw / f"confused-{i+1}-maj+1.cap"
                )
                with open(import_path, "wb") as handle:
                    handle.write(ic.collect())
                shutil.make_archive(confused_file, "zip", tempdir)
                shutil.move(str(confused_file) + ".zip", confused_file)
                # >>

                # NOTE decrement twice to restore
                pkg.decrement_major_version()
                pkg.decrement_major_version()
                confused_file = pathlib.Path(
                    self.workdir / "build" / version.raw / f"confused-{i+1}-maj-1.cap"
                )
                with open(import_path, "wb") as handle:
                    handle.write(ic.collect())
                shutil.make_archive(confused_file, "zip", tempdir)
                shutil.move(str(confused_file) + ".zip", confused_file)


class Scenario:
    STAGES = [
        # {
        #     # 'install' is one of the predefined stages
        #     "name": "install",
        #     "path": "build/{version}/confused.cap",
        #     "optional": False,
        # },
    ]

    @classmethod
    def dynamic_stages(cls, workdir):
        cls.STAGES = []
        for sdk_path in (workdir / "build").iterdir():
            version = sdk_path.name
            for cap_path in sdk_path.iterdir():
                path = f"build/{version}/{cap_path.name}"
                cls.STAGES.extend(
                    [
                        {
                            "name": "install",
                            "path": path,
                            "optional": True,
                        },
                        # NOTE manually unistall to workaround AID reuse
                        {
                            "name": "uninstall",
                            "path": path,
                            "optional": True,
                        },
                    ]
                )
