#!/usr/bin/env python3

import argparse

import os
import glob
import zipfile
import tempfile
from pathlib import Path
import shutil

from collections import namedtuple
from dataclasses import dataclass

import sys
from typing import List


@dataclass
class AID:
    RID: bytes  # 5 bytes
    PIX: bytes  # 0-11 bytes


@dataclass
class package_info:
    minor_version: bytes  # u1
    major_version: bytes  # u1
    AID_length: bytes  # u1
    # AID: List[AID]  # AID[AID_length]
    AID: bytes  # AID[AID_length]

    @classmethod
    def parse(cls, stream: bytes):
        minor_version = stream.read(1)
        major_version = stream.read(1)
        AID_length = stream.read(1)
        AID = stream.read(int.from_bytes(AID_length, byteorder="big"))

        return (
            package_info(
                minor_version=minor_version,
                major_version=major_version,
                AID_length=AID_length,
                AID=AID,
            ),
            stream,
        )

    # FIXME do not overflow 255
    def increment_minor_version(self):
        value = int.from_bytes(self.minor_version, byteorder="big")
        value += 1
        self.minor_version = value.to_bytes(1, byteorder="big")

    def decrement_minor_version(self):
        value = int.from_bytes(self.minor_version, byteorder="big")
        if value != 0:
            value -= 1
        self.minor_version = value.to_bytes(1, byteorder="big")

    def increment_major_version(self):
        value = int.from_bytes(self.major_version, byteorder="big")
        value += 1
        self.major_version = value.to_bytes(1, byteorder="big")

    def decrement_major_version(self):
        value = int.from_bytes(self.major_version, byteorder="big")
        if value != 0:
            value -= 1
        self.major_version = value.to_bytes(1, byteorder="big")

    def collect(self) -> bytes:
        return self.minor_version + self.major_version + self.AID_length + self.AID


@dataclass
class package_name:
    name_length: bytes  # u1
    # name: List[bytes]  # name[name_length]
    name: bytes  # name[name_length]

    @classmethod
    def parse(cls, stream: bytes) -> "package_name":
        raise NotImplemented

    def collect(self) -> bytes:
        raise NotImplemented


# NOTE parsing might be SDK version dependant
@dataclass
class ImportComponent:
    tag: bytes  # u1
    size: bytes  # u2
    count: bytes  # u1, should be 0-128 inclusive
    packages: List[package_info]  # package_info[count]

    @classmethod
    def parse(cls, stream: bytes) -> "ImportComponent":
        tag = stream.read(1)
        size = stream.read(2)
        count = stream.read(1)
        packages = []

        for i in range(int.from_bytes(count, byteorder="big")):
            package, stream = package_info.parse(stream)
            packages.append(package)

        return ImportComponent(
            tag=tag,
            size=size,
            count=count,
            packages=packages,
        )

    def collect(self) -> bytes:
        packages = [p.collect() for p in self.packages]
        return self.tag + self.size + self.count + b"".join(packages)


@dataclass
class HeaderComponent:
    tag: bytes  # u1
    size: bytes  # u2
    magic: bytes  # u4
    minor_version: bytes  # u1
    major_version: bytes  # u1
    flags: bytes  # u1
    package: package_info  # u1
    package_name_info: bytes  # u1 package_name

    @classmethod
    def parse(cls, stream: bytes) -> "HeaderComponent":
        tag = stream.read(1)
        size = stream.read(2)
        magic = stream.read(4)
        minor_version = stream.read(1)
        major_version = stream.read(1)
        flags = stream.read(1)
        # package =
        # package_name =
        return HeaderComponent(
            tag=tag,
            size=size,
            magic=magic,
            minor_version=minor_version,
            major_version=major_version,
            # package=package,
            # ackage_info=package_info,
        )

    def collect(self):
        pass


def get_import_path(tempdir: Path) -> Path:
    """
    Return a path to ImportComponent.cap in a `tempdir` if it exists
    """
    for root, dirs, files in os.walk(tempdir):
        path = root.split(os.sep)
        for file in files:
            if file == "Import.cap":
                return Path("/") / "/".join(path) / f"{file}"


def confuse_import_component(cap_path: Path, result_path: Path):
    zf = zipfile.ZipFile(cap_path)

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)

        import_path = get_import_path(tempdir)
        print("reading")
        with open(import_path, "rb") as handle:
            ic = ImportComponent.parse(handle)
            print(ic)
            pkg = ic.packages[1]
            pkg.increment_minor_version()

        print("writing")
        print(ic)
        with open(import_path, "wb") as handle:
            # handle.write(tag + size + count + package_info)
            handle.write(ic.collect())

        shutil.make_archive(result_path, "zip", tempdir)
        shutil.move(str(result_path) + ".zip", result_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--path", type=Path, default=Path("./javacardversion-jc211.cap")
    )
    args = parser.parse_args()

    confuse_import_component(cap_path=args.path)


if __name__ == "__main__":
    main()
