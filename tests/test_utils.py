from typing import Optional

import pytest

from jsec.utils import JCVersion, SDKVersion, load_versions

# from pytest_mock import mocker

# FIXME depends on external configuration
def test__load_versions__filters_unknown_versions():
    versions = ["not a version", "jc221"]
    assert load_versions(versions) == ["jc221"]


def test__load_versions__sorts_versions_from_newest():
    versions = ["jc221", "jc305u3"]
    assert load_versions(versions) == ["jc305u3", "jc221"]


class TestJCVersion:
    @pytest.mark.parametrize(
        "version,major,minor",
        [
            ("0000", 0, 0),
            ("0100", 1, 0),
            ("0202", 2, 2),
            ("0201", 2, 1),
            ("0300", 3, 0),
        ],
    )
    def test_from_str(self, version: str, major: int, minor: int):
        jcversion = JCVersion.from_str(version)

        assert jcversion.major == major
        assert jcversion.minor == minor

    @pytest.mark.parametrize(
        "version,string",
        [
            ("0000", "JavaCard version: 0.0"),
            ("0100", "JavaCard version: 1.0"),
            ("0202", "JavaCard version: 2.2"),
            ("0201", "JavaCard version: 2.1"),
            ("0300", "JavaCard version: 3.0"),
        ],
    )
    def test___str__(self, version: str, string: str):
        jcversion = JCVersion.from_str(version)
        assert str(jcversion) == string

    @pytest.mark.parametrize(
        "jcversion,exp_sdks",
        [
            ("0200", SDKVersion.from_list("jc202")),
            ("0300", SDKVersion.from_list("jc202,jc300,jc301,jc304")),
            ("0310", SDKVersion.from_list("jc202,jc300,jc301,jc304,jc310b43")),
        ],
    )
    def test_get_sdks(self, mocker, jcversion, exp_sdks):
        # mocking available SDKs
        mocker.patch.object(SDKVersion, "get_available_sdks")
        SDKVersion.get_available_sdks.return_value = SDKVersion.from_list(
            "jc202,jc300,jc301,jc304,jc310b43"
        )

        jcversion = JCVersion.from_str(jcversion)
        sdks = jcversion.get_sdks()
        assert sdks == exp_sdks


class TestSDKVersion:
    @pytest.mark.parametrize(
        "version,major,minor,patch,update,b_value",
        [
            ("jc211", 2, 1, 1, None, None),
            ("jc212", 2, 1, 2, None, None),
            ("jc222", 2, 2, 2, None, None),
            ("jc305u3", 3, 0, 5, 3, None),
            ("jc310b43", 3, 1, 0, None, 43),
        ],
    )
    def test_from_str(
        self,
        version: str,
        major: int,
        minor: int,
        patch: int,
        update: Optional[int],
        b_value: Optional[int],
    ):
        sdkversion = SDKVersion.from_str(version)
        assert sdkversion.major == major
        assert sdkversion.minor == minor
        assert sdkversion.patch == patch
        assert sdkversion.update == update
        assert sdkversion.b_value == b_value

    # FIXME this interacts with real data, but is not really a check
    def test_available_sdks(self):
        available = SDKVersion.get_available_sdks()
        assert SDKVersion.from_str("jc211") == available[0]

    @pytest.mark.parametrize(
        "raw_list,versions",
        [
            ("jc211", [SDKVersion.from_str("jc211")]),
            (
                "jc222,jc310b43",
                [SDKVersion.from_str("jc222"), SDKVersion.from_str("jc310b43")],
            ),
        ],
    )
    def test_from_list(self, raw_list: str, versions: list):
        assert SDKVersion.from_list(raw_list) == versions


# @pytest.mark.parametrize("jcversion,sdks", [("0300", [])])
# def test_infer_sdks_from_jcversion(jcversion: str, sdks: list):
#     jcversion = JCVersion.from_str(jcversion)
#     assert jcversion.get_sdks() == sdks
