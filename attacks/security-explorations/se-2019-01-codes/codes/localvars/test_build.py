#!/usr/bin/env python

import configparser
import pytest
import os
import subprocess as sp

import zipfile

BUILD_DIR = "build"


def load_versions():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["BUILD"]["versions"].split(",")


VERSIONS = load_versions()


def ant_clean(ver):
    sp.check_output(["ant", "-Dversion=" + ver, "clean"])


def ant_bootstrap(ver):
    sp.check_output(["ant", "-Dversion=" + ver, "bootstrap"])


def ant_build(ver):
    sp.check_output(["ant", "-Dversion=" + ver, "build"])


def gen_vuln_cap(ver):
    # generate the vulnerable/malicious CAP file
    sp.check_output(["pipenv", "run", "./build.py", ver])


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


@pytest.mark.skip(reason="Cannot build any version at the moment.")
@pytest.mark.parametrize("ver", VERSIONS)
def test_creating_vulnerable_cap(ver):
    ant_clean(ver)
    assert ver not in os.listdir(BUILD_DIR)

    ant_bootstrap(ver)
    assert ver in os.listdir(BUILD_DIR)

    ant_build(ver)
    ver_dir = os.path.join(BUILD_DIR, ver)
    assert get_expected_build_dir(ver) == list(os.walk(ver_dir))

    gen_vuln_cap(ver)

    vulns_dir = os.path.join(BUILD_DIR, ver, "com", "se", "vulns", "javacard")
    assert "vulns.new.cap" in os.listdir(vulns_dir)

    # if the generated cap file is not unzippable it
    # means, it's not generated properly
    # it would raise BadZipFile exception, other exceptions mean
    # different failure
    new_cap_file = os.path.join(
        BUILD_DIR, ver, "com", "se", "vulns", "javacard", "vulns.new.cap"
    )

    zp = zipfile.ZipFile(new_cap_file)
