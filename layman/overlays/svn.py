#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN SVN OVERLAY HANDLER
#################################################################################
# File:       svn.py
#
#             Handles subversion overlays
#
# Copyright:
#             (c) 2005 - 2006 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
''' Subversion overlay support.'''

__version__ = "$Id: svn.py 236 2006-09-05 20:39:37Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.overlay  import Overlay

#===============================================================================
#
# Class SvnOverlay
#
#-------------------------------------------------------------------------------

class SvnOverlay(Overlay):
    ''' Handles subversion overlays.'''

    type = 'Subversion'

    binary = '/usr/bin/svn'

    def add(self, base):
        '''Add overlay.'''

        self.supported()

        Overlay.add(self, base)

        return self.cmd(self.binary + ' co "' + self.src + '/" "' +
                        path([base, self.name]) + '"')

    def sync(self, base):
        '''Sync overlay.'''

        self.supported()

        return self.cmd(self.binary + ' update "' + path([base, self.name]) +
                        '"')

    def supported(self):
        '''Overlay type supported?'''

        return Overlay.supported(self, [(self.binary,  'svn',
                                         'dev-util/subversion'),])
