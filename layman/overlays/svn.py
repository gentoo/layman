#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
# LAYMAN SVN OVERLAY HANDLER
###############################################################################
# File:       svn.py
#
#             Handles subversion overlays
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
''' Subversion overlay support.'''

__version__ = "$Id: svn.py 236 2006-09-05 20:39:37Z wrobel $"

#==============================================================================
#
# Dependencies
#
#------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.source   import OverlaySource, require_supported

#==============================================================================
#
# Class SvnOverlay
#
#------------------------------------------------------------------------------

class SvnOverlay(OverlaySource):
    ''' Handles subversion overlays.'''

    type = 'Subversion'
    type_key = 'svn'

    def __init__(self, parent, config, _location,
            ignore = 0):

        super(SvnOverlay, self).__init__(
            parent, config, _location, ignore)
        self.subpath = None

    def add(self, base):
        '''Add overlay.'''

        if not self.supported():
            return 1

        super(SvnOverlay, self).add(base)

        cfg_opts = self.config["svn_addopts"]
        self.target = path([base, self.parent.name])

        args = ['co']
        if self.config['quiet']:
            args.append('-q')
        if len(cfg_opts):
            args.append(cfg_opts)
        args.append(self.src + '/@')
        args.append(self.target)

        return self.postsync(
            self.run_command(self.command(), args, cmd=self.type),
            cwd=self.target)

    def sync(self, base):
        '''Sync overlay.'''

        if not self.supported():
            return 1

        def checkout_location():
            # Append '@' iff needed
            # Keeps users of SVN <1.6.5 happy in more cases (bug #313303)
            repo_part = self.parent.name
            if self.parent.name.find('@') != -1:
                repo_part = repo_part + '@'
            return path([base, repo_part])

        cfg_opts = self.config["svn_syncopts"]
        self.target = checkout_location()

        # svn up [-q] TARGET
        args = ['up']
        if self.config['quiet']:
            args.append('-q')
        if len(cfg_opts):
            args.append(cfg_opts)
        args.append(self.target)

        return self.postsync(
            self.run_command(self.command(), args, cmd=self.type),
            cwd=self.target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
            [(self.command(),  'svn','dev-vcs/subversion'),],
            self.output.warn)

    def cleanup(self):
        '''Code to run in the event of a keyboard interrupt.
        runs svn cleanup
        '''
        self.output.warn("SVN: preparing to run cleanup()", 2)
        args = ["cleanup"]
        args.append(self.target)
        cleanup = self.run_command(self.command(), args, cmd="svn cleanup")
        return
