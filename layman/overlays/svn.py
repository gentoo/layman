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

    def __init__(self, parent, xml, config, _location,
            ignore = 0, quiet = False):

        super(SvnOverlay, self).__init__(
            parent, xml,config, _location, ignore, quiet)

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        super(SvnOverlay, self).add(base)

        cfg_opts = self.config["svn_addopts"]

        args = ['co']
        if quiet:
            args.append('-q')
        if cfg_opts:
            args.append(cfg_opts)
        args.append(self.src + '/@')
        args.append(path([base, self.parent.name]))

        return self.run_command(*args)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        def checkout_location():
            # Append '@' iff needed
            # Keeps users of SVN <1.6.5 happy in more cases (bug #313303)
            repo_part = self.parent.name
            if self.parent.name.find('@') != -1:
                repo_part = repo_part + '@'
            return path([base, repo_part])

        cfg_opts = self.config["svn_syncopts"]

        # svn up [-q] TARGET
        args = ['up']
        if quiet:
            args.append('-q')
        if cfg_opts:
            args.append(cfg_opts)
        args.append(checkout_location())

        return self.run_command(*args)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
            [(self.command(),  'svn','dev-vcs/subversion'),]
        )
