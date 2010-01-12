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

import xml.etree.ElementTree as ET # Python 2.5

from   layman.utils             import path, ensure_unicode
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

        super(CvsOverlay, self).__init__(xml, config, ignore, quiet)

        _subpath = xml.find('subpath')
        if _subpath != None:
            self.subpath = ensure_unicode(_subpath.text.strip())
        elif 'subpath' in xml.attrib:
            self.subpath = ensure_unicode(xml.attrib['subpath'])
        else:
            self.subpath = ''

    def __eq__(self, other):
        res = super(CvsOverlay, self).__eq__(other) \
            and self.subpath == other.subpath
        return res

    def __ne__(self, other):
        return not self.__eq__(other)

    # overrider
    def to_xml(self):
        repo = super(CvsOverlay, self).to_xml()
        if self.subpath:
            _subpath = ET.Element('subpath')
            _subpath.text = self.subpath
            repo.append(_subpath)
        return repo

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

        return super(CvsOverlay, self).supported([(self.command(),  'cvs',
                                         'dev-util/cvs'),])
