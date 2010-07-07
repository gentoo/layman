#!python
# -*- coding: utf-8 -*-
#######################################################################
# LAYMAN - A UTILITY TO SELECT AND UPDATE GENTOO OVERLAYS
#######################################################################
# Distributed under the terms of the GNU General Public License v2
#
# Copyright:
#             (c) 2010 Brian Dolbec
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#              Brian Dolbec <dol-sen@sourceforge.net>
#

from sys import stderr, stdin, stdout
import os, types

from layman.config import Config
#from layman.action import Sync

from layman.dbbase import UnknownOverlayException
from layman.db import DB, RemoteDB
#from layman.utils import path, delete_empty_directory
from layman.debug import Message, OUT

# give them some values for now, these are from the packagekit backend
# TODO  establish some proper errors for the api.
ERROR_REPO_NOT_FOUND = -1
ERROR_INTERNAL_ERROR = -2
UNKNOWN_REPO_ID = "Repo ID '%s' " + \
        "is not listed in the current available overlays list"

# In order to redirect output you need to get a Message class instance with the
# stderr, stdout, stddebug directed to where you want.
# eg:  output = Message('layman', err=mystderr, dbg=mydebug, out=myoutput)
# there are many more options available, refer to debug.py Message class


class LaymanAPI(object):
    """class to hold and run a layman instance for use by API consumer apps, guis, etc.
    """
    ## hell, even the current cli should probably be converted to use this one.
    ## It is a near duplicate of the actions classes.

    def __init__(self, config=None, report_errors=False, output=None):
        """@param configfile, optional config file to use instead of the default
        """
        
        self.output = output if output  else OUT
       
        self.config = config if config else Config(output=output)
        
        self.report_errors = report_errors
        
        # get installed and available dbs
        self._installed_db = None
        self._installed_ids = None
        self._available_db = None
        self._available_ids = None
        # call reload() for now to initialize the 2 db's
        self.reload()
        # change it to delayed loading (similar to delayed imports)
        # to simplify some of the code and make it automagic.


    def is_repo(self, id):
        """validates that the id given is a known repo id
        
        @param id: repo id
        @type id: str
        @rtype boolean
        """
        return id in self._available_ids


    def is_installed(self, id):
        """checks the repo id is a known installed repo id
        
        @param id: repo id
        @type id: str
        @rtype boolean
        """
        return id in self._installed_ids


    def delete_repo(self, repos):
        """delete the selected repo from the system
        
       @type repos: list
        @param repos: ['repo-id1', ...]
        @param output: method to handle output if desired
        @rtype dict
        """
        results = {}
        for id in repos:
            if not self.is_installed(id):
                results[i] = True
                break
            if not self.is_repo(id):
                self.error(1, UNKNOWN_REPO_ID %id)
                results[i] = False
                break
            try:
                self._installed_db.delete(self._installed_db.select(id))
                results[i] = True
            except Exception, e:
                self.error(ERROR_INTERNAL_ERROR,
                        "Failed to disable repository '"+id+"':\n"+str(e))
                results[i] = False
            self.get_installed(reload=True)
        return results


    def add_repo(self, repos):
        """installs the seleted repo id
        
        @type repos: list
        @param repos: ['repo-id1', ...]
        @param output: method to handle output if desired
        @rtype dict
        """
        results = {}
        for id in repos:
            if self.is_installed(id):
                results[i] = True
                break
            if not self.is_repo(id):
                self.error(1, UNKNOWN_REPO_ID %id)
                results[i] = False
                break
            try:
                self._installed_db.add(self._available_db.select(id), quiet=True)
                results[i] = True
            except Exception, e:
                self.error(ERROR_INTERNAL_ERROR,
                        "Failed to enable repository '"+id+"' : "+str(e))
                results[i] = False
            self.get_installed(reload=True)
        return results


    def get_info(self, repos):
        """retirves the recorded information about the repo specified by id
        
        @type repos: list
        @param repos: ['repo-id1', ...]
        @rtype list of tuples [(str, bool, bool),...]
        @return: (info, official, supported)
        """
        result = []

        for i in repos:
            if not self.is_repo(id):
                self.error(1, UNKNOWN_REPO_ID %id)
                result.append(('', False, False))
            try:
                overlay = self._available_db.select(i)
            except UnknownOverlayException, error:
                self.error(2, "Error: %s" %str(error))
                result.append(('', False, False))
            else:
                # Is the overlay supported?
                info = overlay.__str__()
                official = overlay.is_official()
                supported = overlay.is_supported()
                result.append((info, official, supported))

        return result


    def sync(self, repos):
        """syncs the specified repo(s) specified by repos
        
        @type repos: list
        @param repos: ['repo-id1', ...]
        @rtype bool
        """
        # currently uses a modified Sync class with a few added parameters,
        # but should be re-written into here for a better fit and output
        #_sync = Sync(self.config, repos, db=self._installed_db, rdb=self._available_db)
        #_sync.run()
        
        fatals = []
        warnings = []
        success  = []
        for i in repos:
            try:
                odb = self._installed_db.select(i)
            except UnknownOverlayException, error:
                fatals.append((i, str(error)))
                continue

            try:
                ordb = self._available_db.select(i)
            except UnknownOverlayException:
                warnings.append((i,
                    'Overlay "%s" could not be found in the remote lists.\n'
                    'Please check if it has been renamed and re-add if necessary.', {'repo_name':i}))
            else:
                current_src = odb.sources[0].src
                available_srcs = set(e.src for e in ordb.sources)
                if ordb and odb and not current_src in available_srcs:
                    if len(available_srcs) == 1:
                        plural = ''
                        candidates = '  %s' % tuple(available_srcs)[0]
                    else:
                        plural = 's'
                        candidates = '\n'.join(('  %d. %s' % (i + 1, v)) for i, v in enumerate(available_srcs))

                    warnings.append((i,
                        'The source of the overlay "%(repo_name)s" seems to have changed.\n'
                        'You currently sync from\n'
                        '\n'
                        '  %(current_src)s\n'
                        '\n'
                        'while the remote lists report\n'
                        '\n'
                        '%(candidates)s\n'
                        '\n'
                        'as correct location%(plural)s.\n'
                        'Please consider removing and re-adding the overlay.' , {
                            'repo_name':i,
                            'current_src':current_src,
                            'candidates':candidates,
                            'plural':plural,
                            }))

            try:
                self._installed_db.sync(i, self.config['quiet'])
                success.append((i,'Successfully synchronized overlay "' + i + '".'))
            except Exception, error:
                fatals.append((i,
                    'Failed to sync overlay "' + i + '".\nError was: '
                    + str(error)))

        return (warnings, success, fatals)


    def fetch_remote_list(self):
        """Fetches the latest remote overlay list"""
        try:
            self._available_db.cache()
        except Exception, error:
            self.error(-1,'Failed to fetch overlay list!\n Original Error was: '
                    + str(error))
            return False
        return True


    def get_available(self, reload=False):
        """returns the list of available overlays"""
        if not self._available_db or reload:
            self._available_db = RemoteDB(self.config)
            self._available_ids = sorted(self._available_db.overlays)
        return self._available_ids[:]


    def get_installed(self, reload=False):
        """returns the list of installed overlays"""
        if not self._installed_db or reload:
            self._installed_db = DB(self.config)
            self._installed_ids = sorted(self._installed_db.overlays)
        return self._installed_ids[:]


    def reload(self):
        """reloads the installed and remote db's to the data on disk"""
        result = self.get_available(reload=True)
        result = self.get_installed(reload=True)


    def error(self, num, message):
        """outputs the error to the pre-determined output
        defaults to stderr.  This method may be removed, is here for now
        due to code taken from the packagekit backend.
        """
        if self.report_errors:
            print >>stderr, "Error: %d," %num, message


class Output(Message):
    """a subclass of debug.py's Message to overide several output functions
    for data capture.  May not be in final api"""
    
    def __init__(self, error=stderr):
        self.stderr = error
        self.captured = []
        Message.__init__(self, err=error)

    def notice (self, note):
        self.captured.append(note)

    def info (self, info, level = 4):

        if type(info) not in types.StringTypes:
            info = str(info)

        if level > self.info_lev:
            return

        for i in info.split('\n'):
            self.captured.append(self.maybe_color('green', '* ') + i)

    def status (self, message, status, info = 'ignored'):

        if type(message) not in types.StringTypes:
            message = str(message)

        lines = message.split('\n')

        if not lines:
            return

        for i in lines[0:-1]:
            self.captured.append(self.maybe_color('green', '* ') + i)

        i = lines[-1]

        if len(i) > 58:
            i = i[0:57]

        if status == 1:
            result = '[' + self.maybe_color('green', 'ok') + ']'
        elif status == 0:
            result = '[' + self.maybe_color('red', 'failed') + ']'
        else:
            result = '[' + self.maybe_color('yellow', info) + ']'

        self.captured.append( self.maybe_color('green', '* ') + i + ' ' + '.' * (58 - len(i))  \
              + ' ' + result)

    def warn (self, warn, level = 4):

        if type(warn) not in types.StringTypes:
            warn = str(warn)

        if level > self.warn_lev:
            return

        for i in warn.split('\n'):
            self.captured.append(self.maybe_color('yellow', '* ') + i)


def create_fd():
    """creates file descriptor pairs an opens them ready for
    use in place of stdin, stdout, stderr.
    """
    fd_r, fd_w = os.pipe()
    w = os.fdopen(fd_w, 'w')
    r = os.fdopen(fd_r, 'r')
    return (r, w, fd_r, fd_w)
    
    
