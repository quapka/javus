#!/usr/bin/env python3
import argparse
import logging
import os
import re
import subprocess as sp
import sys
import time

import pymongo

from contextlib import contextmanager

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# FIXME use enum and allow 'debug' as value for --verbose
LOG_LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
]


class Error(enum.Enum):
    UNSUPPORTED_PYTHON_VERSION = -1


# kudos to: https://medium.com/@ramojol/python-context-managers-and-the-with-statement-8f53d4d9f87
class MongoConnection(object):
    def __init__(
        self,
        host="localhost",
        port="27017",
        database="card-analysis",
        collation="commands",
    ):
        self.host = host
        self.port = port
        self.connection = None
        self.db_name = database
        self.collation_name = collation

    def __enter__(self, *args, **kwargs):
        conn_str = f"mongodb://{self.host}:{self.port}"
        log.debug("Starting the connection with %s", conn_str)

        self.connection = pymongo.MongoClient(conn_str)
        self.db = self.connection[self.db_name]
        self.col = self.db[self.collation_name]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug("Closing the connection to the database")
        self.connection.close()


class Timer(object):
    # naive timer, but to get at least an idea
    def __init__(self):
        self.start = None
        self.end = None
        self.duration = None

    def __enter__(self, *args, **kwargs):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.duration = self.end - self.start


class CommandLineApp(object):
    """
    Template for Python command line applications.
    """

    APP_DESCRIPTION = None

    def __init__(self):
        self.verbosity = logging.ERROR
        self.args = None

        self.parser = argparse.ArgumentParser(description=self.APP_DESCRIPTION,)
        self.add_options()
        self.parse_options()

        self.setup_logging()

    def setup_logging(self, target_log=None):
        if target_log is None:
            target_log = log
        old = logging.getLevelName(target_log.level)
        new = logging.getLevelName(self.verbosity)
        target_log.setLevel(self.verbosity)
        log.debug(
            "logging level for %s changed from %s to %s ", target_log.name, old, new
        )

    def add_options(self):
        levels = ", ".join([str(lvl) for lvl in LOG_LEVELS])
        self.parser.add_argument(
            "-v",
            "--verbose",
            help="Set the verbosity {" + levels + "}",
            type=self.validate_verbosity,
        )

    def validate_verbosity(self, value):
        # FIXME use enum.Enum - already in gppw.py
        try:
            value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("verbosity is not an integer")
        if value not in LOG_LEVELS:
            raise argparse.ArgumentTypeError("verbosity level not from expected range")
        return value

    def parse_options(self):
        self.args = self.parser.parse_args()
        if self.args.verbose is not None:
            self.verbosity = self.args.verbose

    def run(self):
        raise NotImplementedError("The method 'run' has not bee implemented!")


# kudos to:
# https://stackoverflow.com/questions/431684/how-do-i-change-the-working-directory-in-python/13197763#13197763
@contextmanager
def cd(new_path):
    old_path = os.getcwd()
    log.debug("Save old path: %s", old_path)
    try:
        log.debug("Change directory to: %s", new_path)
        # no yield for now, as there is no need for additional information
        os.chdir(new_path)
        yield old_path
    finally:
        # the old directory might also be remove, however there isn't
        # good and logical thing to do, so in that case the exception will be
        # thrown
        # FIXME Ceesjan taught to not to use format in logging!!!
        log.debug("Switch back to old path: %s", old_path)
        os.chdir(old_path)


if __name__ == "__main__":
    app = CommandLineApp()
    app.run()
