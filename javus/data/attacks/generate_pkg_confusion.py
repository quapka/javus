#!/usr/bin/env python3

import argparse
import os
import re
import shutil

from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="The directory containing cap files", type=Path)
    args = parser.parse_args()

    # 1. iterate over files
    for cap in args.dir.rglob("*.cap"):
        name = cap.stem.replace("-", "_").replace(".", "_")
        print(f"Processing {name}")

        cap_dir = args.dir.parent / name
        # 2. create a dir for them (change - and . to _)
        os.makedirs(cap_dir, exist_ok=True)

        # 3. create aids.ini hardcoded
        with open(cap_dir / "aids.ini", "w") as handle:
            handle.write(
                """
[BUILD]
pkg.rid = 0011223346
applet.pix = AABB""".strip()
            )

        # 4. create config.ini based on jcXXX in file name
        version = re.search(r"_(?P<version>jc[^_]+)", name).group("version")
        with open(cap_dir / "config.ini", "w") as handle:
            handle.write(
                f"""
[BUILD]
versions = {version}
unsupported.versions =""".strip()
            )

        # 5. create Scenario.STAGES
        with open(cap_dir / (name + ".py"), "w") as handle:
            x = f"""class Scenario:
    STAGES = [
        {{
            "name": "install",
            "path": "./{cap.name}",
            "optional": False,
        }}
    ]
        """.strip()
            handle.write(x)

        # 6. copy the original cap
        shutil.copy(cap, cap_dir)

        # 7. create a dummy build.xml
        Path.touch(cap_dir / "build.xml")


if __name__ == "__main__":
    main()
