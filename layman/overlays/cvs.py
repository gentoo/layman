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
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class CvsOverlay
#
#-------------------------------------------------------------------------------

class CvsOverlay(OverlaySource):
    ''' Handles cvs overlays.'''

    type = 'cvs'
    type_key = 'cvs'

    def __init__(self, parent, config, _location, ignore = 0, quiet = False):

        super(CvsOverlay, self).__init__(parent, config, _location, ignore, quiet)


    def __eq__(self, other):
        res = super(CvsOverlay, self).__eq__(other) \
            and self.subpath == other.subpath
        return res

    def __ne__(self, other):
        return not self.__eq__(other)

    # overrider
    def to_xml_hook(self, repo_elem):
        if self.subpath:
            _subpath = ET.Element('subpath')
            _subpath.text = self.subpath
            repo_elem.append(_subpath)
            del _subpath

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        cfg_opts = self.config["cvs_addopts"]
        target = path([base, self.parent.name])

        # cvs [-q] co -d SOURCE SCOPE
        args = []
        if quiet:
            args.append('-q')
        args.append('co')
        args.append('-d')
        if cfg_opts:
            args.append(cfg_opts)
        args.append(self.parent.name)
        args.append(self.subpath)

        return self.postsync(
            self.run_command(self.command(), *args, cwd=base,
                env=dict(CVSROOT=self.src), cmd=self.type),
            cwd=target)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        cfg_opts = self.config["cvs_syncopts"]
        target = path([base, self.parent.name])

        # cvs [-q] update -d
        args = []
        if quiet:
            args.append('-q')
        args.append('update')
        args.append('-d')
        if cfg_opts:
            args.append(cfg_opts)
        return self.postsync(
            self.run_command(self.command(), *args, cwd=target, cmd=self.type),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
            [(self.command(),  'cvs', 'dev-vcs/cvs'),],
            self.output.error)
