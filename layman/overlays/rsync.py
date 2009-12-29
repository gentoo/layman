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
from   layman.overlays.overlay  import Overlay

#===============================================================================
#
# Class RsyncOverlay
#
#-------------------------------------------------------------------------------

class RsyncOverlay(Overlay):
    ''' Handles rsync overlays.'''

    type = 'Rsync'
    type_key = 'rsync'

    binary = '/usr/bin/rsync'

    base = binary + ' -rlptDvz --progress --delete --delete-after ' +           \
        '--timeout=180 --exclude="distfiles/*" --exclude="local/*" ' +          \
        '--exclude="packages/*" '

    def __init__(self, xml, config, ignore = 0, quiet = False):

        Overlay.__init__(self, xml, config, ignore)

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        Overlay.add(self, base)

        return self.sync(base)

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        if quiet:
            quiet_option = '-q '
        else:
            quiet_option = ''

        return self.cmd(self.base + quiet_option + '"' + self.src + '/" "' +
                        path([base, self.name]) + '"')

    def supported(self):
        '''Overlay type supported?'''

        return Overlay.supported(self, [(self.binary,  'rsync',
                                         'net-misc/rsync'),])
