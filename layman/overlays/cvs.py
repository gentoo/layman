#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN CVS OVERLAY HANDLER
#################################################################################
# File:       cvs.py
#
#             Handles cvs overlays
#
# Copyright:
#             (c) 2005 - 2006 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
''' Cvs overlay support.'''

__version__ = "$Id$"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.overlay  import Overlay

#===============================================================================
#
# Class CvsOverlay
#
#-------------------------------------------------------------------------------

class CvsOverlay(Overlay):
    ''' Handles cvs overlays.'''

    type = 'cvs'

    binary = '/usr/bin/cvs'

    def __init__(self, xml, ignore = 0, quiet = False):

        Overlay.__init__(self, xml, ignore, quiet)

        if '&subpath' in self.data.keys():
            self.subpath = self.data['&subpath']
        else:
            self.subpath = ''

    def add(self, base):
        '''Add overlay.'''

        self.supported()

        return self.cmd('cd "' + base + '" && CVSROOT="' + self.src + '" ' + 
                        self.binary + ' co -d "' + self.name 
                        + '" "' + self.subpath + '"' )

    def sync(self, base):
        '''Sync overlay.'''

        self.supported()

        return self.cmd('cd "' + path([base, self.name]) + '" && ' +
                        self.binary + ' update')

    def supported(self):
        '''Overlay type supported?'''

        return Overlay.supported(self, [(self.binary,  'cvs',
                                         'dev-util/cvs'),])
