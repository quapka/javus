import pytest
from jsec.viewer import format_duration, add_whitespace_id


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


@pytest.mark.parametrize(
    "_id",
    [
        ("5ede2f24b69c4aa58f209a71"),
        ("5ede3f4ae7983ce6b81868f2"),
        ("5edfa555327223721fce9a8b"),
        ("5edfb1a58ebd9320dc42d50e"),
        ("5edfbbe291e4823727f4c62e"),
        ("5edfbbf14207c1387a7b7267"),
        ("5edfc44712c3d80d4b9f85d7"),
        ("5edfc594741a40e4fe12fd16"),
        ("5edfc6f429f8cc28f8d0ce97"),
        ("5edfc75f392ee85fd112be1c"),
        ("5ee1f79d513ea7911c3ec4a7"),
        ("5ee1fdee1667196caa667c81"),
        ("5ee203fc3225a7d137c750da"),
        ("5ee22329163233c47831cee6"),
        ("5ee223d1b91ae419621f2fd1"),
        ("5ee2368031d2420572a5e8fe"),
        ("5ee23fd32d2894e2e81f8ae5"),
    ],
)
def test_add_whitespace_id(_id):
    assert add_whitespace_id(_id).replace(" ", "") == _id
