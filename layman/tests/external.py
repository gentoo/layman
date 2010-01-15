# -*- coding: utf-8 -*-
#################################################################################
# EXTENRAL LAYMAN TESTS
#################################################################################
# File:       external.py
#
#             Runs external (non-doctest) test cases.
#
# Copyright:
#             (c) 2009        Sebastian Pipping
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Sebastian Pipping <sebastian@pipping.org>
#
'''Runs external (non-doctest) test cases.'''

import unittest
import os
from layman.overlay import Overlays
from warnings import filterwarnings, resetwarnings

HERE = os.path.dirname(os.path.realpath(__file__))


class Unicode(unittest.TestCase):
    def _overlays_bug(self, number):
        config = {}
        filename = os.path.join(HERE, 'testfiles', 'overlays_bug_%d.xml' % number)
        o = Overlays([filename], config)
        for verbose in (True, False):
            for t in o.list(verbose=verbose):
                print t[0]
                print

    def test_184449(self):
        self._overlays_bug(184449)

    def test_286290(self):
        self._overlays_bug(286290)


class FormatSubpathCategory(unittest.TestCase):
    def _run(self, number):
        config = {}
        filename1 = os.path.join(HERE, 'testfiles',
                'subpath-%d.xml' % number)

        # Read, write, re-read, compare
        os1 = Overlays([filename1], config)
        filename2 = os.tmpnam()
        os1.write(filename2)
        os2 = Overlays([filename2], config)
        os.unlink(filename2)
        self.assertTrue(os1 == os2)

        # Pass original overlays
        return os1

    def test(self):
        os1 = self._run(1)
        os2 = self._run(2)

        # Same content from old/layman-global.txt
        #   and new/repositories.xml format?
        self.assertTrue(os1 == os2)


if __name__ == '__main__':
    filterwarnings('ignore')
    unittest.main()
    resetwarnings()
