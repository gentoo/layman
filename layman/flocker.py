#!/usr/bin/python
# -*- coding: utf-8 -*-
# File:       flocker.py
#
#             Handles all file locking.
#
# Copyright:
#             (c) 2015 Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Michał Górny <mgorny@gentoo.org>
#             Devan Franchini <twitch153@gentoo.org>
#

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------
import fcntl

from layman.compatibility import fileopen

class LockingException(Exception):
    '''
    Exception class for relay errors properly
    '''
    def __init__(self, msg):
        self.msg = msg


    def __str__(self):
        return repr(self.msg)


class FileLocker(object):

    def __init__(self):
        self.files = {}
        self.locked = set()


    def lock_file(self, path, exclusive=False):
        '''Lock the file located at path.'''
        file_mode = 'r'
        lock_mode = fcntl.LOCK_SH

        if exclusive:
            file_mode = 'w+'
            lock_mode = fcntl.LOCK_EX

        if path in self.locked:
            raise LockingException('"%(path)s" is already locked.'
                                    % {'path': path})

        self.locked.add(path)
        fcntl.flock(self.get_file(path, file_mode).fileno(), lock_mode)


    def unlock_file(self, path):
        '''Unlock the file located at path.'''
        if path not in self.locked:
            raise LockingException('"%(path)s" is not locked, unlocking failed'
                                    % {'path': path})

        fcntl.flock(self.get_file(path).fileno(), fcntl.LOCK_UN)
        self.locked.discard(path)


    def get_file(self, path, mode='r'):
        '''Obtains file object for given path'''
        if mode not in ('r', 'w+'):
            raise LockingException('Invalid mode %(mode)s' % {'mode': mode})

        if path not in self.files or self.files[path].closed:
            self.files[path] = fileopen(path, mode)

        f = self.files[path]
        f.seek(0)

        return f
