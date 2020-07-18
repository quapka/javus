#!/usr/bin/env python

import argparse
import configparser
import os
import subprocess

# TODO put to config to make modular
BUILD_DIR = "build"


current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__)))
print(current_dir)
config = configparser.ConfigParser()
config.read(os.path.join(current_dir, "config.ini"))

gp = [
    "java",
    "-jar",
    os.path.join(os.environ["HOME"], "projects/GlobalPlatformPro/gp.jar"),
]


def _get_vulns_new_cap_path(version):
    print(current_dir)
    print(BUILD_DIR)
    print(version)
    path = os.path.join(
        current_dir,
        BUILD_DIR,
        version,
        "com",
        "se",
        "vulns",
        "javacard",
        "vulns.new.cap",
    )
    print(path)
    return path


def _get_applet_path(version):
    path = os.path.join(
        current_dir,
        BUILD_DIR,
        version,
        "com",
        "se",
        "applets",
        "javacard",
        "applets.cap",
    )
    print(path)
    return path


def install(version):
    print("Installing the vulnerable CAP file")
    cmd = gp + [
        "--verbose",
        "--debug",
        "--install",
        _get_vulns_new_cap_path(version),
    ]
    output = subprocess.check_output(cmd)
    print(output.decode("utf8"))

    print("Installing the applet CAP file")
    cmd = gp + [
        "--verbose",
        "--debug",
        "--install",
        _get_applet_path(version),
    ]
    output = subprocess.check_output(cmd)
    print(output.decode("utf8"))


def uninstall(version):
    print("Uninstalling the applet CAP file")
    cmd = gp + [
        "--verbose",
        "--debug",
        "--uninstall",
        _get_applet_path(version),
    ]
    output = subprocess.check_output(cmd)
    print(output.decode("utf8"))

    print("Uninstalling the vulnerable CAP file")
    cmd = gp + [
        "--verbose",
        "--debug",
        "--uninstall",
        _get_vulns_new_cap_path(version),
    ]
    output = subprocess.check_output(cmd)
    print(output.decode("utf8"))


def _get_applet_select_apdu():
    apdu = "00a40400"
    rid = config["BUILD"]["pkg.rid"]
    pix = config["BUILD"]["applet.pix"]
    aid = rid + pix
    aid_len = "{:02X}".format(len(bytes.fromhex(aid)))
    return apdu + aid_len + aid


def read_mem(payload):

    cmd = gp + [
        "--verbose",
        "--debug",
        "--apdu",
        _get_applet_select_apdu(),
        "--apdu",
        "8010010204{}7F".format(payload.hex()),
        "--dump",
        "read-mem.apdu.{}".format(payload.hex()),
    ]
    output = subprocess.check_output(cmd)
    print(output.decode("utf8"))


def write_mem(payload):
    # TODO calculate the lenght of the payload
    cmd = gp + [
        "--verbose",
        "--debug",
        "--apdu",
        _get_applet_select_apdu(),
        "--apdu",
        "8011010208{}7F".format(payload.hex()),
        "--dump",
        "write-mem.apdu.{}".format(payload.hex()),
    ]
    output = subprocess.check_output(cmd)
    print(output.decode("utf8"))


def validate_jc_version(value):
    if value not in config["BUILD"]["versions"].split(","):
        raise argparse.ArgumentTypeError(
            "The version '{}' is not supported.".format(value)
        )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("version", type=validate_jc_version)
    args = parser.parse_args()

    version = args.version

    # install(version)
    # # // send READMEM APDU
    # read_mem(bytes([0x00, 0x00, 0xC0, 0x00]))
    # # // send WRITEMEM APDU
    # write_mem(bytes([0x00, 0x0A, 0x04, 0x00, 0xAA, 0xBB, 0xCC, 0xDD]))
    # # // send WRITEMEM APDU
    # write_mem(bytes([0x00, 0x0E, 0x04, 0x01, 0x11, 0x22, 0x33, 0x44]))
    # # // send READMEM APDU
    # read_mem(bytes([0x00, 0x00, 0xC0, 0x01]))
    # uninstall(version)
