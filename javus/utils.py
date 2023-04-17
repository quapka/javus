#!/usr/bin/env python3
import argparse
import configparser
import enum
import logging
import os
import pathlib
import re
import subprocess
import sys
import time
from contextlib import contextmanager

# from collections import namedtuple
from typing import List, NamedTuple, Optional

import bson
import pymongo
import smartcard
from smartcard.CardConnection import CardConnection
from smartcard.CardConnectionDecorator import CardConnectionDecorator
from smartcard.System import readers

from javus.settings import LIB_DIR

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# FIXME use enum and allow 'debug' as value for --verbose
LOG_LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
]


class Error(enum.Enum):
    UNSUPPORTED_PYTHON_VERSION = -1


class Timer(object):
    def __init__(self):
        self.start = None
        self.end = None
        self.duration = None

    def __enter__(self, *args, **kwargs):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.duration = self.end - self.start


class CommandLineApp(object):
    """
    Template for Python command line applications.
    """

    APP_DESCRIPTION = None

    def __init__(self):
        self.verbosity = logging.ERROR
        self.args = None

        self.parser = argparse.ArgumentParser(
            description=self.APP_DESCRIPTION,
        )
        self.add_subparsers()
        self.add_options()
        self.parse_options()

        self.setup_logging()

    def setup_logging(self, target_log=None):
        if target_log is None:
            target_log = log
        old = logging.getLevelName(target_log.level)
        new = logging.getLevelName(self.verbosity)
        target_log.setLevel(self.verbosity)
        log.debug(
            "logging level for %s changed from %s to %s ", target_log.name, old, new
        )

    def add_subparsers(self):
        r"""
        Allows to add subparsers for parsing sub-commands. To be overriden
        by the subclasses
        """
        pass

    def add_options(self):
        levels = ", ".join([str(lvl) for lvl in LOG_LEVELS])
        self.parser.add_argument(
            "-v",
            "--verbose",
            help="Set the verbosity {"
            + levels
            + "}. Lower number means higher verbosity.",
            type=self.validate_verbosity,
        )

    def validate_verbosity(self, value):
        # FIXME use enum.Enum - already in gppw.py
        try:
            value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("verbosity is not an integer")
        if value not in LOG_LEVELS:
            raise argparse.ArgumentTypeError("verbosity level not from expected range")
        return value

    def parse_options(self):
        self.args = self.parser.parse_args()
        if self.args.verbose is not None:
            self.verbosity = self.args.verbose

    def run(self):
        raise NotImplementedError("The method 'run' has not bee implemented!")


@contextmanager
def cd(new_path):
    """
    kudos to:
    https://stackoverflow.com/questions/431684/how-do-i-change-the-working-directory-in-python/13197763#13197763
    """
    old_path = os.getcwd()
    log.debug("Save old path: %s", old_path)
    try:
        log.debug("Change directory to: %s", new_path)
        # no yield for now, as there is no need for additional information
        os.chdir(new_path)
        yield old_path
    finally:
        # the old directory might also be remove, however there isn't
        # good and logical thing to do, so in that case the exception will be
        # thrown
        # FIXME Ceesjan taught to not to use format in logging!!!
        log.debug("Switch back to old path: %s", old_path)
        os.chdir(old_path)


# FIXME rename to load_sdks
# FIXME depends on external configuration
# TODO maybe just load them directly from the submodule and put it on SDKVersion
def load_versions(versions):
    """
    parses 'jc221,jc221' etc.
    returns the supported versions and orders them
    from newest to oldest
    """
    props = configparser.ConfigParser()
    props.read(LIB_DIR / "sdkversions.properties")
    known = list(props["SUPPORTED_VERSIONS"])

    filtered = []
    for version in versions:
        if version in known:
            filtered.append(version)

    # sort the values based on the order of JC versions in sdkversions.properties
    filtered.sort(key=known.index)

    return filtered[::-1]


class JCVersion(NamedTuple):
    major: Optional[int]
    minor: Optional[int]

    @classmethod
    def from_str(cls_obj, string: str) -> "JCVersion":
        r"""
        Parses output from JavaCard from `JCSystem.getVersion()`, which returns
        a `short` value (two bytes). In case the string is empty `self.major` and
        `self.minor` will be set to `None`.
        param `string`: two bytes
        """
        # TODO add try/except?
        try:
            major = int(string[:2])
        except ValueError:
            major = None

        try:
            minor = int(string[2:])
        except ValueError:
            minor = None

        return cls_obj(major=major, minor=minor)

    def __str__(self) -> str:
        # TODO how to handle 'None' self values?
        return "%s.%s" % (self.major, self.minor)

    def get_sdks(self) -> List["SDKVersion"]:
        r"""
        Returns a list of sdks, that are worth trying for the specific card.
        """
        sdks = []
        available_sdks = SDKVersion.get_available_sdks()
        if self.major is None:
            # be generous and return all the available SDKs
            return available_sdks

        for sdk in available_sdks:
            if sdk.major < self.major:
                sdks.append(sdk)
            elif sdk.major == self.major:
                if self.minor is None:
                    # in case we can't compare we'll use the sdk
                    sdks.append(sdk)
                elif sdk.minor <= self.minor:
                    sdks.append(sdk)

        return sdks


class SDKVersion(NamedTuple):
    major: int
    minor: int
    patch: int
    update: Optional[int]
    # TODO what is 'b' in jc310b43
    b_value: Optional[int]
    # the original string, that was parsed to separate values
    raw: str

    # TODO rename cls_obj to cls
    @classmethod
    def from_str(cls_obj, string: str) -> "SDKVersion":
        string = string.strip().lower()
        # fmt: off
        sdk_regex = re.compile(
                r"((?P<header>jc)"
                r"(?P<major>\d)"
                r"(?P<minor>\d)"
                r"(?P<patch>\d)"
                r"((?P<type>[ub]?)"
                r"(?P<type_value>\d+))?)"
        )
        # fmt: on

        match = sdk_regex.match(string)
        if match is not None:
            major = int(match.group("major"))
            minor = int(match.group("minor"))
            patch = int(match.group("patch"))
            update = None
            b_value = None
            if match.group("type") == "u":
                update = int(match.group("type_value"))
            elif match.group("type") == "b":
                b_value = int(match.group("type_value"))

            return cls_obj(
                major=major,
                minor=minor,
                patch=patch,
                update=update,
                b_value=b_value,
                raw=string,
            )

    @classmethod
    def from_list(cls, string: str, sep: str = ",") -> List["SDKVersion"]:
        sdks = []
        for part in [x.strip() for x in string.split(sep=sep)]:
            sdks.append(cls.from_str(part))

        return sdks

    def __str__(self) -> str:
        return self.raw
        # output = "SDK Version: %s.%s.%s." % (self.major, self.minor, self.patch)
        # if self.update:
        #     output += "u%s" % self.update
        # elif self.b_value:
        #     output += "b%s" % self.b_value
        # return output

    def __repr__(self) -> str:
        return self.raw

    # TODO load only once and get them from the class afterwards
    @classmethod
    def get_available_sdks(cls) -> List["SDKVersion"]:
        sdks = []
        properties = configparser.ConfigParser()
        properties.read(LIB_DIR / "sdkversions.properties")
        for version, _ in properties["SUPPORTED_VERSIONS"].items():
            sdks.append(SDKVersion.from_str(version))

        return sdks

    # TODO missing other comparison methods
    def __eq__(self, other) -> bool:
        result = self.major == other.major
        result = result and self.minor == other.minor
        result = result and self.patch == other.patch
        result = result and self.update == other.update
        result = result and self.b_value == other.b_value
        return result


class AID:
    def __init__(self, string: str = "", rid: bytes = None, pix: bytes = None):
        if string:
            # TODO add input length checks
            aid = bytes.fromhex(string)
            rid = aid[:5]
            if len(rid) != 5:
                raise ValueError("RID from '%s' is not 5 bytes long" % string)
            pix = aid[5:]
            if not (0 <= len(pix) <= 11):
                raise ValueError("PIX length from '%s' is not 0-11 bytes long" % string)
            self.rid = rid
            self.pix = pix
        else:
            if rid is not None:
                if isinstance(rid, str):
                    self.rid = bytes.fromhex(rid)
                elif isinstance(rid, bytes):
                    self.rid = rid
                if pix is not None:
                    if isinstance(pix, str):
                        self.pix = bytes.fromhex(pix)
                    elif isinstance(pix, bytes):
                        self.pix = pix
                else:
                    self.pix = bytes()

    @property
    def aid(self):
        return self.rid + self.pix

    def increase(self):
        r"""Increases `self.rid` by one each time"""
        byteorder = "big"
        rid_len = 5

        rid_as_int = int.from_bytes(self.rid, byteorder) + 1

        self.rid = rid_as_int.to_bytes(rid_len, byteorder)

    def __eq__(self, other):
        if isinstance(other, bytes):
            return self.aid == other
        elif isinstance(other, self.__class__):
            return self.aid == other.aid

    def __str__(self):
        return self.aid.hex().upper()


JC_FRAMEWORK_ISO7816 = {
    "6999": {
        "note": "Applet selection failed",
        "const": "SW_APPLET_SELECT_FAILED",
    },
    "6100": {
        "note": "Response bytes remaining",
        "const": "SW_BYTES_REMAINING_00",
    },
    "6E00": {
        "note": "CLA value not supported",
        "const": "SW_CLA_NOT_SUPPORTED",
    },
    "6884": {
        "note": "Command chaining not supported",
        "const": "SW_COMMAND_CHAINING_NOT_SUPPORTED",
    },
    "6986": {
        "note": "Command not allowed (no current EF)",
        "const": "SW_COMMAND_NOT_ALLOWED",
    },
    "6985": {
        "note": "Conditions of use not satisfied",
        "const": "SW_CONDITIONS_NOT_SATISFIED",
    },
    "6C00": {
        "note": "Correct Expected Length (Le)",
        "const": "SW_CORRECT_LENGTH_00",
    },
    "6984": {
        "note": "Data invalid",
        "const": "SW_DATA_INVALID",
    },
    "6A84": {
        "note": "Not enough memory space in the file",
        "const": "SW_FILE_FULL",
    },
    "6983": {
        "note": "File invalid",
        "const": "SW_FILE_INVALID",
    },
    "6A82": {
        "note": "File not found",
        "const": "SW_FILE_NOT_FOUND",
    },
    "6A81": {
        "note": "Function not supported",
        "const": "SW_FUNC_NOT_SUPPORTED",
    },
    "6A86": {
        "note": "Incorrect parameters (P1,P2)",
        "const": "SW_INCORRECT_P1P2",
    },
    "6D00": {
        "note": "INS value not supported",
        "const": "SW_INS_NOT_SUPPORTED",
    },
    "6883": {
        "note": "Last command in chain expected",
        "const": "SW_LAST_COMMAND_EXPECTED",
    },
    "6881": {
        "note": "Card does not support the operation on the specified logical channel",
        "const": "SW_LOGICAL_CHANNEL_NOT_SUPPORTED",
    },
    "9000": {
        "note": "No Error",
        "const": "SW_NO_ERROR",
    },
    "6A83": {
        "note": "Record not found",
        "const": "SW_RECORD_NOT_FOUND",
    },
    "6882": {
        "note": "Card does not support secure messaging",
        "const": "SW_SECURE_MESSAGING_NOT_SUPPORTED",
    },
    "6982": {
        "note": "Security condition not satisfied",
        "const": "SW_SECURITY_STATUS_NOT_SATISFIED",
    },
    "6F00": {
        "note": "No precise diagnosis",
        "const": "SW_UNKNOWN",
    },
    "6200": {
        "note": "Warning, card state unchanged",
        "const": "SW_WARNING_STATE_UNCHANGED",
    },
    "6A80": {
        "note": "Wrong data",
        "const": "SW_WRONG_DATA",
    },
    "6700": {
        "note": "Wrong length",
        "const": "SW_WRONG_LENGTH",
    },
    "6B00": {
        "note": "Incorrect parameters (P1,P2)",
        "const": "SW_WRONG_P1P2",
    },
}


class RequestAPDU:
    def __init__(self, string: str):
        self.data = None
        self.SW1 = None
        self.SW2 = None

    def success(self):
        pass


class CommandAPDU:
    def __init__(
        self,
        string: str = "",
        # cla=None,
        # ins=None,
        # p1=None,
        # p2=None,
        # lc=None,
        # data=None,
        # le=None,
    ):
        self.CLA = cla
        self.INS = ins
        self.P1 = p1
        self.P2 = p2
        self.Lc = lc
        self.data = data
        self.Le = le


class AttackConfigParser(configparser.ConfigParser):
    def getlist(self, section: str, option: str, *args, sep=",", **kwargs) -> List[str]:
        value = self.get(section, option)
        items = value.split(sep)
        return [x.strip() for x in items if x]

    def get_sdk_versions(self, section: str, option: str, *args, **kwargs) -> List[str]:
        strings = self.getlist(section, option, *args, **kwargs)
        sdks = [SDKVersion.from_str(ver) for ver in strings]
        return sdks

    def get_supported_versions(self) -> List[str]:
        return self.getlist(section="BUILD", option="supported.versions")


class PathTypeEncoder(bson.codec_options.TypeEncoder):
    python_type = pathlib.PosixPath

    def transform_python(self, value: pathlib.PosixPath) -> str:
        return str(value)


path_codec = PathTypeEncoder()
custom_codecs = [path_codec]
type_registry = bson.codec_options.TypeRegistry(custom_codecs)
codec_options = bson.codec_options.CodecOptions(type_registry=type_registry)


# kudos to: https://medium.com/@ramojol/python-context-managers-and-the-with-statement-8f53d4d9f87
class MongoConnection(object):
    def __init__(
        self,
        host="localhost",
        port="27017",
        database="javacard-analysis",
        collation="commands",
    ):
        self.host = host
        self.port = port
        self.connection = None
        self.db_name = database
        self.collation_name = collation

    def __enter__(self, *args, **kwargs):
        conn_str = f"mongodb://{self.host}:{self.port}"
        log.debug("Starting the connection with %s", conn_str)

        self.connection = pymongo.MongoClient(conn_str)
        self.db = self.connection[self.db_name]
        self.col = self.db.get_collection(
            self.collation_name, codec_options=codec_options
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug("Closing the connection to the database")
        self.connection.close()


def get_user_consent(message, question):
    print(message)
    while True:
        answer = input(question + " [Y/n] ").lower().strip()
        if answer.startswith("y"):
            return True
        elif answer.startswith("n"):
            return False


def proc_to_dict(proc: subprocess.CompletedProcess) -> dict:
    """
    Turns `subprocess.CompletedProcess` into a dictionary.
    """
    result = {}
    attributes = ["args", "returncode"]
    for attr in attributes:
        # all those attributes should be present, but lets be cautious
        try:
            result[attr] = getattr(proc, attr)
        except AttributeError:
            pass

    attributes = ["stdout", "stderr"]
    for attr in attributes:
        # all those attributes should be present, but lets be cautious
        try:
            result[attr] = getattr(proc, attr).decode("utf8")
        except AttributeError:
            pass

    return result


def detect_cards() -> List[CardConnectionDecorator]:
    """
    Detect all the JavaCards, that are currently inserted
    in the readers.
    """
    cards = []
    for reader in readers():
        con = reader.createConnection()
        try:
            # NOTE we are not explicitly disconnecting, so far it seems that it is not
            # an issue
            con.connect()
            cards.append(con)
        except (
            smartcard.Exceptions.NoCardException,
            smartcard.Exceptions.CardConnectionException,
        ):
            pass

    return cards


if __name__ == "__main__":
    app = CommandLineApp()
    app.run()
