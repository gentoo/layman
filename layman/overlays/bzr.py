#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN BZR OVERLAY HANDLER
#################################################################################
# File:       bzr.py
#
#             Handles bzr overlays
#
# Copyright:
#             (c) 2005 - 2008 Adrian Perez, Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Adrian Perez <moebius@connectical.net>
#             Gunnar Wrobel <wrobel@gentoo.org>
#
'''Should work with any version of Bzr equal to or better than 0.7 --
 caution: tested only with 0.8 and 0.8.2...'''

__version__ = "$Id: bzr.py 236 2006-09-05 20:39:37Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.overlay  import Overlay

#===============================================================================
#
# Class BzrOverlay
#
#-------------------------------------------------------------------------------

class BzrOverlay(Overlay):
    ''' Handles bzr overlays.'''

    type = 'Bzr'
    type_key = 'bzr'

    def __init__(self, xml, config, ignore = 0, quiet = False):

        super(BzrOverlay, self).__init__(xml, config, ignore)

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        return self.cmd(self.command() + ' get "' + self.src + '/" "' +\
                        path([base, self.name]) + '"')

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        return self.cmd('cd "' + path([base, self.name]) + '" && ' +          \
                        self.command() + ' pull --overwrite "' + self.src \
                        + '"')

    def supported(self):
        '''Overlay type supported?'''

        return super(BzrOverlay, self).supported([(self.command(),  'bzr',
                                         'dev-util/bzr'),])
