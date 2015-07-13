#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN XML DB
#################################################################################
# File:       xml_db.py
#
#             Access XML overlay database(s).
#
# Copyright:
#             (c) 2015        Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Devan Franchini <twitch153@gentoo.org>
#
'''Handler for xml overlay databases.'''

from __future__ import unicode_literals

__version__ = "$Id: xml_db.py 273 2015-07-07 10:30:30Z twitch153 $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys
import xml
import xml.etree.ElementTree as ET # Python 2.5

from   layman.utils              import indent
from   layman.compatibility      import fileopen
from   layman.overlays.overlay   import Overlay


#py3.2+
if sys.hexversion >= 0x30200f0:
    _UNICODE = 'unicode'
else:
    _UNICODE = 'UTF-8'


#===============================================================================
#
# Class BrokenOverlayCatalog
#
#-------------------------------------------------------------------------------

class BrokenOverlayCatalog(ValueError):
    def __init__(self, origin, expat_error, hint=None):
        if hint == None:
            hint = ''
        else:
            hint = '\nHint: %s' % hint

        super(BrokenOverlayCatalog, self).__init__(
            'XML parsing failed for "%(origin)s" (line %(line)d, column'\
            '%(column)d)%(hint)s' % {'line': expat_error.lineno,
                                     'column':expat_error.offset + 1,
                                     'origin':origin, 'hint':hint})


#===============================================================================
#
# Class DbBase
#
#-------------------------------------------------------------------------------

class DBHandler(object):
    '''
    Handle a xml overlay database.
    '''

    def __init__(self, config, overlays, paths=None, ignore=0,
                 ignore_init_read_errors=False):

        self.config = config
        self.ignore = ignore
        self.overlays = overlays
        self.paths = paths
        self.output = config['output']
        self.ignore_init_read_errors = ignore_init_read_errors

        self.output.debug('Initializing XML overlay list handler', 8)


    def _broken_catalog_hint(self):
        this_function_name = sys._getframe().f_code.co_name

        msg = 'Method "%(name)s.%(func)s" not implemented'\
              % {'name': self.__class__.__name__,
                 'func': this_function_name}

        raise NotImplementedError(msg)


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
                    msg = 'XML DBHandler - Failed to read the overlay list at'\
                      '("%(path)s")' % {'path': path}
                self.output.error(msg)
                raise error

        self.read(document, origin=path)


    def read(self, text, origin):
        '''
        Read an xml list of overlays (adding to and potentially overwriting
        existing entries)
        '''
        try:
            document = ET.fromstring(text)
        except xml.parsers.expat.ExpatError as err:
            raise BrokenOverlayCatalog(origin, err, self._broken_catalog_hint())

        overlays = document.findall('overlay') + document.findall('repo')

        for overlay in overlays:
            msg = 'XML DBHandler - Parsing overlay: %(ovl)s' % {'ovl': overlay}
            self.output.debug(msg, 9)
            ovl = Overlay(config=self.config, xml=overlay, ignore=self.ignore)
            self.overlays[ovl.name] = ovl


    def add_new(self, xml=None, origin=None):
        '''
        Reads xml text and dictionary definitions and adds
        them to the db.
        '''
        if not xml:
            msg = 'XML DBHandler - add_new() failed: XML text cannot be none'
            self.output.warn(msg)
            return False

        self.read(xml, origin)
        return True


    def write(self, path):
        '''
        Write the list of overlays to a file.
        '''
        tree = ET.Element('repositories', version="1.0", encoding=_UNICODE)
        tree[:] = [e.to_xml() for e in self.overlays.values()]
        indent(tree)
        tree = ET.ElementTree(tree)
        try:
            with fileopen(path, 'w') as f:
                tree.write(f, encoding=_UNICODE)

        except Exception as err:
            msg = 'Failed to write to local overlays file: %(path)s\nError was'\
                  ':\n%(err)s' % {'path': path, 'err': err}
            raise Exception(msg)
