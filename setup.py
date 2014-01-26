#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re
import os
import codecs


# Borrowed from
# https://github.com/jezdez/django_compressor/blob/develop/setup.py
def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='orchard',
    version=find_version("orchard", "__init__.py"),
    description='',
    url='https://orchardup.com',
    author='Orchard Laboratories Ltd.',
    author_email='hello@orchardup.com',
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    install_requires=[
        'docopt==0.6.1',
        'requests==2.0.1',
        'six==1.3.0',
        'texttable==0.8.1',
        'websocket-client==0.11.0',
    ],
    entry_points="""
    [console_scripts]
    orchard=orchard.cli:main
    """,
)
