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

    def __init__(self, parent, xml, config, _location, ignore = 0, quiet = False):
        super(GCommonOverlay, self).__init__(parent, xml, config, _location, ignore, quiet)
        #split source into driver and remote uri. 
        self.driver=self.src[:self.src.find(' ')]
        self.remote_uri=self.src[self.src.find(' ')+1:]

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        os.makedirs(os.path.join(base,self.parent.name))
        return self.sync(base, quiet)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        args = [os.path.join(base,self.parent.name), 'sync', self.driver, self.remote_uri]
        returncode=self.run_command(*args,cwd=path([base,self.parent.name]))
        if returncode: return returncode
        args = [os.path.join(base,self.parent.name), 'generate-tree']
        return self.run_command(*args,cwd=path([base,self.parent.name]))

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
                                [(self.command(),
                                'g-common',
                                'app-portage/g-common'),
                                ('/usr/share/g-common/drivers/'+self.driver+'.cfg',
                                'g-common for '+self.driver,
                                'app-portage/g-'+self.driver),])
