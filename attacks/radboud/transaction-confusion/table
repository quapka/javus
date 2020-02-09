#!/usr/bin/env python

import re
import subprocess as sp

from dominate.util import raw
from jcvmutils.tables import Table, almost, failed, passed

ATTACK_NAME = 'BasicTransaction'
PREPARE1 = 'send INS_PREPARE1'
PREPARE2 = 'send INS_PREPARE2'
READMEM_0000 = 'send INS_READMEM at 0000'
READMEM_0020 = 'send INS_READMEM at 0020'
READMEM_3017 = 'send INS_READMEM at 3017'
READMEM_3201 = 'send INS_READMEM at 3201'
READMEM_4000 = 'send INS_READMEM at 4000'
READMEM_5000 = 'send INS_READMEM at 5000'


def get_read_result(obj):
    # rex = re.compile(r'(A>>.*A0B00000 00.*\nA<<\s*\(.*\)\s+(.*))', re.MULTILINE)
    # read one line after the INS_READ is sent
    rex = re.compile(r'(A>>.*80.* 00.*\n(.*))', re.MULTILINE)
    output = rex.search(obj['stdout'])
    if output:
        out = output.group(2)
        # out = out.replace('\n', '</br>')
        error_code = re.search(r'[A-Z0-9]{4}$', out).group()
        if error_code == '9000':
            if obj['returncode'] == 0:
                ret = passed() + '</br>' + out
            else:
                ret = failed() + '</br>' + out
        else:
            try:
                x = sp.check_output(['jcer', error_code]).decode('utf8').strip()
                err_desc = x.split('\n')[-1]
                ret = '</br>'.join([almost(), error_code, err_desc])
            except sp.CalledProcessError:
                ret = out.strip('<')
        return raw(ret)
    return raw(failed())


class Result(Table):
    ATTACK_NAME = 'BasicTransaction'
    STAGES = {
        PREPARE1: get_read_result,
        PREPARE2: get_read_result,
        READMEM_0000: get_read_result,
        READMEM_0020: get_read_result,
        READMEM_3017: get_read_result,
        READMEM_3201: get_read_result,
        READMEM_4000: get_read_result,
        READMEM_5000: get_read_result,
    }

if __name__ == '__main__':
    res = Result()
    print(res.run())
