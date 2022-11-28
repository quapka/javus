#!/usr/bin/env python3

import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")

    args = parser.parse_args()
    path = args.path

    framework = []
    crypto = []
    security = []

    with open(path, "r") as handle:
        data = json.load(handle)

    # FIXME missing the CAP with both security and crypto
    for file, ic in data.items():
        for package in ic["packages"]:
            if package["name"] == "javacard.framework":
                framework.append((package["major_version"], package["minor_version"]))
            elif package["name"] == "javacard.security":
                security.append((package["major_version"], package["minor_version"]))
            elif package["name"] == "javacardx.crypto":
                crypto.append((package["major_version"], package["minor_version"]))

    print("javacard.framework")
    print(sorted(framework))
    print("javacard.security")
    print(sorted(security))
    print("javacardx.crypto")
    print(sorted(crypto))


if __name__ == "__main__":
    main()
