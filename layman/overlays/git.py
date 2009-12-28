#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN GIT OVERLAY HANDLER
#################################################################################
# File:       git.py
#
#             Handles git overlays
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel, Stefan Schweizer
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Stefan Schweizer <genstef@gentoo.org>
''' Git overlay support.'''

__version__ = "$Id: git.py 146 2006-05-27 09:52:36Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.overlay  import Overlay

#===============================================================================
#
# Class GitOverlay
#
#-------------------------------------------------------------------------------

class GitOverlay(Overlay):
    ''' Handles git overlays.'''

    type = 'Git'
    type_key = 'git'

    binary_command  = '/usr/bin/git'

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        if quiet:
            quiet_option = '-q '
        else:
            quiet_option = ''
 
        # http:// should get trailing slash, other protocols shouldn't
        slash = ''
        if self.src.split(':')[0] == 'http':
            slash = '/'
        return self.cmd(self.binary_command + ' clone ' + quiet_option + '"' + self.src + slash
                        + '" "' + path([base, self.name]) + '"')

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        if quiet:
            quiet_option = ' -q'
        else:
            quiet_option = ''
 
        return self.cmd('cd "' + path([base, self.name]) + '" && '
                        + self.binary_command + ' pull' + quiet_option)

    def supported(self):
        '''Overlay type supported?'''

        return Overlay.supported(self, [(self.binary_command,  'git',
                                         'dev-util/git'),])
