from jcvmutils.functions import is_hex, valid_aid


def test__is_hex__with_valid_value():
    assert is_hex('aa')

def test__is_hex__with_invalid_value():
    assert not is_hex('xa')

def test__valid_aid__with_short_value():
    # four bytes is not enough
    assert not valid_aid('001122333')

def test__valid_aid__with_long_value():
    # 17 bytes is too much
    assert not valid_aid('001122333445566778899aabbccddeeffaa')

def test__valid_aid__with_valid_value():
    assert valid_aid('0011223344')

def test__valid_aid__with_invalid_value():
    assert not valid_aid('00112233xx')
