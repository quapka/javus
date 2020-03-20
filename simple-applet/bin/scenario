#!/usr/bin/env python

import argparse
import configparser
import os
import subprocess as sp

from PyInquirer import print_json, prompt

CONFIG_FILE = 'config.ini'

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

parser = argparse.ArgumentParser(
    description='Test non-interactive scenarios'
)

parser.add_argument('-i', '--interactive', action='store_true')
parser.add_argument(
        '-c', '--cap',
        default='com.simple-jc212.cap',
     )

args = parser.parse_args()
cap_file = args.cap


gp = [
    'java',
    '-jar',
    os.path.join(os.environ['HOME'], 'projects/GlobalPlatformPro/gp.jar'),
]

def run_command(cmd):
    process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    while process.poll() is None:
        output = process.stdout.readline().decode('utf8')
        if output:
            print(output, end='')
    rc = process.poll()
    print(rc)

def install():
    cmd = gp + [
        '--verbose',
        '--debug',
        '--install',
        cap_file
    ]
    # output = sp.check_output(cmd)
    run_command(cmd)

def uninstall():
    cmd = gp + [
        '--verbose',
        '--debug',
        '--uninstall',
        cap_file
    ]
    # output = sp.check_output(cmd)
    run_command(cmd)

def select():
    aid = config['DEFAULT']['AID']
    select_payload = '00a40400'
    select_payload += '{:02}'.format(len(aid)//2)
    select_payload += aid
    print(select_payload)
    cmd = gp + [
        '--verbose',
        '--debug',
        '--apdu',
        select_payload,
    ]
    # output = sp.check_output(cmd)
    run_command(cmd)

INSTALL = 'install'
SELECT = 'select'
UNINSTALL = 'uninstall'

STEPS = {
    INSTALL: install,
    SELECT: select,
    UNINSTALL: uninstall,
}

questions = [
    {
        'type': 'list',
        'message': 'Which step do you want to perform?',
        'name': 'step',
        'choices': list(STEPS.keys()) + ['exit'],
        },
]

if args.interactive:
    answer = prompt(questions)
    while True:
        if answer['step'] == 'exit':
            break
        STEPS[answer['step']]()

        answer = prompt(questions)
else:
    for step, func in STEPS.items():
        print(step)
        func()
