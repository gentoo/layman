#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

from   layman.utils             import path
from   layman.overlays.source   import OverlaySource

#===============================================================================
#
# Class StubOverlay
#
#-------------------------------------------------------------------------------

class StubOverlay(OverlaySource):
    ''' Handles overlays with missing modules. '''

    type = 'N/A'
    type_key = 'n/a'

    def __init__(self, parent, config, _location, ignore = 0):
        super(StubOverlay, self).__init__(parent,
            config, _location, ignore)
        self.branch = self.parent.branch
        self.info = {'name': self.parent.name, 'type': self.parent.ovl_type}
        self.missing_msg = 'Overlay "%(name)s" is missing "%(type)s" module!'\
            % self.info
        self.hint = 'Did you install layman with "%(type)s" support?'\
            % self.info


    def add(self, base):
        '''Add overlay.'''
        self.output.error(self.missing_msg)
        self.output.warn(self.hint)
        return True


    def update(self, base, src):
        '''
        Updates overlay src-url.
        '''
        self.output.error(self.missing_msg)
        self.output.warn(self.hint)
        return True


    def sync(self, base):
        '''Sync overlay.'''
        self.output.error(self.missing_msg)
        self.output.warn(self.hint)
        return True


    def supported(self):
        '''Overlay type supported?'''
        return False
