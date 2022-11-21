#!/usr/bin/env python3

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


import argparse
import shutil
import tempfile
import zipfile

from pathlib import Path

from javus.components import ImportComponent, get_import_path


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


if __name__ == "__main__":
    main()
