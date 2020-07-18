# FIXME prevent running live tests in case there is a card in the system
import configparser

import pytest

from javus.gppw import Diversifier, GlobalPlatformProWrapper
from javus.card import Card
from smartcard.ATR import ATR


def test__gp_prefix__from_config():
    config = configparser.ConfigParser()
    config["PATHS"] = {
        "gp.jar": "/path/to/the/gp.jar",
    }
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp.process_config()
    assert gp.gp_prefix() == ["java", "-jar", "/path/to/the/gp.jar"]


def test__gp_prefix__when_missing_in_config():
    config = configparser.ConfigParser()
    config["PATHS"] = {}
    with pytest.raises(RuntimeError):
        gp = GlobalPlatformProWrapper(config=config, dry_run=True)


@pytest.mark.parametrize(
    "div,diversifier_flag",
    [
        (Diversifier.NONE, ""),
        (Diversifier.EMV, "--emv"),
        (Diversifier.VISA2, "--visa2"),
    ],
)
def test_add_diversifier_flag_to_gp_prefix(div, diversifier_flag):
    config = configparser.ConfigParser()
    config["PATHS"] = {
        "gp.jar": "/path/to/the/gp.jar",
    }
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp.process_config()
    gp.diversifier = div

    expected_cmd = [
        "java",
        "-jar",
        "/path/to/the/gp.jar",
    ]
    if diversifier_flag:
        expected_cmd.append(diversifier_flag)

    assert gp.gp_prefix() == expected_cmd


def test_detecting_diversifier_from_config():
    config = configparser.ConfigParser()
    # FIXME the path needs to be loaded dynamically
    # even in tests!
    config["PATHS"] = {
        "gp.jar": "/home/qup/projects/fi/crocs/GlobalPlatformPro/gp.jar",
    }
    config["CARD"] = {
        "diversifier": Diversifier.EMV.name,
    }

    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp.load_diversifier_from_config()
    assert gp.diversifier == Diversifier.EMV


def test_detecting_diversifier_from_card_types():
    config = configparser.ConfigParser()
    config["PATHS"] = {"gp.jar": ""}
    types = configparser.ConfigParser()
    atr = "3b fe 18 00 00 80 31 fe 45 53 43 45 36 30 2d 43 44 30 38 31 2d 6e 46 a9"
    types[atr] = {
        "diversifier": "EMV",
    }

    gp = GlobalPlatformProWrapper(config=config, card_types=types, dry_run=True)
    card = Card(gp=gp)
    card.atr = ATR([int(x, 16) for x in atr.split()])
    gp.card = card
    gp.infer_diversifier()
    assert gp.diversifier == Diversifier.EMV


# TODO move to class test
def test___parse_gp_dump_file__():
    # raw is the content of a --dump file from GlobalPlatformPro
    raw = """# Generated on Mon, 4 May 2020 17:31:15 +0200 by apdu4j/19.05.08.1-0-gfbddd95-dirty
# Using Alcor Micro AU9560 00 00
# ATR: 3BFC180000813180459067464A01002005000000004E
# PROTOCOL: T=1
#
# Sent
00A40400070011223344AACC
# Received in 14ms
6A82
# Sent
8001000000
# Received in 7ms
6D00
# Sent
00A4040000
# Received in 25ms
6F5C8408A000000003000000A550734A06072A864886FC6B01600C060A2A864886FC6B02020101630906072A864886FC6B03640B06092A864886FC6B040255650B06092B8510864864020103660C060A2B060104012A026E01029F6501FF9000
"""
    config = configparser.ConfigParser()
    config["PATHS"] = {
        "gp.jar": "/path/to/the/gp.jar",
    }
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp = GlobalPlatformProWrapper(config=config)

    assert gp._parse_gp_dump_file(raw) == {
        "00A40400070011223344AACC": {"payload": "", "status": "6A82"},
        "8001000000": {"payload": "", "status": "6D00"},
        "00A4040000": {
            "payload": (
                "6F5C8408A000000003000000A550734A06072A864886FC6B01600C060A2A864886FC6B0202"
                "0101630906072A864886FC6B03640B06092A864886FC6B040255650B06092B851086486402"
                "0103660C060A2B060104012A026E01029F6501FF"
            ),
            "status": "9000",
        },
    }
