#!/usr/bin/env python

from setuptools import setup

setup(
    # FIXME name?
    name="javus",
    version="0.1.0",
    # TODO Does it match the diploma thesis name?
    description="JavaCard Vulnerability Scanner",
    author="Jan Kvapil",
    # FIXME create an e-mail address for this project
    author_email="",
    # upload it to PYPI?
    url="",
    packages=["javus"],
    # TODO there will be scripts
    scripts=["scripts/javus", "scripts/builder"],
    # TODO add package_data and/or data_files
    # package_data={"javus": ["data/jcversion/jcversion.py"]},
    include_package_data=True,
    # TODO figure out testing with disutils
)
