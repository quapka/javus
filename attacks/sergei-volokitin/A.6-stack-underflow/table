#!/usr/bin/env python

import re
import subprocess as sp

from dominate.util import raw
from jcvmutils.tables import Table, almost, failed, passed

READ = 'send INS_READ'


def get_read_result(obj):
    # read one line after the INS_READ is sent
    rex = re.compile(r'(A>>.*A0B0.* 00.*\n(.*))', re.MULTILINE)
    output = rex.search(obj['stdout'])
    if output:
        out = output.group(2)
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
    ATTACK_NAME = 'StackUnderflow'
    STAGES = {
        READ:  get_read_result,
    }

if __name__ == '__main__':
    res = Result()
    print(res.run())
