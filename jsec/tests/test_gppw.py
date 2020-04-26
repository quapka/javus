import pytest


# FIXME prevent running live tests in case there is a card in the system
import configparser

from jsec.jsec.gppw import GlobalPlatformProWrapper
from jsec.jsec.gppw import Diversifier


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
    "div,str_div",
    [
        (Diversifier.NONE, ""),
        (Diversifier.EMV, "--emv"),
        (Diversifier.VISA2, "--visa2"),
    ],
)
def test_add_diversifier_flag_to_gp_prefix(div, str_div):
    config = configparser.ConfigParser()
    config["PATHS"] = {
        "gp.jar": "/path/to/the/gp.jar",
    }
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp.process_config()
    gp.diversifier = div
    assert gp.gp_prefix() == [
        "java",
        "-jar",
        "/path/to/the/gp.jar",
        str_div,
    ]


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
    gp.atr = atr
    gp.infer_diversifier()
    assert gp.diversifier == Diversifier.EMV
