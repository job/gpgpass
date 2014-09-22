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

from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import unittest

from gpgpass import gpgpass
from ConfigParser import SafeConfigParser

import os
import shutil
from os.path import dirname, realpath, join


class TestGpgPass(unittest.TestCase):
    def test_00__imports(self):
        # clear PATH to force failing to find the module
        path = sys.path
        sys.path = []
        with self.assertRaises(SystemExit) as cm:
            state = gpgpass.importGnuPG()
        self.assertEqual(cm.exception.code, 1)
        with self.assertRaises(SystemExit) as cm:
            state = gpgpass.importGit()
        self.assertEqual(cm.exception.code, 1)

        # Restore PATH
        sys.path = path

    def test_01__init(self):
        state = gpgpass.init('/tmp/gpgpasscfg.%s' % os.getpid(), '/tmp/gpgpasscfg-pwrepo.%s' % os.getpid())
        self.assertTrue(state)

        # Init again, to pick up the now created config.ini
        state = gpgpass.init('/tmp/gpgpasscfg.%s' % os.getpid(), '/tmp/gpgpasscfg-pwrepo.%s' % os.getpid())
        self.assertTrue(state)

        # Init with an invalid path
        with self.assertRaises(SystemExit) as cm:
            state = gpgpass.init('/tmp/gpgpasscfg-proc.%s' % os.getpid(), '/proc/foo')
        self.assertEqual(cm.exception.code, 1)

        # https://github.com/rvdh/gpgpass_passwords.git
        cfg = SafeConfigParser()
        cfg.read(os.path.join('/tmp/gpgpasscfg.%s' % os.getpid(), 'config.ini'))
        cfg.set('Passwords', 'passwordsRepositoryRemote', 'https://github.com/rvdh/gpgpass_passwords.git')
        with open(os.path.join('/tmp/gpgpasscfg.%s' % os.getpid(), 'config.ini'), 'wb') as fh:
            cfg.write(fh)

        # Run the test again, now with a remote
        state = gpgpass.init('/tmp/gpgpasscfg.%s' % os.getpid(), '/tmp/gpgpasscfg-pwrepo.%s' % os.getpid())
        self.assertTrue(state)

        # Remove the tmp config dir
        shutil.rmtree('/tmp/gpgpasscfg.%s' % os.getpid())
        shutil.rmtree('/tmp/gpgpasscfg-proc.%s' % os.getpid())
        shutil.rmtree('/tmp/gpgpasscfg-pwrepo.%s' % os.getpid())

    def test_02__updateRepository(self):
        state = gpgpass.updateRepository('/tmp/testrepo.%s' % os.getpid(), 1440, 'https://github.com/rvdh/gpgpass.git')
        self.assertEqual(state, 2)
        state = gpgpass.updateRepository('/tmp/testrepo.%s' % os.getpid(), 1440)
        self.assertEqual(state, 1)
        state = gpgpass.updateRepository('/tmp/testrepo.%s' % os.getpid(), 0)
        self.assertEqual(state, 1)

        # Remove the temp repo
        shutil.rmtree('/tmp/testrepo.%s' % os.getpid())

        with self.assertRaises(StandardError):
            state = gpgpass.updateRepository('/tmp', 1440) # /tmp should not be a GIT repo ;)

    def test_03__searchThruFiles(self):
        gpgpass.init('/tmp/gpgpasstest03.%s' % os.getpid(), '/tmp/gpgpasstest03-pwrepo.%s' % os.getpid())
        cfg = SafeConfigParser()
        cfg.read(os.path.join('/tmp/gpgpasstest03.%s' % os.getpid(), 'config.ini'))
        cfg.set('Passwords', 'passwordsRepositoryRemote', 'https://github.com/rvdh/gpgpass_passwords.git')
        with open(os.path.join('/tmp/gpgpasstest03.%s' % os.getpid(), 'config.ini'), 'wb') as fh:
            cfg.write(fh)

        # Check out the repository
        gpgpass.init('/tmp/gpgpasstest03.%s' % os.getpid(), '/tmp/gpgpasstest03-pwrepo.%s' % os.getpid())

        # Copy the test file
        #shutil.copyfile("/tmp/gpgpasstest03-pwrepo.%s/testfile.gpg" % os.getpid(), '/tmp/gpgpasstest03-pwrepo.%s/testfile.gpg' % os.getpid())

        self.assertTrue(gpgpass.searchThruFiles("search", False, os.path.join(os.path.dirname(os.path.realpath(__file__)), "gpg")))
        self.assertTrue(gpgpass.searchThruFiles("search", True, os.path.join(os.path.dirname(os.path.realpath(__file__)), "gpg")))

        # Test for whole file
        with self.assertRaises(SystemExit) as cm:
            gpgpass.searchThruFiles("testfile.gpg", True, os.path.join(os.path.dirname(os.path.realpath(__file__)), "gpg"))
        self.assertEqual(cm.exception.code, 0)

        # Remove the temp repo
        shutil.rmtree('/tmp/gpgpasstest03.%s' % os.getpid())
        shutil.rmtree('/tmp/gpgpasstest03-pwrepo.%s' % os.getpid())

    def test_04__parseargs(self):
        state = gpgpass.parse_args(['foo'])
        self.assertEqual(state.searchText, 'foo')




#        self.assertTrue('radix.Radix' in str(type(tree)))
#        self.assertEquals(num_nodes_in - num_nodes_del, num_nodes_out)
#        self.assertNotEquals(node, None)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
