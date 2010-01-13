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
from   layman.overlays.source   import OverlaySource

#===============================================================================
#
# Class GitOverlay
#
#-------------------------------------------------------------------------------

class GitOverlay(OverlaySource):
    ''' Handles git overlays.'''

    type = 'Git'
    type_key = 'git'

    def __init__(self, parent, xml, config, _location, ignore = 0, quiet = False):

        super(GitOverlay, self).__init__(parent, xml, config, _location, ignore, quiet)

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
        return self.cmd(self.command() + ' clone ' + quiet_option + '"' + self.src + slash
                        + '" "' + path([base, self.parent.name]) + '"')

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        if quiet:
            quiet_option = ' -q'
        else:
            quiet_option = ''
 
        return self.cmd('cd "' + path([base, self.parent.name]) + '" && '
                        + self.command() + ' pull' + quiet_option)

    def supported(self):
        '''Overlay type supported?'''

        return super(GitOverlay, self).supported([(self.command(),  'git',
                                         'dev-util/git'),])
