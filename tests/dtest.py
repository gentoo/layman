#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN DOCTEST AGGREGATOR
#################################################################################
# File:       dtest.py
#
#             Combines the doctests that are available for the different modules
#
# Copyright:
#             (c) 2005 - 2006 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
'''Aggregates doctests from all modules that provide such tests.'''

__version__ = '$Id: dtest.py 237 2006-09-05 21:18:54Z wrobel $'

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import unittest, doctest, sys

# On module creation:

# 1.) Check header section (copyright notice)
# 2.) Add module doc string
# 3.) Add version string
# 4.) Add testing handler at bottom of module
# 5.) Add module into tests/dtest.py. Check that tests run through
# 6.) Run pylint over the code. Fix any reasonable complaints.
# 7.) Whitespace clean the buffer.
# 8.) Add svn:keywords "Id" to file.

# On module change:

# 1.) Check header section (copyright notice)
# 5.) Check that tests run through
# 6.) Run pylint over the code. Fix any reasonable complaints.
# 7.) Whitespace clean the buffer.

# clean modules         : CT
# not yet clean         : UT
# clean but no testing  : CN
# unclean but no testing: UN

import layman.action             #CT
import layman.config             #CT
import layman.db                 #CT
import layman.overlay            #CT
import layman.utils              #CT
import layman.overlays.overlay   #CT
import layman.overlays.tar       #CT

#===============================================================================
#
# Test Suite
#
#-------------------------------------------------------------------------------

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(layman.action),
        doctest.DocTestSuite(layman.config),
        doctest.DocTestSuite(layman.db),
        doctest.DocTestSuite(layman.overlay),
        doctest.DocTestSuite(layman.utils),
        doctest.DocTestSuite(layman.overlays.overlay),
        doctest.DocTestSuite(layman.overlays.tar),
        ))

#===============================================================================
#
# Run Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    unittest.main(defaultTest='test_suite')

    resetwarnings()
