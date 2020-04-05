#!/usr/bin/env python3

import re
import sys


def load(filepath):
    with open(filepath, 'r') as f:
        data = [x.strip() for x in f.readlines()]

    return data

def warn_about_single_hex(lines):
    single_hex = re.compile(r'0x.[^a-zA-Z0-9]')
    # import pudb; pudb.set_trace()
    for i, line in enumerate(lines):
        if single_hex.findall(line):
            raise ValueError('Single hex value on line {}'.format(i + 1))

def remove_empty_lines(lines):
    return list(filter(lambda x: True if x else False, lines))

def print_lines(lines):
    for line in lines:
        print(line)

def remove_comments(lines):
    return list(filter(lambda x: not x.startswith('//'), lines))

def remove_hex_tag(lines):
    return [x.replace('0x', '') for x in lines]

def remove_spaces(lines):
    return [re.sub(r'\s', '', x) for x in lines]

def remove_semicolon(lines):
    return [x.replace(';', '') for x in lines]

def remove_non_hex(lines):
    def is_hex(value):
        try:
            bytes.fromhex(value)
            return True
        except ValueError:
            return False

    return list(filter(is_hex, lines))



def main(filepath):
    lines = load(filepath)
    warn_about_single_hex(lines)

    lines = remove_empty_lines(lines)
    lines = remove_comments(lines)
    lines = remove_hex_tag(lines)
    lines = remove_spaces(lines)
    lines = remove_semicolon(lines)
    lines = remove_non_hex(lines)

    print_lines(lines)


if __name__ == '__main__':
    main(sys.argv[1])
