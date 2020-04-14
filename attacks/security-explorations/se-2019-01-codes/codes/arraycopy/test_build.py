#!/usr/bin/env python

import configparser
import pytest
import os
import subprocess as sp

BUILD_DIR = 'build'

def load_versions():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['BUILD']['versions'].split(',')

# def test_emptiness():
#     versions = load_versions()
#     for ver in versions:
#         _test_build_dir(ver)

# TODO refactor to make it dynamic
# class TestEmptinessOfBuildFolder():

expected_files = [('build/jc211', ['com'], ['vulns.jar', 'applets.jar']),
 ('build/jc211/com', ['se'], []),
 ('build/jc211/com/se', ['vulns', 'applets'], []),
 ('build/jc211/com/se/vulns', ['javacard'], []),
 ('build/jc211/com/se/vulns/javacard',
  [],
  ['vulns.exp', 'vulns.cap', 'vulns.jca']),
 ('build/jc211/com/se/applets', ['javacard'], []),
 ('build/jc211/com/se/applets/javacard',
  [],
  ['applets.cap', 'applets.exp', 'applets.jca'])]


@pytest.mark.parametrize(
        'ver', load_versions()
    )
def test_ant_clean_versions(ver):
    target = ver + '-clean'
    sp.check_output(['ant', target])
    assert ver not in os.listdir(BUILD_DIR)

@pytest.mark.parametrize(
        'ver', load_versions()
    )
def test_ant_build_versions(ver):
    sp.check_output(['ant', ver])
    ver_dir = os.path.join(BUILD_DIR, ver)

    for path, dirs, files in os.walk(ver_dir):
