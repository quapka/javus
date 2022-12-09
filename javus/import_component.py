#!/usr/bin/env python3


import argparse
import shutil
import subprocess as sp
import tempfile
import zipfile
import os
import time

import pandas as pd
from pathlib import Path

import plotly.express as px

from javus.components import ImportComponent, get_import_path

# Given a cap file, produce a file with a specific package version
PKG_NAME_2_VERSIONS = {
    "javacard.framework": [
        (1, 0),
        (1, 1),
        # the previous were added artificially
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 6),
        (1, 6),
        (1, 8),
    ],
    "javacard.security": [
        (1, 0),
        (1, 1),
        # the previous were added artificially
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 6),
        (1, 6),
        (1, 7),
    ],
    "javacardx.crypto": [
        (1, 0),
        (1, 1),
        # the previous were added artificially
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 6),
        (1, 6),
        (1, 7),
    ],
}


def update_pkg_minor(
    cap_path: Path, result_dir: Path, pkg_name: str  # , major: int, minor: int
):
    zf = zipfile.ZipFile(cap_path)

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)

        import_path = get_import_path(tempdir)
        with open(import_path, "rb") as handle:
            ic = ImportComponent.parse(handle)
            # pkg = ic.packages[1]
            # pkg.increment_minor_version()

        versions = PKG_NAME_2_VERSIONS[pkg_name]
        for major, minor in versions:
            pkg = ic.get_package(name=pkg_name)
            if pkg is None:
                raise ValueError(f"Package {pkg_name} not found in {ic}")

            pkg.set_minor_version(value=minor)

            with open(import_path, "wb") as handle:
                handle.write(ic.collect())

            orig_name = cap_path.stem
            if not result_dir.is_dir():
                raise ValueError(f"The result_dir {result_dir} is not a directory")

            name = f"{orig_name}_{pkg_name}-{major}.{minor}.cap"
            new_path = result_dir / name
            print(f"Creating: {new_path}")
            shutil.make_archive(new_path, "zip", tempdir)
            shutil.move(str(new_path) + ".zip", new_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cap", type=Path, help="The path to a CAP file whose packages will be altered."
    )
    parser.add_argument(
        "pkg",
        type=str,
        help="The fullname of the target package, e.g. 'javacard.framework'",
    )
    parser.add_argument(
        "dir",
        type=Path,
        help="The path to the directory where the newly created CAP files will be stored",
    )
    # parser.add_argument("min", type=int)
    # parser.add_argument("max", type=int)

    args = parser.parse_args()
    cap_path = args.cap
    pkg_name = args.pkg
    result_dir = args.dir

    if cap_path.is_dir():
        for cap_file in sorted(cap_path.rglob("*.cap")):
            update_pkg_minor(
                cap_path=cap_file, result_dir=result_dir, pkg_name=pkg_name
            )
    else:
        update_pkg_minor(cap_path=cap_path, result_dir=result_dir, pkg_name=pkg_name)


def security_vs_crypto():
    parser = argparse.ArgumentParser()
    parser.add_argument("card_name")
    args = parser.parse_args()
    card_name = args.card_name

    def install(path):
        proc = sp.run(["gp", "--install", path])
        return proc.returncode == 0
        # return proc.stdout.decode()

    def uninstall(path):
        proc = sp.run(["gp", "--uninstall", path])
        return proc.returncode == 0

    # 0. [DONE] Build with a different AID
    # 1. [TODO] Iterate over the prebuilt SDK versions
    versions = [
        # "jc221",
        "jc222",
        "jc303",
        "jc304",
        "jc305u1",
        "jc305u2",
        "jc305u3",
        "jc310b43",
    ]
    # FIXME run for all
    ROOT_DIR = Path(
        "/home/qup/projects/javus/javus/data/attacks/crypto_and_security_pkg"
    )
    # versions = ["jc221"]
    for version in versions:
        df = pd.DataFrame()
        cap_path = ROOT_DIR / "build" / version / f"crypto-security-pkg-{version}.cap"
        print(f"Processing {cap_path}")
        # 2. Iterate over the crypto and security matrix
        for sc_major, sc_minor in PKG_NAME_2_VERSIONS["javacard.security"]:

            row = pd.Series(dtype="int")
            row.name = f"sec {sc_major}.{sc_minor}"

            for cr_major, cr_minor in PKG_NAME_2_VERSIONS["javacardx.crypto"]:
                # Unzip and open the original CAP
                zf = zipfile.ZipFile(cap_path)
                with tempfile.TemporaryDirectory() as tempdir:
                    zf.extractall(tempdir)

                    import_path = get_import_path(tempdir)
                    with open(import_path, "rb") as handle:
                        ic = ImportComponent.parse(handle)
                    # Set the new package versions
                    scpkg = ic.get_package(name="javacard.security")
                    if scpkg is None:
                        raise ValueError(f"Package javacard.security not found in {ic}")

                    scpkg.set_minor_version(value=sc_minor)

                    crpkg = ic.get_package(name="javacardx.crypto")
                    if crpkg is None:
                        raise ValueError(f"Package javacardx.crypto not found in {ic}")

                    crpkg.set_minor_version(value=cr_minor)

                    # print(import_path)
                    with open(import_path, "wb") as handle:
                        handle.write(ic.collect())

                    # 3. Create the CAP file and install it - work even in failure case
                    # tmpcap = tempfile.NamedTemporaryFile(delete=False)
                    with tempfile.NamedTemporaryFile() as tmpcap:
                        # tmpcap.write(b"xxxxxxxxxxxxxxxxxxxxxxxxx")
                        # tmpcap.flush()
                        print(shutil.make_archive(tmpcap.name, "zip", tempdir))
                        # print(sp.check_output(["stat", tmpcap.name]).decode())
                        # out = sp.check_output(["ls", "-Rlat", tempdir])
                        # print(out.decode())
                        new_cap = tmpcap.name + ".zip"

                        installed = install(new_cap)
                        row[f"cr {cr_major}.{cr_minor}"] = 1 if installed else 0
                        # print(f"Installed {installed}")

                        if installed:
                            uninstalled = uninstall(new_cap)
                            if not uninstalled:
                                print(
                                    f"Could not uninstall version:{version}, sc_minor:{sc_minor}, cr_minor:{cr_minor} file:{new_cap}"
                                )
                        # print(f"Unnstalled {uninstalled}")

                        # output = sp.check_output(["hexdump", tmpcap.name + ".zip"])
                        # print(output.decode())

                    # os.unlink(tmpcap.name)
            df = df.append(row)

        df.to_pickle(f"{card_name}_{version}.pkl")
        fig = px.imshow(df)
        fig.update_xaxes(side="top")
        fig.show()

    # 4. Create a table security x crypto


if __name__ == "__main__":
    main()
    # security_vs_crypto()
