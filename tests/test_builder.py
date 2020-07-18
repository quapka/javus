import pytest

from javus.builder import BaseAttackBuilder
from javus.settings import TESTDIR
from javus.utils import cd


def test_building():
    builder = BaseAttackBuilder(
        gp=None, workdir=TESTDIR / "test_simple_applet", version="jc211"
    )
    proc = builder.execute(BaseAttackBuilder.COMMANDS.build)

    assert 0 == proc.returncode
