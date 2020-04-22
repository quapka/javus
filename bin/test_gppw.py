import pytest

import configparser

from gppw import GlobalPlatformProWrapper
from gppw import Diversifier


def test_gp_prefix():
    config = configparser.ConfigParser()
    config["PATHS"] = {
        "gp.jar": "/path/to/the/gp.jar",
    }
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp.process_config()
    assert gp.gp_prefix() == ["java", "-jar", "/path/to/the/gp.jar", ""]


@pytest.mark.parametrize(
    "div,str_div",
    [
        (Diversifier.NONE, ""),
        (Diversifier.EMV, "--emv"),
        (Diversifier.VISA2, "--visa2"),
    ],
)
def test_gp_prefix_with_diversifier(div, str_div):
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


# def test_detecting_diversifier_from_config():
#     raise ValueError
