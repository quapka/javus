#!/usr/bin/env python
from abc import ABC
from abc import abstractmethod


class Attack(ABC):
    def __init__(self, workdir):
        pass

    @abstractmethod
    def uniqfy(self):
        pass


if __name__ == "__main__":
    pass
