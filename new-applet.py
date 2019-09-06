#!/usr/bin/env python3

import argparse
import binascii
import os
import re
import shutil

class NewApplet(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=
            'This script creates a new project folder for a new Java Card applet',
        )
        self.add_options()
        self.process_options()

        self.repo_dir = os.path.abspath(os.path.dirname(__file__))

    def add_options(self):
        required_named = self.parser.add_argument_group('required named arguments')
        required_named.add_argument(
            '-n', '--project-name',
            help='Project name of the new applet',
            required=True,
        )

        required_named.add_argument(
            '-N', '--package-name',
            required=True,
            help='Package name of the new applet',
        )

        required_named.add_argument(
            '-v', '--java-card-version',
            help='Version of the Java Card extensions',
            required=True,
            type=self.validate_jc_version,
        )

        required_named.add_argument(
            '-r', '--rid',
            help='The RID - Registered Application Provider Identifier for the applet',
            required=True,
            type=self.validate_rid,
        )

        required_named.add_argument(
            '-p', '--pix',
            help='The PIX - Proprietary Application Identifier Extension for the applet',
            required=True,
            type=self.validate_pix,
        )

        source_path = os.path.join(os.environ['HOME'], 'projects', 'fi',
                'thesis', 'applet-template')

        self.parser.add_argument(
            '-s', '--source-path',
            help='The path to the directory of the source template',
            default=source_path,
        )

        required_named.add_argument(
            '-d', '--dest-path',
            help='The path to the directory of the destinaton',
            required=True,
        )


    def process_options(self):
        args = self.parser.parse_args()
        self.project_name = args.project_name
        self.package_name = args.package_name
        self.jc_version = args.java_card_version
        self.rid = args.rid
        self.pix = args.pix
        self.source_path = args.source_path
        self.dest_path = args.dest_path

    def create_applet_template(self):
        # create project directory
        os.makedirs(os.path.join(self.dest_path))
        # create the build file
        with open(os.path.join(self.source_path, 'build.xml'), 'r') as f:
            data = f.read()

        data = re.sub('<ProjectName>', self.project_name, data)
        data = re.sub('<PackageName>', self.package_name, data)
        data = re.sub('<JCVersion>', 'JC'+ self.jc_version, data)
        data = re.sub('<RID>', self.rid, data)
        if not self.pix:
            self.pix = ''
        data = re.sub('<PIX>', self.pix, data)

        with open(os.path.join(self.dest_path, 'build.xml'), 'w') as f:
            f.write(data)

        # create the makefile
        with open(os.path.join(self.source_path, 'makefile'), 'r') as f:
            data = f.read()

        data = re.sub('<PackageName>', self.package_name.lower(), data)
        data = re.sub('<RID>', self.rid, data)
        if not self.pix:
            self.pix = ''
        data = re.sub('<PIX>', self.pix, data)
        apdu_data_len = int(len(self.rid + self.pix) / 2)
        apdu_data_len = binascii.hexlify(apdu_data_len.to_bytes(1, 'little'))
        apdu_data_len = apdu_data_len.decode('ascii')
        data = re.sub('<DATA_LEN>', apdu_data_len, data)

        with open(os.path.join(self.dest_path, 'makefile'), 'w') as f:
            f.write(data)

        # create the source file
        os.makedirs(os.path.join(self.dest_path, 'src', self.project_name))
        with open(os.path.join(self.source_path, 'src', 'ProjectName', 'ProjectName.java'), 'r') as f:
            data = f.read()
        data = re.sub('<ProjectName>', self.project_name, data)
        data = re.sub('<PackageName>', self.package_name, data)

        with open(os.path.join(self.dest_path, 'src', self.project_name, self.project_name + '.java'), 'w') as f:
            f.write(data)

        os.symlink(os.path.join(self.repo_dir, 'ext'), os.path.join(self.dest_path, 'ext'))

    # def rollback(self):
    #     shutil.rmtree(self.dest_path)

    def run(self):
        # try:
        self.create_applet_template()
        # except:
        #     self.rollback()
        #     raise

    @staticmethod
    def validate_jc_version(value):
        exts = ['212', '221', '222', '305_u3']
        if value not in exts:
            raise argparse.ArgumentTypeError(
                "The Java Card extension '{value}' is not supported. Choose one of {exts}.".format(
                    value=value,
                     exts=', '.join(exts))
            )
        return value

    def validate_rid(self, value):
        if len(value) != 10: # five bytes
            raise argparse.ArgumentTypeError(
                'The lenght of the rid is not correct. Five bytes are expected.')

        if not self.is_hex(value):
            raise argparse.ArgumentTypeError(
                'The value is not hexadecimal.'
            )
        return value.upper()

    def validate_pix(self, value):
        if len(value) < 2 or len(value) > 22: # 1 - 11 bytes
            raise argparse.ArgumentTypeError(
                'The lenght of the rid is not correct. One through eleven bytes are expected.')
        if not self.is_hex(value):

            raise argparse.ArgumentTypeError(
                'The value is not hexadecimal.'
            )

        return value.upper()

    @staticmethod
    def is_hex(value):
        try:
            bytes.fromhex(value)
        except ValueError:
            return False
        return True


if __name__ == '__main__':
    new_applet = NewApplet()
    new_applet.run()
