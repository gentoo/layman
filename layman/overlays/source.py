# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN OVERLAY SOURCE BASE CLASS
#################################################################################
# File:       source.py
#
#             Base class for the different overlay types.
#
# Copyright:
#             (c) 2010        Sebastian Pipping
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Sebastian Pipping <sebastian@pipping.org>

import os
from layman.overlays.overlay import Overlay

class OverlaySource(Overlay):
    def __init__(self, xml, config, ignore = 0, quiet = False):
        super(OverlaySource, self).__init__(xml, config, ignore, quiet)

    def supported(self, binaries = []):
        '''Is the overlay type supported?'''

        if binaries:
            for command, mtype, package in binaries:
                found = False
                if os.path.isabs(command):
                    kind = 'Binary'
                    found = os.path.exists(command)
                else:
                    kind = 'Command'
                    for d in os.environ['PATH'].split(os.pathsep):
                        f = os.path.join(d, command)
                        if os.path.exists(f):
                            found = True
                            break

                if not found:
                    raise Exception(kind + ' ' + command + ' seems to be missing!'
                                    ' Overlay type "' + mtype + '" not support'
                                    'ed. Did you emerge ' + package + '?')

        return True

    def is_supported(self):
        '''Is the overlay type supported?'''

        try:
            self.supported()
            return True
        except Exception, error:
            return False

    def command(self):
        return self.config['%s_command' % self.__class__.type_key]
