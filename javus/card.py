import logging
import re
import io

from dataclasses import dataclass


log = logging.getLogger(__file__)
# TODO add handler for printing
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class CardState:
    r"""Basically a parsed output from `gp --list`"""

    def __init__(self, raw: str):
        self.raw = raw
        self.isds = []
        self.pkgs = []
        self.applets = []
        self._items = None
        self.parseable = False

    def _parse_raw(self):
        if self._items is not None:
            # cannot parse again!
            return
        self._items = []

        # fmt: off
        tag = re.compile(
            r"(?P<type>ISD|APP|PKG):\s*"
            r"(?P<aid>[A-Z0-9]+)\s*"
            r"\((?P<state>\w+)\)"
        )
        # TODO there have been things added!
        prop = re.compile(
            r"(?P<name>Privs|Version|Applet):\s*"
            r"(?P<value>.*)"
        )
        # fmt: on

        item = {}
        for line in self.raw.strip().split("\n"):
            line = line.strip()

            if not line:
                continue

            tag_match = tag.match(line)
            if tag_match is not None:
                item = {}
                _type = tag_match.group("type")
                aid = tag_match.group("aid")
                state = tag_match.group("state")

                item[_type] = {
                    "AID": aid,
                    "STATE": state,
                    "ITEMS": {"Privs": [], "Version": [], "Applet": []},
                }
                self._items.append(item)
                continue

            prop_match = prop.match(line)
            if prop_match is not None:
                name = prop_match.group("name")
                value = prop_match.group("value")
                if name == "Privs":
                    values = [x.strip() for x in value.split(",")]
                    item[_type]["ITEMS"][name].extend(values)
                else:
                    item[_type]["ITEMS"][name].append(value)

    def process(self):
        # parse the raw output of `gp --list`
        try:
            self._parse_raw()
            self.parseable = True
        except Exception:
            log.warning("The card state coult not be parsed properly")
            self.parseable = False

        # FIXME the next few lines are ugly, but will do for now
        for item in self._items:
            if list(item.keys()) == ["APP"]:
                self.applets.append(item)
            if list(item.keys()) == ["PKG"]:
                self.pkgs.append(item)
            if list(item.keys()) == ["ISD"]:
                self.isds.append(item)

    def get_all_aids(self) -> list:
        aids = []
        for item in self.isds:
            try:
                aids.append(item["ISD"]["AID"])
            except KeyError:
                pass

        for item in self.pkgs:
            try:
                aids.append(item["PKG"]["AID"])
            except KeyError:
                pass

            # FIXME this might not work for multiple applets
            aids.extend(item["PKG"]["ITEMS"]["Applet"])

        for item in self.applets:
            try:
                aids.append(item["AID"])
            except KeyError:
                pass

        return aids


class Card:
    # object representing a card during the analysis
    # basically a card can go from one state to another if a GlobalPlatformCall is performed on it. E.g. listing, installing etc.
    # Being defensies and cautious we can, hopefully log each weird behaviour
    # TODO
    # install an applet
    # execute applet/attack steps
    def __init__(self, gp: "GlobalPlatformProWrapper"):
        self.states = None
        self.current_state = None
        self.gp = gp
        self.jcversion = None
        self.atr = None
        self.reader = None
        self.cplc = None

    def add_state(self, state: CardState):
        r"""Add CardState to the list of states"""
        if self.states is None:
            self.states = [state]
        else:
            self.states.append(state)

        self.current_state = state

    def get_current_aids(self) -> list:
        r"""Get a list of AIDs of the current state"""
        if self.current_state is None:
            self.current_state = self.gp._save_state()

        return self.current_state.get_all_aids()

    def get_report(self) -> dict:
        smartcard_link = "https://smartcard-atr.apdu.fr/parse?ATR=%s" % str(
            self.atr
        ).replace(" ", "")

        report = {
            "jcversion": str(self.jcversion),
            "atr": str(self.atr),
            "smartcard-atr-link": smartcard_link,
            "reader": self.reader,
        }
        return report


@dataclass
class CPLC:
    """Card Production Life Cycle (CPLC)"""

    # sourced from:
    # https://github.com/martinpaljak/GlobalPlatformPro/blob/2da8e65b72e54a510ca8d583a2a141e4092cabcd/library/src/main/java/pro/javacard/gp/GPData.java#LL457
    # ICFabricator(2),
    # ICType(2),
    # OperatingSystemID(2),
    # OperatingSystemReleaseDate(2),
    # OperatingSystemReleaseLevel(2),
    # ICFabricationDate(2),
    # ICSerialNumber(4),
    # ICBatchIdentifier(2),
    # ICModuleFabricator(2),
    # ICModulePackagingDate(2),
    # ICCManufacturer(2),
    # ICEmbeddingDate(2),
    # ICPrePersonalizer(2),
    # ICPrePersonalizationEquipmentDate(2),
    # ICPrePersonalizationEquipmentID(4),
    # ICPersonalizer(2),
    # ICPersonalizationDate(2),
    # ICPersonalizationEquipmentID(4);

    prefix: str  # number of bytes 3
    ICFabricator: str  # number of bytes: 2
    ICType: str  # number of bytes: 2
    OperatingSystemID: str  # number of bytes: 2
    OperatingSystemReleaseDate: str  # number of bytes: 2
    OperatingSystemReleaseLevel: str  # number of bytes: 2
    ICFabricationDate: str  # number of bytes: 2
    ICSerialNumber: str  # number of bytes: 4
    ICBatchIdentifier: str  # number of bytes: 2
    ICModuleFabricator: str  # number of bytes: 2
    ICModulePackagingDate: str  # number of bytes: 2
    ICCManufacturer: str  # number of bytes: 2
    ICEmbeddingDate: str  # number of bytes: 2
    ICPrePersonalizer: str  # number of bytes: 2
    ICPrePersonalizationEquipmentDate: str  # number of bytes: 2
    ICPrePersonalizationEquipmentID: str  # number of bytes: 4
    ICPersonalizer: str  # number of bytes: 2
    ICPersonalizationDate: str  # number of bytes: 2
    ICPersonalizationEquipmentID: str  # number of bytes: 4

    APDU = [0x80, 0xCA, 0x9F, 0x7F]

    @classmethod
    def parse(cls, stream: io.BytesIO) -> "CPLC":
        prefix = stream.read(3)
        # NOTE: this is the prefix I was seeing, but I do not know whether it is standardized
        # and/or expected
        expected_prefix = bytes.fromhex("9F7F2A")
        if prefix != expected_prefix:
            log.info(
                "The received CPLC prefix '%s' was not the expected '%s'",
                prefix,
                expected_prefix,
            )

        prefix = prefix.hex()

        ICFabricator = stream.read(2).hex()
        ICType = stream.read(2).hex()
        OperatingSystemID = stream.read(2).hex()
        OperatingSystemReleaseDate = stream.read(2).hex()
        OperatingSystemReleaseLevel = stream.read(2).hex()
        ICFabricationDate = stream.read(2).hex()
        ICSerialNumber = stream.read(4).hex()
        ICBatchIdentifier = stream.read(2).hex()
        ICModuleFabricator = stream.read(2).hex()
        ICModulePackagingDate = stream.read(2).hex()
        ICCManufacturer = stream.read(2).hex()
        ICEmbeddingDate = stream.read(2).hex()
        ICPrePersonalizer = stream.read(2).hex()
        ICPrePersonalizationEquipmentDate = stream.read(2).hex()
        ICPrePersonalizationEquipmentID = stream.read(4).hex()
        ICPersonalizer = stream.read(2).hex()
        ICPersonalizationDate = stream.read(2).hex()
        ICPersonalizationEquipmentID = stream.read(4).hex()

        return CPLC(
            prefix=prefix,
            ICFabricator=ICFabricator,
            ICType=ICType,
            OperatingSystemID=OperatingSystemID,
            OperatingSystemReleaseDate=OperatingSystemReleaseDate,
            OperatingSystemReleaseLevel=OperatingSystemReleaseLevel,
            ICFabricationDate=ICFabricationDate,
            ICSerialNumber=ICSerialNumber,
            ICBatchIdentifier=ICBatchIdentifier,
            ICModuleFabricator=ICModuleFabricator,
            ICModulePackagingDate=ICModulePackagingDate,
            ICCManufacturer=ICCManufacturer,
            ICEmbeddingDate=ICEmbeddingDate,
            ICPrePersonalizer=ICPrePersonalizer,
            ICPrePersonalizationEquipmentDate=ICPrePersonalizationEquipmentDate,
            ICPrePersonalizationEquipmentID=ICPrePersonalizationEquipmentID,
            ICPersonalizer=ICPersonalizer,
            ICPersonalizationDate=ICPersonalizationDate,
            ICPersonalizationEquipmentID=ICPersonalizationEquipmentID,
        )
