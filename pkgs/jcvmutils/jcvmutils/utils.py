#!/usr/bin/env python3
import argparse
import logging
import os
import re
import subprocess as sp
import sys

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

LOG_LEVELS = [
    logging.DEBUG, logging.INFO, logging.WARNING,
    logging.ERROR, logging.CRITICAL
]

class CommandLineApp():
    '''
    Template for Python command line applications.
    '''
    APP_DESCRIPTION = None

    def __init__(self):
        self.verbosity = logging.ERROR
        self.args = None

        self.parser = argparse.ArgumentParser(
                description=self.APP_DESCRIPTION,
        )
        self.add_options()
        self.parse_options()

        log.setLevel(self.verbosity)
        log.debug('Logging level changed')

    def add_options(self):
        levels = ', '.join([str(lvl) for lvl in LOG_LEVELS])
        self.parser.add_argument(
            '-v', '--verbose',
            help='Set the verbosity {' + levels + '}',
            type=self.validate_verbosity,
        )

    def validate_verbosity(self, value):
        try:
            value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError('verbosity is not and integer')
        if value not in LOG_LEVELS:
            raise argparse.ArgumentTypeError('verbosity level not from expected range')
        return value

    def parse_options(self):
        self.args = self.parser.parse_args()
        if self.args.verbose is not None:
            self.verbosity = self.args.verbose

    def run(self):
        pass

if __name__ == '__main__':
    app = CommandLineApp()
    app.run()
