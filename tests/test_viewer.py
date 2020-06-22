import pytest
from jsec.viewer import format_duration


@pytest.mark.parametrize(
    "utc_timestamp, duration",
    [
        ("0", "0ms"),
        ("1", "1s"),
        ("0.123", "123ms"),
        ("59.0", "59s"),
        ("61", "01:01"),
        ("61.013", "01:01.013"),
    ],
)
def test_format_duration(utc_timestamp, duration):
    assert format_duration(utc_timestamp) == duration
