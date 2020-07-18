#!/usr/bin/env python

import subprocess as sp


def main():
    print("Building all versions")
    output = sp.check_output(["ant", "build-all-versions"])
    print("Generating all versions")
    output = sp.check_output(["pipenv", "run", "./generate.py"])


if __name__ == "__main__":
    main()
