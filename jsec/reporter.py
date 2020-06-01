#!/usr/bin/env python

from abc import ABC, abstractmethod


class AbstractReporter:
    pass


class BaseReporter(AbstractReporter):
    def fetch_results(self):
        pass

    def get_full_report(self):
        pass


if __name__ == "__main__":
    pass
