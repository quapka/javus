# read the contents of your README file
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="jcvmutils",
    version="0.1",
    description="Package containing utilities for the analysis of JavaCard Virtual Machine",
    long_description=long_description,
    url="#",
    author="quapka",
    author_email="quapka@gmail.com",
    packages=["jcvmutils"],
    zip_safe=False,
)
