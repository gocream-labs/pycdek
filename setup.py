#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from setuptools import find_packages
from setuptools import setup


long_description = '\n'.join([
    open(Path(__file__).parent / 'README.md').read(),
    # open(Path(__file__).parent / 'CHANGELOG.md').read()
])

setup(
    name = 'pycdek',
    url = 'https://gitlab.com/gocream/pycdek.git',
    version = __import__('pycdek').version,
    author = 'Gocream',
    author_email = 'dd@manin.space',
    description = 'python wrapper for cdek api v2.0',
    license = 'GNU GPL v3',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'requests==2.22.0',
        'pyjwt==1.7.1',
    ],
    long_description = long_description,
    platforms = 'All',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Natural Language :: Russian',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
