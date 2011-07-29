#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN G-COMMON OVERLAY HANDLER
#################################################################################
# File:       g_common.py
#
#             Handles g-common-style repositories
#
# Copyright:
#             (c) 2010 Gentoo Foundation
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Auke Booij <auke@tulcod.com>
#
''' G-common repository support.'''

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os
from   layman.utils             import path
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class GCommonOverlay
#
#-------------------------------------------------------------------------------

class GCommonOverlay(OverlaySource):
    ''' Handles g-common-style repositories.'''

    type = 'g-common'
    type_key = 'g-common'

    def __init__(self, parent, config, _location, ignore = 0, quiet = False):
        super(GCommonOverlay, self).__init__(parent, config,
            _location, ignore, quiet)
        #split source into driver and remote uri.
        self.driver=self.src[:self.src.find(' ')]
        self.remote_uri=self.src[self.src.find(' ')+1:]
        self.subpath = None

    def add(self, base, quiet = False):
        '''Add overlay.'''

        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        os.makedirs(target)

        return self.sync(base, quiet)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        args = [target, 'sync', self.driver, self.remote_uri]
        returncode = self.run_command(self.command(), args, cwd=target)
        if returncode:
            return returncode
        args = [target, 'generate-tree']
        return self.postsync(
            self.run_command(self.command(), args, cwd=target, cmd=self.type),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
            [(self.command(),
            'g-common',
            'app-portage/g-common'),
            ('/usr/share/g-common/drivers/'+self.driver+'.cfg',
            'g-common for '+self.driver,
            'app-portage/g-'+self.driver),],
            self.output.warn)
