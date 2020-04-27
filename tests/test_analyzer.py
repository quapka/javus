import pytest

from jsec.analyzer import CardState


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
