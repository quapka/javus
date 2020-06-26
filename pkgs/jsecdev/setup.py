# read the contents of your README file
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="jsecdev",
    version="0.1",
    description="Package containing utilities for the development of jsec, meant to be used only locally",
    long_description=long_description,
    url="#",
    author="Jan Kvapil",
    author_email="408788@mail.muni.cz",
    packages=["jsecdev"],
    scripts=["scripts/jsecdev"],
    include_package_data=True,
    zip_safe=False,
)
