#!/usr/bin/env python3

from javus.builder import BaseAttackBuilder
from javus.executor import BaseAttackExecutor
from javus.settings import ATTACKS
from javus.utils import cd


class AttackBuilder(BaseAttackBuilder):
    def _build(self):
        # NOTE the attacks are not build automatically at the moment
        pass


class AttackExecutor(BaseAttackExecutor):
    # NOTE based on the known versions use only <= SDK, aka the ones that should be realistically supported
    pass
