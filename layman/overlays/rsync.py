#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN RSYNC OVERLAY HANDLER
#################################################################################
# File:       rsync.py
#
#             Handles rsync overlays
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
''' Rsync overlay support.'''

__version__ = "$Id: rsync.py 236 2006-09-05 20:39:37Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class RsyncOverlay
#
#-------------------------------------------------------------------------------

class RsyncOverlay(OverlaySource):
    ''' Handles rsync overlays.'''

    type = 'Rsync'
    type_key = 'rsync'


    def __init__(self, parent, config, _location, ignore = 0, quiet = False):

        super(RsyncOverlay, self).__init__(parent, config, _location, ignore, quiet)

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        super(RsyncOverlay, self).add(base)

        return self.sync(base)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        # rsync OPTIONS [-q] SOURCE TARGET
        args = ['-rlptDvz', '--progress', '--delete', '--delete-after', '--timeout=180',
            '--exclude=distfiles/*', '--exclude=local/*', '--exclude=packages/*']

        cfg_opts = self.config["rsync_syncopts"]
        target = path([base, self.parent.name])

        if quiet:
            args.append('-q')
        if cfg_opts:
            args.append(cfg_opts)
        args.append(self.src + '/')
        args.append(target)

        return self.postsync(
            self.run_command(self.command(), *args, cmd=self.type),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported([(self.command(),  'rsync',
                                         'net-misc/rsync'),])
