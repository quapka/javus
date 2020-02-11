#!/usr/bin/env python


item = '\\item[{abbr}] {desc}'

def create_item(line):
    abbr, *desc = [x.strip() for x in line.split('-')]
    desc = '-'.join(desc)
    return item.format(abbr=abbr, desc=desc)


def main():
    lines = None
    with open('../abbreviations.md', 'r') as f:
        lines = [x.strip() for x in f.readlines()]

    if not lines:
        raise ValueError('No lines read!')

    for line in lines:
        tex_item = create_item(line)
        print(tex_item)

if __name__ == '__main__':
    main()
