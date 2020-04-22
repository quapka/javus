import pytest

import configparser

from gpp import GlobalPlatformProWrapper


def test_gp_prefix():
    config = configparser.ConfigParser()
    config["PATHS"] = {
        "gp.jar": "/path/to/the/gp.jar",
    }
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp.process_config()
    assert gp.gp_prefix() == [
        "java",
        "-jar",
        "/path/to/the/gp.jar",
    ]


# def test_detecting_diversifier_from_config():
#     raise ValueError
