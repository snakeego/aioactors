#!/usr/bin/env python
import re
from setuptools import setup, find_packages
from pathlib import Path


def get_version(package: str) -> str:
    result = re.findall(r"^__version__ = ['\"]([^']+)['\"]\r?$", Path(package, '__init__.py').read_text(), re.M)
    if not result:
        raise RuntimeError("Can't find package version")
    return result[0]


def get_readme(fname: str) -> str:
    fp = Path(fname)
    if not fp.exists():
        return str()
    with fp.open(encoding='utf-8') as f:
        return f.read()


setup(
    version=get_version(find_packages(exclude='tests')[0]),
    long_description=get_readme('README.md')
)
