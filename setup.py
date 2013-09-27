#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
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
    author='Orchard Laboratories Ltd.',
    packages=['orchard', 'orchard.api', 'orchard.api.models', 'orchard.cli'],
    package_data={},
    include_package_data=True,
    install_requires=[
        'docopt==0.6.1',
        'docker-py==0.2.0-orchard',
        'requests==1.2.3',
        'texttable==0.8.1',
    ],
    dependency_links=[
        'https://github.com/aanand/docker-py/tarball/3af6f8cc040c5b9e94d952519c36eb54130b7008#egg=docker-py-0.2.0-orchard',
    ],
    entry_points="""
    [console_scripts]
    orchard=orchard.cli:main
    """,
)
