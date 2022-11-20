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

# source: https://github.com/petrs/jcAIDScan/blob/master/jcAIDScan.py#L81
PKG_AID_TO_NAME = {
    "A0000000620001": "java.lang",
    "A0000000620002": "java.io",
    "A0000000620003": "java.rmi",
    "A0000000620101": "javacard.framework",
    "A000000062010101": "javacard.framework.service",
    "A0000000620102": "javacard.security",
    "A0000000620201": "javacardx.crypto",
    "A0000000620202": "javacardx.biometry",
    "A0000000620203": "javacardx.external",
    "A0000000620204": "javacardx.biometry1toN",
    "A0000000620205": "javacardx.security",
    "A000000062020801": "javacardx.framework.util",
    "A00000006202080101": "javacardx.framework.util.intx",
    "A000000062020802": "javacardx.framework.math",
    "A000000062020803": "javacardx.framework.tlv",
    "A000000062020804": "javacardx.framework.string",
    "A0000000620209": "javacardx.apdu",
    "A000000062020901": "javacardx.apdu.util",
    "A00000015100": "org.globalplatform",
    "A00000015102": "org.globalplatform.contactless",
    "A00000015103": "org.globalplatform.securechannel",
    "A00000015104": "org.globalplatform.securechannel.provider",
    "A00000015105": "org.globalplatform.privacy",
    "A00000015106": "org.globalplatform.filesystem",
    "A00000015107": "org.globalplatform.upgrade",
    "A0000000030000": "visa.openplatform",
}


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

    def __str__(self):
        """
        <name/AID> <major>.<minor>
        """
        try:
            name = PKG_AID_TO_NAME[self.AID.hex().upper()]
        except KeyError:
            name = self.AID.hex(sep=" ")

        major = int.from_bytes(self.major_version, byteorder="big")
        minor = int.from_bytes(self.minor_version, byteorder="big")
        output = f"{name} {major}.{minor}"
        return output


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

    def __str__(self):
        tag = int.from_bytes(self.tag, byteorder="big")
        size = int.from_bytes(self.size, byteorder="big")
        count = int.from_bytes(self.count, byteorder="big")
        packages = "\n\t".join([str(p) for p in self.packages])
        output = f"""
ImportComponent:
    tag: {tag}
    size: {size}
    count: {count}
    packages:
        {packages}"""
        return output.strip()


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


def print_import_component(cap_path: Path):
    zf = zipfile.ZipFile(cap_path)

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)

        import_path = get_import_path(tempdir)
        with open(import_path, "rb") as handle:
            ic = ImportComponent.parse(handle)

    print(ic)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--path", type=Path, default=Path("./javacardversion-jc211.cap")
    )
    args = parser.parse_args()

    path = args.path
    if path.is_dir():
        for cap_file in sorted(path.rglob("*.cap")):
            print(cap_file.name)
            print_import_component(cap_path=cap_file)
            print()
    else:
        print_import_component(cap_path=path)
    # confuse_import_component(cap_path=args.path)


if __name__ == "__main__":
    main()
