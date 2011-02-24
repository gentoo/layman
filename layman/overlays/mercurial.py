#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN MERCURIAL OVERLAY HANDLER
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
''' Mercurial overlay support.'''

__version__ = "$Id: mercurial.py 236 2006-09-05 20:39:37Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class MercurialOverlay
#
#-------------------------------------------------------------------------------

class MercurialOverlay(OverlaySource):
    ''' Handles mercurial overlays.'''

    type = 'Mercurial'
    type_key = 'mercurial'

    def __init__(self, parent, config,
        _location, ignore = 0, quiet = False):

        super(MercurialOverlay, self).__init__(parent,
            config, _location, ignore, quiet)

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        cfg_opts = self.config["mercurial_addopts"]
        target = path([base, self.parent.name])

        # hg clone SOURCE TARGET
        if cfg_opts:
            args = ['clone', cfg_opts, self.src + '/', target]
        else:
            args = ['clone', self.src + '/', target]

        return self.postsync(
            self.run_command(self.command(), *args, cmd=self.type),
            cwd=target)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        cfg_opts = self.config["mercurial_syncopts"]
        target = path([base, self.parent.name])

        # hg pull -u SOURCE
        if cfg_opts:
            args = ['pull', '-u', cfg_opts, self.src]
        else:
            args = ['pull', '-u', self.src]

        return self.postsync(
            self.run_command(self.command(), *args, cwd=target, cmd=self.type),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported([(self.command(),  'mercurial',
                                         'dev-vcs/mercurial'),])
