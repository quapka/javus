import pytest

import configparser

from gppw import GlobalPlatformProWrapper
from gppw import Diversifier


def test__gp_prefix__from_config():
    config = configparser.ConfigParser()
    config["PATHS"] = {
        "gp.jar": "/path/to/the/gp.jar",
    }
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    gp.process_config()
    assert gp.gp_prefix() == ["java", "-jar", "/path/to/the/gp.jar", ""]


def test__gp_prefix__when_missing_in_config():
    config = configparser.ConfigParser()
    config["PATHS"] = {}
    gp = GlobalPlatformProWrapper(config=config, dry_run=True)
    with pytest.raises(RuntimeError):
        gp.process_config()


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

# FIXME should be reimplemented as pytest check rather


@pytest.mark.live
class TestLive:
    def setup_method(self, method):
        self.config = configparser.ConfigParser()
        # FIXME the path needs to be loaded dynamically
        self.config["PATHS"] = {
            "gp.jar": "/home/qup/projects/fi/crocs/GlobalPlatformPro/gp.jar",
        }

    @pytest.mark.skip("Takes too long")
    def test_for_specific_gp_version(self):
        gp = GlobalPlatformProWrapper(config=self.config, dry_run=False)
        gp.process_config()

        gp.read_gp_version()
        assert gp.version == "GlobalPlatformPro v20.01.23-0-g5ad373b"

    def test_that_gp_is_working(self):
        gp = GlobalPlatformProWrapper(config=self.config, dry_run=False)
        gp.process_config()

        gp.verify_gp()
        assert gp.works == True
