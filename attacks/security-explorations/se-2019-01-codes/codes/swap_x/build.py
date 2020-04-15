#!/usr/bin/env python

import subprocess as sp
import configparser
import os


def get_versions():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["BUILD"]["versions"].split()


def get_directory():
    this_script_path = os.path.realpath(__file__)
    directory = os.path.dirname(this_script_path)
    return directory


def build_version(ver):
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
        "4",
        "0",
    ]
    output = sp.check_output(cmd, stderr=sp.STDOUT,).decode("utf8")
    if "Exception" in output:
        print("Problem with version", ver)

    # print(output)
    os.chdir(wd)


def build_all_versions():
    for ver in get_versions():
        build_version(ver)


if __name__ == "__main__":
    build_all_versions()
