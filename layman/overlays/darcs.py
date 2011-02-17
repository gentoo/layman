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
#             (c) 2005 - 2008 Gunnar Wrobel, Andres Loeh
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
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class BzrOverlay
#
#-------------------------------------------------------------------------------

class DarcsOverlay(OverlaySource):
    ''' Handles darcs overlays.'''

    type = 'Darcs'
    type_key = 'darcs'

    def __init__(self, parent, xml, config, _location, ignore = 0, quiet = False):

        super(DarcsOverlay, self).__init__(parent, xml, config, _location, ignore, quiet)

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        cfg_opts = self.config["darcs_addopts"]

        # darcs get --partial SOURCE TARGET
        if cfg_opts:
            args = ['get', '--partial', cfg_opts,
                self.src + '/', path([base, self.parent.name])]
        else:
            args = ['get', '--partial',
                self.src + '/', path([base, self.parent.name])]

        return self.run_command(*args)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        cfg_opts = self.config["darcs_addopts"]

        # darcs pull --all SOURCE
        if cfg_opts:
            args = ['pull', '--all', cfg_opts, self.src]
        else:
            args = ['pull', '--all', self.src]
        return self.run_command(*args, cwd=path([base, self.parent.name]))

    def supported(self):
        '''Overlay type supported?'''

        return require_supported([(self.command(),  'darcs',
                                         'dev-vcs/darcs'),])
