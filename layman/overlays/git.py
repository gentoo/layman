#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN GIT OVERLAY HANDLER
#################################################################################
# File:       git.py
#
#             Handles git overlays
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel, Stefan Schweizer
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Stefan Schweizer <genstef@gentoo.org>
''' Git overlay support.'''

__version__ = "$Id: git.py 146 2006-05-27 09:52:36Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class GitOverlay
#
#-------------------------------------------------------------------------------

class GitOverlay(OverlaySource):
    ''' Handles git overlays.'''

    type = 'Git'
    type_key = 'git'

    def __init__(self, parent, xml, config, _location, ignore = 0, quiet = False):

        super(GitOverlay, self).__init__(parent, xml, config, _location, ignore, quiet)

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        def fix_git_source(source):
            # http:// should get trailing slash, other protocols shouldn't
            if source.split(':')[0] == 'http':
                return source + '/'
            return source

        # git clone [-q] SOURCE TARGET
        args = ['clone']
        if quiet:
            args.append('-q')
        args.append(fix_git_source(self.src))
        args.append(path([base, self.parent.name]))
        return self.run_command(args)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        args = ['pull']
        if quiet:
            args.append('-q')
        return self.run_command(args, cwd=path([base, self.parent.name]))

    def supported(self):
        '''Overlay type supported?'''

        return require_supported([(self.command(),  'git',
                                         'dev-vcs/git'),])
