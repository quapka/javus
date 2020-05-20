import pytest

from jsec.utils import cd
from jsec.builder import Builder
from jsec.settings import TESTDIR


def test_building():
    builder = Builder(workdir=TESTDIR / "test_simple_applet", version="jc211")
    proc = builder.execute(Builder.COMMANDS.build)

    assert 0 == proc.returncode
