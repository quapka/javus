#!/usr/bin/env python3

import argparse
import json
import pprint

import os
import glob
import zipfile
import tempfile
from pathlib import Path
import shutil

from collections import namedtuple
from dataclasses import dataclass

import sys
from typing import List, Union

# FIXME: The keys are actually bytes values, but HEX representation is ambigious
#        using `bytes` as keys is possible (lower x upper)
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

NAME_TO_PKG_AID = {value: key for key, value in PKG_AID_TO_NAME.items()}

COMPONENT_NAME_TO_NUM = {
    "COMPONENT_Header": 1,
    "COMPONENT_Directory": 2,
    "COMPONENT_Applet": 3,
    "COMPONENT_Import": 4,
    "COMPONENT_ConstantPool": 5,
    "COMPONENT_Class": 6,
    "COMPONENT_Method": 7,
    "COMPONENT_StaticField": 8,
    "COMPONENT_ReferenceLocation": 9,
}

NUM_TO_COMPONENT_NAME = {value: key for key, value in COMPONENT_NAME_TO_NUM.items()}


@dataclass
class AID:
    RID: bytes  # 5 bytes
    PIX: bytes  # 0-11 bytes


@dataclass
class package_info:
    # FIXME we have to move to the actual values I am afraid :(
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

    def set_major_version(self, value: int):
        self.major_version = value.to_bytes(1, byteorder="big")

    def set_minor_version(self, value: int):
        self.minor_version = value.to_bytes(1, byteorder="big")

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

    def as_json(self):
        return {
            "minor_version": int.from_bytes(self.minor_version, byteorder="big"),
            "major_version": int.from_bytes(self.major_version, byteorder="big"),
            "AID_length": self.AID_length.hex(),
            "AID": self.AID.hex(),
            "name": PKG_AID_TO_NAME[self.AID.hex().upper()],
        }


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
    # TODO add a method to tell whether a package is available
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

    def get_package(self, name: Union[str, bytes]) -> package_info:
        aid = bytes.fromhex(NAME_TO_PKG_AID[name.strip()])
        for pkg in self.packages:
            if pkg.AID == aid:
                return pkg

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

    def as_json(self):
        return {
            "tag": self.tag.hex(),
            "size": self.size.hex(),
            "count": self.count.hex(),
            "packages": [p.as_json() for p in self.packages],
        }


@dataclass
class DirectoryComponent:
    tag: bytes  # u1
    size: bytes  # u2
    component_sizes: bytes  # [12] u2
    static_field_size: bytes  # static_field_size_info
    import_count: bytes  # u1
    applet_count: bytes  # u1
    custom_count: bytes  # u1
    custom_components: bytes  # [custom_count] custom_component_info

    @classmethod
    def parse(cls, stream: bytes) -> "DirectoryComponent":
        tag = stream.read(1)
        size = stream.read(2)
        # list of sizes of all the components, in 2.2.2 equals to two for all
        # FIXME create the actual array
        # component_sizes = stream.read(2 * 12)
        component_sizes = [int.from_bytes(stream.read(2), "big") for _ in range(12)]
        # FIXME create the sub struct
        static_field_size = stream.read(3 * 2)
        import_count = stream.read(1)
        applet_count = stream.read(1)
        custom_count = stream.read(1)
        custom_components = stream.read(int.from_bytes(custom_count, "big"))

        return DirectoryComponent(
            tag=tag,
            size=size,
            component_sizes=component_sizes,
            static_field_size=static_field_size,
            import_count=import_count,
            applet_count=applet_count,
            custom_count=custom_count,
            custom_components=custom_components,
        )

    def collect(self) -> bytes:
        # FIXME finish impl
        raise NotImplementedError
        return b""

    def __str__(self):
        tag = int.from_bytes(self.tag, byteorder="big")
        size = int.from_bytes(self.size, byteorder="big")
        component_sizes = self.component_sizes
        static_field_size = self.static_field_size
        import_count = int.from_bytes(self.import_count, byteorder="big")
        applet_count = int.from_bytes(self.applet_count, byteorder="big")
        custom_count = int.from_bytes(self.custom_count, byteorder="big")
        custom_components = self.custom_components

        output = f"""
DirectoryComponent:
    tag: {tag}
    size: {size}
    component_sizes: {component_sizes}
    static_field_size: {static_field_size}
    import_count: {import_count}
    applet_count: {applet_count}
    custom_count: {custom_count}
    custom_components: {custom_components}
        """.strip()
        return output


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


def get_import_path(tempdir: Path, target_name: str = "Import.cap") -> Path:
    """
    Return a path to ImportComponent.cap in a `tempdir` if it exists
    """
    for root, dirs, files in os.walk(tempdir):
        path = root.split(os.sep)
        for file in files:
            if file == target_name:
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


def get_import_component(cap_path: Path, as_json: bool = False):
    zf = zipfile.ZipFile(cap_path)

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)

        import_path = get_import_path(tempdir)
        with open(import_path, "rb") as handle:
            ic = ImportComponent.parse(handle)

    if as_json:
        return ic.as_json()

    return ic


def get_directory_component(cap_path: Path, as_json: bool = False):
    zf = zipfile.ZipFile(cap_path)

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)

        path = get_import_path(tempdir, target_name="Directory.cap")
        with open(path, "rb") as handle:
            # ic = .parse(handle)
            dc = DirectoryComponent.parse(handle)
            # with open("jc222-applets-directory-component.cap", "wb") as out:
            #     out.write(handle.read())
            # import sys

            # sys.stdout.write(handle.read())

    if as_json:
        return dc.as_json()
    return dc


def show_directory():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        type=Path,
        help="A path to a CAP file or a directory containing CAP files (recurses into subdirs)",
    )
    args = parser.parse_args()

    path = args.path
    dc = get_directory_component(path)
    ic = get_import_component(path)
    print(dc)
    print(ic)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        type=Path,
        help="A path to a CAP file or a directory containing CAP files (recurses into subdirs)",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
    )
    args = parser.parse_args()
    as_json = args.json

    path = args.path
    result = {}
    package_sets = set()
    if path.is_dir():
        for cap_file in sorted(path.rglob("*.cap")):
            data = get_import_component(cap_path=cap_file, as_json=as_json)
            if as_json:
                result[cap_file.name] = data
            else:
                print(cap_file)
                print(data)
                package_sets.add(tuple(str(pkg) for pkg in data.packages))
                # for pc in data.packages:
                #     print(pc)
                print()
        if as_json:
            print(json.dumps(result, indent=4))
    else:
        data = get_import_component(cap_path=path)
        print(data)

    # confuse_import_component(cap_path=args.path)
    pprint.pprint(package_sets)


if __name__ == "__main__":
    # main()
    show_directory()
