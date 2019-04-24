#!/usr/bin/env python
import re
from setuptools import setup, find_packages
from os import path as op

__version__ = "1.2"

PACKAGES = find_packages(exclude=['tests'])
NAME = PACKAGES[0]

patterns = {
    'version': re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]'),
    'doc': re.compile(r'__doc__ = [\'"]([^\'"]*)[\'"]')
}


def extract(pattern, fname):
    result = ''
    reg = re.compile(patterns[pattern])
    with open(fname, 'r') as fp:
        for line in fp:
            m = reg.match(line)
            if m:
                result = m.group(1)
                break
    if not result:
        raise RuntimeError('Cannot find matched information for pattern {}'.format(pattern))
    return result


def get_readme(fname):
    result = ''
    if op.exists(fname):
        with open(fname, encoding='utf-8') as f:
            result = f.read()
    return result


setup(
    name=NAME,
    packages=PACKAGES,
    version=extract('version', "{}/__init__.py".format(NAME)),
    description=extract('doc', "{}/__init__.py".format(NAME)),
    long_description=get_readme('README.md'),
    install_requires=[]
)
