#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN DB BASE
#################################################################################
# File:       dbbase.py
#
#             Access to an xml list of overlays
#
# Copyright:
#             (c) 2005 - 2009 Gunnar Wrobel
#             (c) 2009        Sebastian Pipping
#             (c) 2009        Christian Groschupp
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Sebastian Pipping <sebastian@pipping.org>
#             Christian Groschupp <christian@groschupp.org>
#             Devan Franchini <twitch153@gentoo.org>
#
'''Main handler for overlays.'''

from __future__ import unicode_literals

__version__ = "$Id: overlay.py 273 2006-12-30 15:54:50Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os
import os.path
import sys
import xml
import xml.etree.ElementTree as ET # Python 2.5

#from   layman.debug              import OUT
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
# Class UnknownOverlayException
#
#-------------------------------------------------------------------------------
def UnknownOverlayMessage(ovl):
    return 'Exception: Overlay "%s" does not exist.' % ovl

class UnknownOverlayException(Exception):
    def __init__(self, repo_name):
        self.repo_name = repo_name

    def __str__(self):
        return UnknownOverlayMessage(self.repo_name)

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

class DbBase(object):
    '''
    Handle a list of overlays.
    '''

    def __init__(self, config, paths=None, ignore = 0,
        ignore_init_read_errors=False, allow_missing=False):

        self.config = config
        self.ignore = ignore
        self.paths = paths
        self.output = config['output']
        self.overlays = {}
        self.ignore_init_read_errors = ignore_init_read_errors
        path_found = False

        self.output.debug('Initializing overlay list handler', 8)

        for path in self.paths:
            if not os.path.exists(path):
                continue

            self.read_file(path)
            path_found = True

        if not path_found and not allow_missing:
            msg = "Warning: an installed db file was not found at: %(path)s"
            self.output.warn(msg % {'path': str(self.paths)})


    def __eq__(self, other):
        for key in set(self.overlays.keys()) | set(other.overlays.keys()):
            if self.overlays[key] != other.overlays[key]:
                return False
        return True


    def __ne__(self, other):
        return not self.__eq__(other)


    def read_file(self, path):
        '''
        Read the overlay definition file.
        '''
        try:
            with fileopen(path, 'r') as df:
                document = df.read()

        except Exception as error:
            if not self.ignore_init_read_errors:
                self.output.error('Failed to read the overlay list at ("'
                    + path + '")')
                raise error

        self.read(document, origin=path)


    def _broken_catalog_hint(self):
        this_function_name = sys._getframe().f_code.co_name
        msg = 'Method "%(name)s.%(func)s" not implemented'\
              % {'name': self.__class__.__name__,
                 'func': this_function_name}
        raise NotImplementedError(msg)


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
            self.output.debug('Parsing overlay: %s' % overlay, 9)
            ovl = Overlay(config=self.config, xml=overlay, ignore=self.ignore)
            self.overlays[ovl.name] = ovl


    def add_new(self, xml=None, origin=None, from_dict=None):
        '''
        Reads xml text and dictionary definitions and adds
        them to the db.
        '''
        if xml is not None:
            self.read(xml, origin)
        if from_dict is not None:
            self.output.info("DbBase: add_new() from_dict")
            if isinstance(from_dict, dict):
                from_dict = [from_dict]
            self._add_from_dict(from_dict)

        return


    def _add_from_dict(self, overlays=None):
        '''
        Add a new overlay from a list of dictionary values
        '''
        self.output.info("DbBase: add_from_dict()")
        for overlay in overlays:
            self.output.debug('Parsing overlay entry', 8)
            ovl = Overlay(self.config, ovl_dict=overlay,
                    ignore=self.ignore)
            self.overlays[ovl.name] = ovl
        return


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


    def select(self, overlay):
        '''
        Select an overlay from the list.
        '''
        ovl = {'ovl': overlay}
        msg = 'DbBase.select(), overlay = %(ovl)s' % ovl
        self.output.debug(msg, 5)

        if not overlay in self.overlays.keys():
            msg = 'DbBase.select(), unknown overlay = %(ovl)s' % ovl
            self.output.debug(msg, 4)
            ovls = {'ovls': ', '.join(self.overlays.keys())}
            msg = 'DbBase.select(), known overlays = %(ovls)s' % ovls
            self.output.debug(ovls, 4)
            raise UnknownOverlayException(overlay)
        return self.overlays[overlay]

    def list(self, repos=None, verbose = False, width = 0):
        '''
        List all overlays.
        '''
        result = []

        selection = [overlay for (a, overlay) in self.overlays.items()]
        if repos is not None:
            selection = [ovl for ovl in selection if ovl.name in repos]

        for overlay in selection:
            if verbose:
                result.append((overlay.get_infostr(), overlay.is_supported(),
                               overlay.is_official()))
            else:
                result.append((overlay.short_list(width),
                               overlay.is_supported(), overlay.is_official()))

        result = sorted(result, key=lambda summary_supported_official:\
                                summary_supported_official[0].lower())

        return result

    def list_ids(self):
        '''
        Returns a list of the overlay names
        '''
        return sorted(self.overlays)
