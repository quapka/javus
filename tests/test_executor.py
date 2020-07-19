#!/usr/bin/env python
import configparser
from contextlib import ExitStack as does_not_raise
from pathlib import Path

import pytest

from javus.card import Card
from javus.executor import BaseAttackExecutor
from javus.utils import AttackConfigParser
from javus.gppw import GlobalPlatformProWrapper
import mock


@pytest.mark.skip(reason="Need to be updated for the newer specs")
class TestBaseAttackExecutor:
    def setup_method(self):
        gp_config = configparser.ConfigParser()
        gp_config["PATHS"] = {
            "gp.jar": "/path/to/the/gp.jar",
        }

        self.gp = GlobalPlatformProWrapper(config=gp_config)
        self.path = Path()
        self.card = Card(gp=self.gp)

    @staticmethod
    def _load_test_config(self, *args, **kwargs):
        self.config = AttackConfigParser()
        self.config["BUILD"] = {
            "versions": "jc222",
        }

    @pytest.mark.parametrize(
        "raw_payload,parsed_payload",
        [
            ("", b""),
            ("aa", b"\xaa"),
            ("a a", b"\x0a\x0a"),
            ("0xaa 0xbb \t\n  0xcc", b"\xaa\xbb\xcc"),
            ("0xa 0xbb \t  0xc", b"\x0a\xbb\x0c"),
            # hexadecimal values are assumed
            ("80 60", b"\x80\x60"),
            # but integers are valid as well
            ("110 255", b"\x6e\xff"),
        ],
    )
    def test__parse_payload(self, raw_payload: str, parsed_payload: bytes) -> None:
        with mock.patch.object(
            BaseAttackExecutor, "_load_config", new=self._load_test_config
        ):
            bae = BaseAttackExecutor(card=self.card, gp=self.gp, workdir=self.path)
            assert bae._parse_payload(raw_payload) == parsed_payload

    @pytest.mark.parametrize(
        "raw,cleaned",
        [
            ("", ""),
            ("aa bb", "aa bb"),
            ("aa bb ", "aa bb"),
            (" aa \t \tbb  \t\n cc\t", "aa bb cc"),
            (" a b", "a b"),
        ],
    )
    def test__clean_payload(self, raw: str, cleaned: str) -> None:
        bae = BaseAttackExecutor(card=self.card, gp=self.gp, workdir=self.path)
        assert bae._clean_payload(raw) == cleaned

    @pytest.mark.parametrize(
        "raw, separated",
        [
            ("", []),
            ("0xaa, 0xbb", ["0xaa", "0xbb"]),
            ("0xaa 0xbb", ["0xaa", "0xbb"]),
            ("a a", ["a", "a"]),
        ],
    )
    def test__separate_payload(self, raw: str, separated: str):
        bae = BaseAttackExecutor(card=self.card, gp=self.gp, workdir=self.path)
        assert bae._separate_payload(raw) == separated

    @pytest.mark.parametrize(
        "stage,clean_stage,exception",
        [
            (" ", "", pytest.raises(RuntimeError)),
            (" install \t", "install", does_not_raise()),
            (" \tsend read memory", "send_read_memory", does_not_raise()),
        ],
    )
    def test__create_stage_name(self, stage, clean_stage, exception):
        bae = BaseAttackExecutor(card=self.card, gp=self.gp, workdir=self.path)
        with exception:
            assert bae._create_stage_name(stage) == clean_stage
