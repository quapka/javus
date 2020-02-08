import argparse
import logging

import dominate
import pymongo
from dominate.tags import body, caption, link, table, tbody, td, th, tr
from dominate.util import raw

from .utils import CommandLineApp

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

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
    if obj['returncode'] == 0:
        return raw(passed())
    return raw(failed())


CARD_NAME = 'card-name'
INSTALL = 'installation'
UNINSTALL = 'uninstallation'

class Table(CommandLineApp):
    APP_DESCRIPTION = 'Script for creating HTML tables from different attack scenarios'
    ATTACK_NAME = None
    STAGES = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_file = None
        self._STAGES = None
        self.doc = dominate.document(title=self.ATTACK_NAME + ' attack')
        with self.doc.head:
            link(rel='stylesheet', href='../../../tables/stylesheet.css')

        self.body = self.doc.add(body())
        self.table = self.body.add(table())
        self.tbody = self.table.add(tbody())


    def add_options(self):
        super().add_options()
        self.parser.add_argument(
            '-o', '--output-file',
            help='A file to save the output html to',
            type=str,
        )

    def parse_options(self):
        super().parse_options()
        if self.args.output_file is not None:
            self.output_file = self.args.output_file

    def build_stages(self):
        self._STAGES = {
            INSTALL: get_install_result,
        }
        self._STAGES.update(self.STAGES)
        self._STAGES.update({
            UNINSTALL: get_uninstall_result,
        })

    def run(self):
        self.build_stages()
        with self.tbody:
            caption(self.ATTACK_NAME)
            header_row = tr()
            header_row += th(CARD_NAME)
            for stage_name in self._STAGES.keys():
                header_row += th(stage_name)

            for card_name in 'ABCDEFGHI':
                desc = {
                    'card-name': card_name,
                    'attack-name': self.ATTACK_NAME,
                }

                last_attack = commands.find_one(
                    filter=desc,
                    sort=[('timestamp', pymongo.DESCENDING)]
                )
                if last_attack is None:
                    continue

                last_attack_id = last_attack['attack-id']
                if last_attack_id is None:
                    continue


                row = tr()
                row += td(card_name)
                for stage, perform  in self._STAGES.items():
                    desc = {
                        'card-name': card_name,
                        'attack-id':last_attack_id,
                        'stage': stage,
                    }
                    msg = 'Trying to recover object for'
                    msg += 'card-name: {}'.format(desc['card-name'])
                    msg += 'attack-id: {}'.format(desc['attack-id'])
                    msg += 'stage: {}'.format(desc['stage'])
                    log.debug(msg)
                    obj = commands.find_one(desc)
                    if obj is None:
                        raise ValueError('No object retrieved!')
                    row += td(perform(obj))

        return self.doc.render()
