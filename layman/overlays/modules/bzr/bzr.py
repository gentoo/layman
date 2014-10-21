#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN BZR OVERLAY HANDLER
#################################################################################
# File:       bzr.py
#
#             Handles bzr overlays
#
# Copyright:
#             (c) 2005 - 2008 Adrian Perez, Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Adrian Perez <moebius@connectical.net>
#             Gunnar Wrobel <wrobel@gentoo.org>
#
'''Should work with any version of Bzr equal to or better than 0.7 --
 caution: tested only with 0.8 and 0.8.2...'''

from __future__ import unicode_literals

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path, run_command
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class BzrOverlay
#
#-------------------------------------------------------------------------------

class BzrOverlay(OverlaySource):
    ''' Handles bzr overlays.'''

    type = 'Bzr'
    type_key = 'bzr'

    def __init__(self, parent, config, _location, ignore = 0):

        super(BzrOverlay, self).__init__(parent,
            config, _location, ignore)
        self.branch = None

    def _fix_bzr_source(self, source):
        '''
        Adds trailing slash to source URL if needed.

        @params source: source URL, string.
        '''
        if source.endswith("/"):
            return source
        return source + '/'
    
    def add(self, base):
        '''Add overlay.'''

        if not self.supported():
            return 1

        cfg_opts = self.config["bzr_addopts"]
        target = path([base, self.parent.name])

        src = self._fix_bzr_source(self.src)

        # bzr get SOURCE TARGET
        if len(cfg_opts):
            args = ['branch', cfg_opts,
                src, target]
        else:
            args = ['branch', src, target]
        return self.postsync(
            run_command(self.config, self.command(), args, cmd=self.type),
            cwd=target)

    def update(self, base, src):
        '''
        Updates overlay src-url.
        
        @params base: base location where all overlays are installed.
        @params src: source URL.
        '''

        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        # bzr bind SOURCE
        args = ['bind', self._fix_bzr_source(src)]
        if self.config['quiet']:
            args.append('--quiet')
        return self.postsync(
            run_command(self.config, self.command(), args, cmd=self.type),
            cwd=target)

    def sync(self, base):
        '''Sync overlay.'''

        if not self.supported():
            return 1

        cfg_opts = self.config["bzr_syncopts"]
        target = path([base, self.parent.name])

        # bzr pull --overwrite SOURCE
        if len(cfg_opts):
            args = ['pull', cfg_opts, '--overwrite', self.src]
        else:
            args = ['pull', '--overwrite', self.src]
        return self.postsync(
            run_command(self.config, self.command(), args, cwd=target,
                        cmd=self.type),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
            [(self.command(),  'bzr', 'dev-vcs/bzr'),],
            self.output.warn)
