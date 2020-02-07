#!/usr/bin/env python

import argparse

# import dominate
# import pymongo
# from dominate.tags import body, caption, link, table, tbody, td, th, tr
# from dominate.util import raw
# import utils.CommandLineApp
from jcvmutils.tables import Table


class Result(Table):
    APP_DESCRIPTION = 'Script for creating HTML tables from different attack scenarios'
    ATTACK_NAME = 'Test Attack'
    STAGES = {}


if __name__ == '__main__':
    res = Result()
    res.run()
