#!/usr/bin/env python

import argparse

import pymongo

# import utils.CommandLineApp
from utils import CommandLineApp

# steps
# connect to mongo
# retrieve results
# go through steps and mark them as (success, failure, other)
# draw the final table


# pylint: disable=C0103
# pylint: disable=E0602
client = pymongo.MongoClient('mongodb://localhost:27017')
database = client.get_database('card-analysis')

commands = database.commands
TICK_SIGN = '&#10004;'
CROSS_SIGN = '&#10060;'
CIRCLE_SIGN = '&#9898;'

def green(x):
    return '<span style="color: green;">{}</span>'.format(x)

def red(x):
    return '<span style="color: red;">{}</span>'.format(x)

def orange(x):
    return '<span style="color: orange;">{}</span>'.format(x)

def passed():
    return green(TICK_SIGN)

def failed():
    return red(CROSS_SIGN)

def almost():
    return orange(CIRCLE_SIGN)

def get_install_result(obj):
    if obj['returncode'] == 0:
        return raw(passed())
    last_two = obj['stderr'].strip().split('\n')[-2:]
    return raw(failed() + '</br>' + '</br>'.join(last_two))

def get_uninstall_result(obj):
    return get_install_result(obj)
    # if obj['returncode'] == 0:
    #     return raw(passed())
    # last_two = obj['stderr'].strip().split('\n')[-2:]
    # return raw(failed() + '</br>' + '</br>'.join(last_two))

INSTALL = 'install'
UNISNTALL = 'uninstall'

class Table(CommandLineApp):
    APP_DESCRIPTION = 'Script for creating HTML tables from different attack scenarios'
    STAGES = [
        INSTALL,
        UNINSTALL,
    ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_file = None
        self.doc = dominate.document(title=ATTACK_NAME + ' attack')
        with doc.head:
            link(rel='stylesheet', href='../../../tables/stylesheet.css')

        body = doc.add(body())
        table = body.add(table())
        tbody = table.add(tbody())


    def add_options(self):
        super().add_options()
        self.parser.add_argument(
            '-o', '--output-file',
            help='A file to save the output html to',
            type=str,
        )

    def parse_options(self):
        super().parse_options()
        if args.output_file is not None:
            self.output_file = args.output_file

    def run(self):
        with tbody:
            caption = caption(ATTACK_NAME)
            header_row = tr()
            for stage in columns:
                header_row += th(stage)
            for card_name in 'ABCDEFGHI':
                desc = {
                    'card-name': card_name,
                    'attack-name': ATTACK_NAME,
                }

                last_attack_id = commands.find_one(
                    filter=desc,
                    sort=[('timestamp', pymongo.DESCENDING)]
                )['attack-id']

                row = tr()
                for stage in columns:
                    if stage == CARD_NAME:
                        row += td(card_name)
                    elif stage == INSTALL:
                        obj = commands.find_one({
                            'card-name': card_name,
                            'attack-id':last_attack_id,
                            'stage': INSTALL,
                        })
                        if obj is None:
                            continue
                        row += td(get_install_result(obj))
                    elif stage == UNINSTALL:
                        obj = commands.find_one({
                            'card-name': card_name,
                            'attack-id':last_attack_id,
                            'stage': UNINSTALL,
                        })
                        row += td(get_uninstall_result(obj))
                    else:
                        obj = commands.find_one({
                            'card-name': card_name,
                            'attack-id':last_attack_id,
                            'stage': stage,
                        })
                        row += td(get_read_result(obj))


if __name__ == '__main__':
    table = Table()
    table.run()
