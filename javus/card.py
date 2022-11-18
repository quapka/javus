import re


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
