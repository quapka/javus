import io
import pytest

from javus.components import ImportComponent, package_info


def test_import_component():
    # Import.cap contents
    # 0000000 0004 010b 0100 a007 0000 6200 0101 000000e 00000000          |...........b..|
    # 0000000e
    import_component_raw = bytes.fromhex("04 00 0b 01 00 01 07 a0  00 00 00 62 01 01")
    stream = io.BytesIO(import_component_raw)
    ic = ImportComponent.parse(stream)

    assert ic.tag == b"\x04"
    assert int.from_bytes(ic.size, byteorder="big") == len(import_component_raw) - (
        len(ic.tag) + len(ic.size)
    )
    assert ic.count == b"\x01"


def test_package_info():
    # take from Import Component example
    package_info_raw = bytes.fromhex("00 01 07 a0 00 00 00 62 01 01")
    stream = io.BytesIO(package_info_raw)

    pi, stream = package_info.parse(stream)

    assert pi.minor_version == b"\x00"
    assert pi.major_version == b"\x01"
    assert pi.AID_length == b"\x07"
    assert pi.AID == bytes.fromhex("a0 00 00 00 62 01 01")


def test_import_component_parse_and_collect():
    import_component_raw = bytes.fromhex("04 00 0b 01 00 01 07 a0  00 00 00 62 01 01")
    stream = io.BytesIO(import_component_raw)
    ic = ImportComponent.parse(stream)

    assert import_component_raw == ic.collect()


@pytest.mark.skip("Not implemented")
def test_package():
    raise NotImplemented


@pytest.mark.skip("Not implemented")
def test_header_component():
    raise NotImplemented
