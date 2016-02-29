#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN DB BASE
#################################################################################
# File:       dbbase.py
#
#             Main handler of overlay database(s).
#
# Copyright:
#             (c) 2005 - 2009 Gunnar Wrobel
#             (c) 2009        Sebastian Pipping
#             (c) 2009        Christian Groschupp
#             (c) 2015        Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Sebastian Pipping <sebastian@pipping.org>
#             Christian Groschupp <christian@groschupp.org>
#             Devan Franchini <twitch153@gentoo.org>
#
'''Main handler for overlay database(s).'''

from __future__ import unicode_literals

__version__ = "$Id: dbbase.py 273 2015-07-09 11:35:55Z twitch153 $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os
import os.path
import sys

from   layman.module             import Modules, InvalidModuleName
from   layman.overlays.overlay   import Overlay


#py3.2+
if sys.hexversion >= 0x30200f0:
    _UNICODE = 'unicode'
    STR = str
else:
    _UNICODE = 'UTF-8'
    STR = basestring


MOD_PATH = os.path.join(os.path.dirname(__file__), 'db_modules')

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
# Class DbBase
#
#-------------------------------------------------------------------------------

class DbBase(object):
    '''
    Handle a list of overlays.
    '''

    def __init__(self, config, paths=None, ignore=0,
           ignore_init_read_errors=False, allow_missing=False):

        self.config = config
        self.db_type = config['db_type']
        self.ignore = ignore
        self.ignore_init_read_errors = ignore_init_read_errors
        self.mod_ctl = Modules(path=MOD_PATH,
                               namepath='layman.db_modules',
                               output=config['output'])
        self.output = config['output']
        self.overlays = {}
        self.paths = paths

        path_found = False

        self.output.debug('Initializing overlay list handler', 8)

        if isinstance(self.db_type, STR):
            self.db_type = [x.strip() for x in self.db_type.split(',')]

        if len(self.db_type) > 1:
            msg = 'DbBase; warning, multiple instances of "db_type" found:'\
                  ' %(db_types)s.\nDefaulting to: %(db_type)s'\
                  % {'db_types': self.db_type, 'db_type': self.db_type[0]}
            self.output.warn(msg)

        self.db_type = self.db_type[0] + '_db'

        for path in self.paths:
            if not os.path.exists(path):
                continue

            success = self.read_db(path)
            if not success:
                msg = 'DbBase; error, Failed to read database at "%(path)s"\n'\
                      'Hint: If you manually set db_type. Please reset it and '\
                      'let layman-updater\nmigrate it. Otherwise layman\'s '\
                      'database is not initialized, nor populated\nwith any '\
                      'existing data.\nRun the following: "layman-updater -m '\
                      '<db_type>"' % {'path': path}
                self.output.error(msg)
                sys.exit(-1)

            path_found = True

        if not path_found and not allow_missing:
            msg = 'Warning: an installed db file was not found at: %(path)s'\
                   % {'path': str(self.paths)}
            self.output.warn(msg)


    def __eq__(self, other):
        for key in set(self.overlays.keys()) | set(other.overlays.keys()):
            if self.overlays[key] != other.overlays[key]:
                return False
        return True


    def __ne__(self, other):
        return not self.__eq__(other)


    def _add_from_dict(self, overlays=None):
        '''
        Add a new overlay from a list of dictionary values
        '''
        self.output.info('DbBase: add_from_dict()')

        for overlay in overlays:
            self.output.debug('Parsing overlay entry', 8)
            ovl = Overlay(self.config, ovl_dict=overlay,
                          ignore=self.ignore)
            self.overlays[ovl.name] = ovl

        return


    def _broken_catalog_hint(self):
        this_function_name = sys._getframe().f_code.co_name
        msg = 'Method "%(name)s.%(func)s" not implemented'\
              % {'name': self.__class__.__name__,
                 'func': this_function_name}

        raise NotImplementedError(msg)


    def _get_dbctl(self, db_type):
        '''
        Returns database module controller for class or dies trying.
        '''
        try:
            db_ctl = self.mod_ctl.get_class(db_type)(self.config,
                        self.overlays,
                        self.paths,
                        self.ignore,
                        self.ignore_init_read_errors)
        except InvalidModuleName:
            msg = 'DbBase._get_dbctl() error:\nDatabase module name '\
                  '"%(name)s" is invalid or not found.\nPlease set db_type '\
                  'variable to proper value to continue.'\
                  % {'name': db_type.replace('_db', '')}
            self.output.die(msg)

        return db_ctl


    def add_new(self, xml=None, origin=None, from_dict=None):
        '''
        Reads xml text and dictionary definitions and adds
        them to the db.

        NOTE: Currently being refactored. Will be disabled until fixed.
        '''
        '''
        if xml is not None:
            self.read(xml, origin)
        if from_dict is not None:
            self.output.info("DbBase: add_new() from_dict")
            if isinstance(from_dict, dict):
                from_dict = [from_dict]
            self._add_from_dict(from_dict)
        '''

        return


    def read_db(self, path, text=None, text_type=None):
        '''
        Read the overlay database for installed overlay definitions.
        '''
        db_type = self.db_type

        if text and text_type:
            db_type = text_type + '_db'

        #Added to keep xml functionality for cached overlay XML definitions
        if 'cache' in path and '.xml' in path:
            db_type = 'xml_db'

        db_ctl = self._get_dbctl(db_type)
        return db_ctl.read_db(path, text=text)


    def write(self, path, remove=False, migrate_type=None):
        '''
        Write the list of overlays to a file.
        '''
        db_type = self.db_type

        if migrate_type:
            db_type = migrate_type + '_db'

        db_ctl = self._get_dbctl(db_type)
        db_ctl.write(path, remove=remove)


    def remove(self, overlay, path):
        '''
        Remove an overlay from the database.
        '''
        db_ctl = self._get_dbctl(self.db_type)
        db_ctl.remove(overlay, path)


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


    def list(self, repos=None, verbose=False, width=0):
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
