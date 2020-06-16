import pytest

from jsec.card import CardState


def test___parse_raw__with_correct_pkg():
    raw = """
    PKG: A00000006303010C02 (LOADED)
    """
    state = CardState(raw)
    state._parse_raw()
    assert state._items == [
        {
            "PKG": {
                "AID": "A00000006303010C02",
                "STATE": "LOADED",
                "ITEMS": {"Privs": [], "Version": [], "Applet": [],},
            }
        }
    ]


def test___parse_raw__with_multiple_entries():
    raw = """
    ISD: A000000003000000 (OP_READY)
         Privs:   SecurityDomain, CardLock, CardTerminate, CardReset, CVMManagement

    PKG: A00000006303010C01 (LOADED)
         Version: 0.0
         Applet:  A00000006303010C0101
    """
    state = CardState(raw)
    state._parse_raw()
    expected = [
        {
            "ISD": {
                "AID": "A000000003000000",
                "STATE": "OP_READY",
                "ITEMS": {
                    "Privs": [
                        "SecurityDomain",
                        "CardLock",
                        "CardTerminate",
                        "CardReset",
                        "CVMManagement",
                    ],
                    "Version": [],
                    "Applet": [],
                },
            },
        },
        {
            "PKG": {
                "AID": "A00000006303010C01",
                "STATE": "LOADED",
                "ITEMS": {
                    "Privs": [],
                    "Version": ["0.0"],
                    "Applet": ["A00000006303010C0101"],
                },
            },
        },
    ]

    assert state._items == expected


def test__process__():
    raw = """
    ISD: A000000003000000 (OP_READY)
         Privs:   SecurityDomain, CardLock, CardTerminate, CardReset, CVMManagement

    PKG: A00000006303010C01 (LOADED)
         Version: 0.0
         Applet:  A00000006303010C0101
    """
    state = CardState(raw)
    state.process()
    isds = [
        {
            "ISD": {
                "AID": "A000000003000000",
                "STATE": "OP_READY",
                "ITEMS": {
                    "Privs": [
                        "SecurityDomain",
                        "CardLock",
                        "CardTerminate",
                        "CardReset",
                        "CVMManagement",
                    ],
                    "Version": [],
                    "Applet": [],
                },
            },
        }
    ]
    pkgs = [
        {
            "PKG": {
                "AID": "A00000006303010C01",
                "STATE": "LOADED",
                "ITEMS": {
                    "Privs": [],
                    "Version": ["0.0"],
                    "Applet": ["A00000006303010C0101"],
                },
            },
        },
    ]

    assert state.isds == isds
    assert state.pkgs == pkgs
    assert state.applets == []


def test__get_all_aids__():
    raw = """
    ISD: A000000003000000 (OP_READY)
         Privs:   SecurityDomain, CardLock, CardTerminate, CardReset, CVMManagement

    PKG: A00000006303010C01 (LOADED)
         Version: 0.0
         Applet:  A00000006303010C0101
    """
    state = CardState(raw)
    state.process()

    assert state.get_all_aids() == [
        "A000000003000000",
        "A00000006303010C01",
        "A00000006303010C0101",
    ]


# TODO fix naming
def test__get_all_aids__2():
    raw = """
# Warning: no keys given, using default test key 404142434445464748494A4B4C4D4E4F
ISD: A000000003000000 (OP_READY)
     Privs:   SecurityDomain, CardLock, CardTerminate, CardReset, CVMManagement

APP: A00000006303010C0101 (SELECTABLE)
     Privs:

PKG: 0011223344 (LOADED)
     Version: 0.0
     Applet:  0011223344AABB
"""
    state = CardState(raw)
    state.process()
    assert "0011223344AABB" in state.get_all_aids()
