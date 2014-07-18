#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN OVERLAY HANDLER
#################################################################################
# File:       overlay.py
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
#
'''Main handler for overlays.'''

from __future__ import unicode_literals

__version__ = "$Id: overlay.py 273 2006-12-30 15:54:50Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys, os, os.path
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
            'XML parsing failed for "%(origin)s" (line %(line)d, column %(column)d)%(hint)s' % \
            {'line':expat_error.lineno, 'column':expat_error.offset + 1, 'origin':origin, 'hint':hint})


#===============================================================================
#
# Class DbBase
#
#-------------------------------------------------------------------------------

class DbBase(object):
    ''' Handle a list of overlays.'''

    def __init__(self, config, paths=None, ignore = 0,
        ignore_init_read_errors=False
        ):

        self.config = config
        self.paths = paths
        self.ignore = ignore
        self.output = config['output']
        self.ignore_init_read_errors = ignore_init_read_errors

        self.overlays = {}

        self.output.debug('Initializing overlay list handler', 8)

        path_found = False
        for path in self.paths:
            if not os.path.exists(path):
                continue

            self.read_file(path)
            path_found = True

        if not path_found:
            self.output.warn("Warning: an installed db file was not found at: %s"
                % str(self.paths))


    def __eq__(self, other):
        for key in set(self.overlays.keys()) | set(other.overlays.keys()):
            if self.overlays[key] != other.overlays[key]:
                return False
        return True


    def __ne__(self, other):
        return not self.__eq__(other)


    def read_file(self, path):
        '''Read the overlay definition file.'''

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
        raise NotImplementedError('Method "%s.%s" not implemented' % \
                (self.__class__.__name__, this_function_name))


    def read(self, text, origin):
        '''
        Read an xml list of overlays (adding to and potentially overwriting existing entries)
        '''
        try:
            document = ET.fromstring(text)
        except xml.parsers.expat.ExpatError as error:
            raise BrokenOverlayCatalog(origin, error, self._broken_catalog_hint())

        overlays = document.findall('overlay') + \
                document.findall('repo')

        for overlay in overlays:
            self.output.debug('Parsing overlay: %s' % overlay, 9)
            ovl = Overlay(config=self.config, xml=overlay,
                    ignore=self.ignore)
            self.overlays[ovl.name] = ovl
        return


    def add_new(self, xml=None, origin=None, from_dict=None):
        '''Reads xml text and dictionary definitions and adds
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
        """Add a new overlay from a list of dictionary values
        """
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

        except Exception as error:
            raise Exception('Failed to write to local overlays file: '
                            + path + '\nError was:\n' + str(error))

    def select(self, overlay):
        '''
        Select an overlay from the list.
        '''
        self.output.debug("DbBase.select(), overlay = %s" % overlay, 5)
        if not overlay in self.overlays.keys():
            self.output.debug("DbBase.select(), unknown overlay = %s"
                % overlay, 4)
            self.output.debug("DbBase.select(), known overlays = %s"
                % ', '.join(self.overlays.keys()), 4)
            raise UnknownOverlayException(overlay)
        return self.overlays[overlay]

    def list(self, repos=None, verbose = False, width = 0):
        '''
        List all overlays.
        '''
        result = []

        selection = [overlay for (a, overlay) in self.overlays.items()]
        if repos is not None:
            selection = [overlay for overlay in selection if overlay.name in repos]

        for overlay in selection:
            if verbose:
                result.append((overlay.get_infostr(), overlay.is_supported(),
                               overlay.is_official()))
            else:
                result.append((overlay.short_list(width), overlay.is_supported(),
                               overlay.is_official()))

        result = sorted(result, key=lambda summary_supported_official: summary_supported_official[0].lower())

        return result

    def list_ids(self):
        """returns a list of the overlay names
        """
        return sorted(self.overlays)


#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
