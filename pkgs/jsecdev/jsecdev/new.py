#!/usr/bin/env python3

import argparse
import os
import re
import shutil

from jsecdev.settings import DATA, JSEC_ATTACKS_DIR


# TODO unify naming 'skeleton' and 'template'
class App(object):
    NEW_SKELETON_CMD = "new-skeleton"
    NEW_SKELETON_CMD_ALIAS = "ns"

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description=(
                "This script creates a new project folder for a new Java Card applet"
            ),
        )
        self.add_subparsers()
        self.process_options()

        self.repo_dir = os.path.abspath(os.path.dirname(__file__))

    def add_subparsers(self):
        self.subparsers = self.parser.add_subparsers(
            title="Available commands",
            description="Here follows the list of sub-commands, that you can run",
            dest="sub_command",
        )
        # TODO in Python3.8 required is already a keyword
        self.subparsers.required = True
        self.add_template_parser()

    def add_template_parser(self):
        self.template_parser = self.subparsers.add_parser(
            self.NEW_SKELETON_CMD,
            help="Create a skeleton for a new attack",
            aliases=["ns"],
        )
        named = self.template_parser.add_argument_group("required arguments")
        named.add_argument(
            "-n",
            "--project-name",
            help="Project name of the new applet, should be in CamelCase",
            type=self.validate_project_name,
            required=True,
        )

        named.add_argument(
            "-N",
            "--package-name",
            required=True,
            help="Package name of the new applet",
        )

        self.template_parser.add_argument(
            "-r",
            "--rid",
            help="The RID - Registered Application Provider Identifier for the applet",
            default="0011223344",
            type=self.validate_rid,
        )

        self.template_parser.add_argument(
            "-p",
            "--pix",
            help="The PIX - Proprietary Application Identifier Extension for the applet",
            default="AABB",
            type=self.validate_pix,
        )

        # TODO ultimately this has to be a valid name for python import
        self.template_parser.add_argument(
            "-d",
            "--dest-name",
            help="The name of the directory in jsec/data/attacks. Defaults to --project-name",
            type=self.validate_dest_name,
        )

    def validate_dest_name(self, value) -> str:
        value = value.strip()
        if not value.isidentifier():
            raise argparse.ArgumentTypeError(
                "--dest-path needs to be a valid Python3 identifier, because it"
                "will be dynamically imported later on. See "
                "https://docs.python.org/3.3/reference/lexical_analysis.html#identifiers for details on identifiers"  # flake8: noqa
            )

        if (JSEC_ATTACKS_DIR / value).exists():
            used = os.listdir(JSEC_ATTACKS_DIR)
            raise argparse.ArgumentTypeError(
                "the name '%s' is already used, the existing and therefore "
                "invalid values for --dest-path are {%s}" % (value, ", ".join(used))
            )
        return value

    def validate_rid(self, value):
        if len(value) != 10:  # five bytes
            raise argparse.ArgumentTypeError(
                "The length of the rid is not correct. Five bytes are expected."
            )

        if not self.is_hex(value):
            raise argparse.ArgumentTypeError("The value is not hexadecimal.")
        return value.upper()

    def validate_pix(self, value):
        if len(value) < 2 or len(value) > 22:  # 1 - 11 bytes
            raise argparse.ArgumentTypeError(
                "The length of the rid is not correct. One through eleven bytes are expected."
            )
        if not self.is_hex(value):

            raise argparse.ArgumentTypeError("The value is not hexadecimal.")

        return value.upper()

    def validate_project_name(self, value):
        if re.match("^(?:[A-Z][a-z]*)+$", value):
            return value
        raise argparse.ArgumentTypeError(
            "Please, write the '--project-name' in CamelCase."
        )

    @staticmethod
    def is_hex(value):
        try:
            bytes.fromhex(value)
        except ValueError:
            return False
        return True

    def process_options(self):
        self.args = self.parser.parse_args()
        if self.new_skeleton_cmd():
            self.project_name = self.args.project_name
            self.package_name = self.args.package_name
            self.rid = self.args.rid
            self.pix = self.args.pix
            self.source_path = DATA / "applet_template"
            # TODO dest_name should really be attack name
            if self.args.dest_name is None:
                if self.project_name.isidentifier():
                    self.dest_name = self.project_name.lower()
                else:
                    raise argparse.ArgumentTypeError(
                        "Either provide --dest-name or set --project-name such, that it "
                        "is a valid Python identifier, because it will be dynamically imported "
                    )
            else:
                self.dest_name = self.args.dest_name

            self.dest_path = JSEC_ATTACKS_DIR / self.dest_name

    def create_applet_template(self):
        print("creating the skeleton directories")
        os.makedirs(self.dest_path)

        print("creating a build.xml file")
        self.create_build_file()

        print("creating *.java source files")
        self.create_source_file()

        print("creating aids.ini file")
        self.create_aid_file()

        print("creating config.ini file")
        self.copy_config_file()

        self.create_attack_module_file()

    def create_build_file(self):
        with open(self.source_path / "build.xml") as f:
            data = f.read()

        data = re.sub("<ProjectName>", self.project_name, data)
        data = re.sub("<PackageName>", self.package_name, data)

        with open(os.path.join(self.dest_path, "build.xml"), "w") as f:
            f.write(data)

    def create_source_file(self):
        dest_dir = self.dest_path / "src" / "com" / self.project_name
        os.makedirs(dest_dir)

        source_file = (
            self.source_path / "src" / "com" / "ProjectName" / "ProjectName.java"
        )
        with open(source_file, "r") as f:
            data = f.read()

        data = re.sub("<ProjectName>", self.project_name, data)
        data = re.sub("<PackageName>", self.package_name, data)

        with open(dest_dir / (self.project_name + ".java"), "w",) as f:
            f.write(data)

    def create_aid_file(self):
        with open(self.source_path / "aids.ini", "r") as f:
            data = f.read()
        data = re.sub("<RID>", self.rid, data)
        data = re.sub("<PIX>", self.pix, data)

        with open(self.dest_path / "aids.ini", "w") as f:
            f.write(data)

    def copy_config_file(self):
        r"""Copies the files, that do not to be altered in any way"""
        shutil.copy(self.source_path / "config.ini", self.dest_path / "config.ini")

    def create_attack_module_file(self):
        filename = self.dest_name + ".py"
        print("creating attack module %s file" % filename)
        shutil.copy(
            self.source_path / "applet_template.py", self.dest_path / filename,
        )

    def new_skeleton_cmd(self):
        return self.args.sub_command in [
            self.NEW_SKELETON_CMD,
            self.NEW_SKELETON_CMD_ALIAS,
        ]

    def run(self):
        if self.new_skeleton_cmd():
            self.create_applet_template()

    def validate_rid(self, value):
        if len(value) != 10:  # five bytes
            raise argparse.ArgumentTypeError(
                "The length of the rid is not correct. Five bytes are expected."
            )

        if not self.is_hex(value):
            raise argparse.ArgumentTypeError("The value is not hexadecimal.")
        return value.upper()

    def validate_pix(self, value):
        if len(value) < 2 or len(value) > 22:  # 1 - 11 bytes
            raise argparse.ArgumentTypeError(
                "The length of the rid is not correct. One through eleven bytes are expected."
            )
        if not self.is_hex(value):

            raise argparse.ArgumentTypeError("The value is not hexadecimal.")

        return value.upper()

    def validate_project_name(self, value):
        if re.match("^(?:[A-Z][a-z]*)+$", value):
            return value
        raise argparse.ArgumentTypeError(
            "The 'project-name': {} is not in CamelCase!".format(value)
        )

    @staticmethod
    def is_hex(value):
        try:
            bytes.fromhex(value)
        except ValueError:
            return False
        return True


if __name__ == "__main__":
    new_applet = App()
    new_applet.run()
