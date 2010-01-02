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


if __name__ == '__main__':
    unittest.main()
