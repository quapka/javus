from jcvmutils.functions import is_hex, valid_aid


def test__is_hex__with_valid_value():
    assert is_hex('aa')

def test__is_hex__with_invalid_value():
    assert not is_hex('xa')
