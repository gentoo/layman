# -*- coding: utf-8 -*-
###############################################################################
# LAYMAN OVERLAY SOURCE BASE CLASS
###############################################################################
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

from __future__ import unicode_literals

import os
import copy
import sys
import shutil
import subprocess
from layman.utils import path, resolve_command, run_command

supported_cache = {}

def _supported(key, check_supported=None):
    """internal caching function that checks tracks any
    un-supported/supported repo types."""
    if key is None:
        return False
    if key not in supported_cache:
        supported_cache[key] = check_supported()
    return supported_cache[key]


def require_supported(binaries, _output):
    for command, mtype, package in binaries:
        kind, path = resolve_command(command, _output)
        if not path:
            if _output:
                _output(kind + ' ' + command + ' seems to be missing!'
                            ' Overlay type "' + mtype + '" not support'
                            'ed. Did you emerge ' + package + '?')
            return False
    return True


class OverlaySource(object):

    type_key = None

    def __init__(self, parent, config, _location,
            ignore = 0):
        self.parent = parent
        self.src = _location
        self.config = config
        self.ignore = ignore

        self.output = config['output']

    def __eq__(self, other):
        return self.src == other.src

    def __ne__(self, other):
        return not self.__eq__(other)

    def add(self, base):
        '''Add the overlay.'''

        mdir = path([base, self.parent.name])

        if os.path.exists(mdir):
            self.output.error('Directory ' + mdir +
                ' already exists. Will not overwrite its contents!')
            return False

        os.makedirs(mdir)
        return True

    def update(self, src):
        '''
        Updates the overlay source url.
        
        @params src: source URL.
        '''
        pass

    def sync(self, base):
        '''Sync the overlay.'''
        pass

    def delete(self, base):
        '''Delete the overlay.'''
        mdir = path([base, self.parent.name])

        if not os.path.exists(mdir):
            self.output.warn('Directory ' + mdir + \
                ' did not exist, no files deleted.')
            return False

        self.output.info('Deleting directory "%s"' % mdir, 2)
        shutil.rmtree(mdir)
        return True

    def supported(self):
        '''Is the overlay type supported?'''
        return True

    def is_supported(self):
        '''Is the overlay type supported?'''
        return _supported(self.get_type_key(), self.supported)

    def get_type_key(self):
        return '%s' % self.__class__.type_key

    def command(self):
        return self.config['%s_command' % self.__class__.type_key]

    def postsync(self, failed_sync, **kwargs):
        """Runs any repo specific postsync operations
        """
        # check if the add/sync operation succeeded
        if failed_sync:
            return failed_sync
        # good to continue
        postsync_opt = self.config['%s_postsync' % self.__class__.type_key]
        if len(postsync_opt):
            # repalce "%cwd=" while it's still a string'
            _opt = postsync_opt.replace('%cwd=',
                kwargs.get('cwd', '')).split()
            command = _opt[0]
            args = _opt[1:]
            return run_command(self.config, command, args,
                cmd='%s_postsync' % self.__class__.type_key)
        return failed_sync

    def to_xml_hook(self, repo_elem):
        pass
