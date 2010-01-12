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

from layman.overlays.overlay import Overlay

class OverlaySource(Overlay):
    def __init__(self, xml, config, ignore = 0, quiet = False):
        super(OverlaySource, self).__init__(xml, config, ignore, quiet)
