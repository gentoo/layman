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
#             (c) 2005 - 2008 Gunnar Wrobel
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
    type_key = 'cvs'

    def __init__(self, xml, config, ignore = 0, quiet = False):

        Overlay.__init__(self, xml, config, ignore, quiet)

        if 'subpath' in xml.attrib:
            self.subpath = xml.attrib['subpath']
        else:
            self.subpath = ''

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        if quiet:
            quiet_option = ' -q'
        else:
            quiet_option = ''

        return self.cmd('cd "' + base + '" && CVSROOT="' + self.src + '" ' +
                        self.command() + quiet_option + ' co -d "' + self.name
                        + '" "' + self.subpath + '"' )

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        if quiet:
            quiet_option = ' -q'
        else:
            quiet_option = ''

        return self.cmd('cd "' + path([base, self.name]) + '" && ' +
                        self.command() + quiet_option + ' update -d')

    def supported(self):
        '''Overlay type supported?'''

        return Overlay.supported(self, [(self.command(),  'cvs',
                                         'dev-util/cvs'),])
