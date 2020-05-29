from jsec.utils import load_versions
from jsec.utils import JCVersion
from jsec.utils import SDKVersion
import pytest
from typing import Optional

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
            ("0000", "0.0"),
            ("0100", "1.0"),
            ("0202", "2.2"),
            ("0201", "2.1"),
            ("0300", "3.0"),
        ],
    )
    def test___str__(self, version: str, string: str):
        jcversion = JCVersion.from_str(version)
        assert str(jcversion) == string

    def test_comparing_version(self):
        pass


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
