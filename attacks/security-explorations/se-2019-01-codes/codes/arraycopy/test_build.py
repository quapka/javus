#!/usr/bin/env python

import configparser
import pytest
import os
import subprocess as sp

BUILD_DIR = "build"


def load_versions():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["BUILD"]["versions"].split(",")

VERSIONS = load_versions()


def ant_clean(ver):
    target = ver + "-clean"
    # clean the build directory
    sp.check_output(["ant", target])


def ant_build(ver):
    sp.check_output(["ant", ver])


def gen_vuln_cap(ver):
    # generate the vulnerable/malicious CAP file
    sp.check_output(["pipenv", "run", "./build.py", ver])


@pytest.mark.parametrize("ver", VERSIONS)
def test_ant_clean_version_empties_build_dir(ver):
    ant_clean(ver)
    assert ver not in os.listdir(BUILD_DIR)


def get_expected_build_dir(ver):
    # TODO this test probably won't work on Windows
    # due to the paths
    build_structure = [
        ("build/" + ver, ["com"], ["vulns.jar", "applets.jar"]),
        ("build/" + ver + "/com", ["se"], []),
        ("build/" + ver + "/com/se", ["vulns", "applets"], []),
        ("build/" + ver + "/com/se/vulns", ["javacard"], []),
        (
            "build/" + ver + "/com/se/vulns/javacard",
            [],
            ["vulns.exp", "vulns.cap", "vulns.jca"],
        ),
        ("build/" + ver + "/com/se/applets", ["javacard"], []),
        (
            "build/" + ver + "/com/se/applets/javacard",
            [],
            ["applets.cap", "applets.exp", "applets.jca"],
        ),
    ]

    return build_structure


@pytest.mark.parametrize("ver", VERSIONS)
def test_ant_build_versions(ver):
    ant_clean(ver)

    ant_build(ver)

    ver_dir = os.path.join(BUILD_DIR, ver)
    assert get_expected_build_dir(ver) == list(os.walk(ver_dir))


# @pytest.mark.parametrize("ver", VERSIONS)
@pytest.mark.parametrize("ver", VERSIONS)
def test_presence_of_generated_vulns_new_cap(ver):
    ant_clean(ver)
    ant_build(ver)

    gen_vuln_cap(ver)

    vulns_dir = os.path.join(BUILD_DIR, ver, "com", "se", "vulns", "javacard")
    assert "vulns.new.cap" in os.listdir(vulns_dir)
