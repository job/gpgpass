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

import os
from os.path import dirname, realpath, join


class TestGpgPass(unittest.TestCase):
    def test_00__init(self):
        state = gpgpass.init()
        self.assertTrue(state)

        # Init again, to pick up the now created config.ini
        state = gpgpass.init()
        self.assertTrue(state)

    def test_01__updateRepository(self):
        state = gpgpass.updateRepository('/tmp/testrepo', 1440, 'https://github.com/rvdh/gpgpass.git')
        self.assertEqual(state, 2)
        state = gpgpass.updateRepository('/tmp/testrepo', 1440)
        self.assertEqual(state, 1)
        with self.assertRaises(StandardError):
            state = gpgpass.updateRepository('/tmp', 1440) # /tmp should not be a GIT repo ;)

#        self.assertTrue('radix.Radix' in str(type(tree)))
#        self.assertEquals(num_nodes_in - num_nodes_del, num_nodes_out)
#        self.assertNotEquals(node, None)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
