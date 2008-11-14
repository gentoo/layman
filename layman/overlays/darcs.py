#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN DARCS OVERLAY HANDLER
#################################################################################
# File:       darcs.py
#
#             Handles darcs overlays
#
# Copyright:
#             (c) 2005 - 2006 Gunnar Wrobel, Andres Loeh
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Andres Loeh <kosmikus@gentoo.org>
#
''' Darcs overlay support.'''

__version__ = "$Id: darcs.py 236 2006-09-05 20:39:37Z wrobel $"

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

class DarcsOverlay(Overlay):
    ''' Handles darcs overlays.'''

    type = 'Darcs'

    binary_command  = '/usr/bin/darcs'

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        return self.cmd(self.binary_command + ' get --partial "' + self.src +
                        '/" "' + path([base, self.name]) + '"')

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        return self.cmd('cd "' + path([base, self.name]) + '" && ' +
                        self.binary_command + ' pull --all "' + self.src + '"')

    def supported(self):
        '''Overlay type supported?'''

        return Overlay.supported(self, [(self.binary_command,  'darcs',
                                         'dev-util/darcs'),])
