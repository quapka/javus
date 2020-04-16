#!/usr/bin/env python

import argparse
import subprocess as sp
import configparser
import os


def get_versions():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["BUILD"]["versions"].split(",")


def get_directory():
    this_script_path = os.path.realpath(__file__)
    directory = os.path.dirname(this_script_path)
    return directory


def _build_version(ver):
    vulns_dir = os.path.realpath(
        os.path.join(get_directory(), "build", ver, "com", "se", "vulns", "javacard",)
    )

    cap_file = os.path.realpath(os.path.join(vulns_dir, "vulns.cap"))
    exp_file = os.path.realpath(os.path.join(vulns_dir, "vulns.exp"))
    new_cap_file = os.path.realpath(os.path.join(vulns_dir, "vulns.new.cap"))

    # go to _gen
    wd = os.getcwd()
    os.chdir("../_gen")
    cmd = [
        "java",
        "Gen",
        cap_file,
        exp_file,
        new_cap_file,
        "5",
        "0",
    ]
    output = sp.check_output(cmd).decode("utf8")
    print(output)
    os.chdir(wd)


def build_versions(versions=None):
    if versions is None:
        versions = get_versions()

    for ver in versions:
        print("Building:", ver)
        _build_version(ver)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "versions", nargs="*",
    )

    args = parser.parse_args()
    if args.versions:
        versions = args.versions
    else:
        versions = None

    build_versions(versions=versions)
