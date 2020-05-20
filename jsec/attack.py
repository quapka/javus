#!/usr/bin/env python
from abc import ABC
from abc import abstractmethod


class Attack(ABC):
    @abstractmethod
    def uniqfy(self):
        # TODO maybe have default aids in config.ini and rewrite only aids.ini
        pass


if __name__ == "__main__":
    pass
