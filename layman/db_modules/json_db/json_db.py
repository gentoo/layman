#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN JSON DB
#################################################################################
# File:       json_db.py
#
#             Access JSON overlay database(s).
#
# Copyright:
#             (c) 2015        Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Devan Franchini <twitch153@gentoo.org>
#
'''Handler for json overlay databases.'''

from __future__ import unicode_literals

__version__ = "$Id: json.py 273 2015-07-10 10:10:49Z twitch153 $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import json
import sys

from   layman.compatibility      import fileopen
from   layman.overlays.overlay   import Overlay


#py3.2+
if sys.hexversion >= 0x30200f0:
    _UNICODE = 'unicode'
else:
    _UNICODE = 'UTF-8'



#===============================================================================
#
# Class DBHandler
#
#-------------------------------------------------------------------------------

class DBHandler(object):
    '''
    Handle a json overlay database.
    '''

    def __init__(self, config, overlays, paths=None, ignore=0,
                 ignore_init_read_errors=False):

        self.config = config
        self.ignore = ignore
        self.overlays = overlays
        self.paths = paths
        self.output = config['output']
        self.ignore_init_read_errors = ignore_init_read_errors

        self.output.debug('Initializing JSON overlay list handler', 8)


    def read_db(self, path, text=None):
        '''
        Read the overlay definition file.
        '''
        document = text

        if not document:
            try:
                with fileopen(path, 'r') as df:
                    document = df.read()
            except Exception as error:
                if not self.ignore_init_read_errors:
                    msg = 'JSON DBHandler - Failed to read the overlay list at'\
                      '("%(path)s")' % {'path': path}
                self.output.error(msg)
                raise error

        self.add_new(document, origin=path)


    def add_new(self, document=None, origin=None):
        '''
        Reads in provided json text and generates overlays to populate database.
        '''
        if not document:
            msg = 'JSON DBHandler - add_new() failed: JSON text cannot be none'\
                  '.\nOrigin: %(path)s' % {'path': origin}
            self.output.warn(msg)
            return False

        load = json.loads(document)['repo']

        for ovl in load:
            overlay = Overlay(self.config, json=ovl, ignore=self.ignore)
            self.overlays[overlay.name] = overlay

        return True


    def remove(self, overlay, path):
        '''
        Removes an overlay from installed overlays list.
        '''
        if overlay.name in self.overlays:
            del self.overlays[overlay.name]


    def write(self, path):
        '''
        Write the list of overlays to a file.
        '''
        try:
            repo = {'@encoding': 'unicode', '@version': '1.0', 'repo': []}
            repo['repo'] = [self.overlays[key].to_json() for key in self.overlays]
            with fileopen(path, 'w') as df:
                df.write(json.dumps(repo, sort_keys=True, indent=2))
        except Exception as err:
            msg = 'Failed to write to local overlays file: %(path)s\nError was'\
                  ': %(err)s' % {'path': path, 'err': err}
            self.output.error(msg)
            raise err
