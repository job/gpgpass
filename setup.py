#!/usr/bin/env python
#
#   Copyright 2014 Rick van den Hof
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

version = "0.1"

import codecs
import os
import sys

from pip.req import parse_requirements
from setuptools import setup, find_packages, Extension
from os.path import abspath, dirname, join

here = abspath(dirname(__file__))

# determine the python version
IS_PYPY = hasattr(sys, 'pypy_version_info')

with codecs.open(join(here, 'README.md'), encoding='utf-8') as f:
    README = f.read()

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

install_reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='gpgpass',
    version=version,
    maintainer="Rick van den Hof",
    maintainer_email='r.vandenhof@tiw.nl',
    url='https://github.com/rvdh/gpgpass',
    description='Password manager for groups. Searching thru GPG-encrypted password files.',
    long_description=README,
    license='Apache License, Version 2.0',
    keywords='python passwords security gpg git',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Security :: Utilities',
        'Topic :: Security :: Cryptography',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta'
    ],
    setup_requires=['nose', 'coverage'] + reqs,
    packages=find_packages(exclude=['tests', 'tests.*']),
    test_suite='nose.collector',
    entry_points={'console_scripts': ['gpgpass = gpgpass.gpgpass:main']},
)
