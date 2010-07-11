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

from layman.config import BareConfig
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
       
        self.config = config if config else BareConfig(output=output)
        
        self.report_errors = report_errors
        
        # get installed and available dbs
        self._installed_db = None
        self._installed_ids = None
        self._available_db = None
        self._available_ids = None
        self._error_messages = []
        self.sync_results = []
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


    @staticmethod
    def _check_repo_type( repos, caller):
        if isinstance(repos, str):
            repos = [repos]
        elif not isinstance(repos, list):
            self._error(2, "%s(), Unsupported input type: %s" %(caller, str(type(repos))))
            return []
        return repos


    def delete_repo(self, repos):
        """delete the selected repo from the system
        
       @type repos: list
        @param repos: ['repo-id1', ...]
        @param output: method to handle output if desired
        @rtype dict
        """
        repos = self._check_repo_type(repos, "delete_repo")
        results = []
        for id in repos:
            if not self.is_installed(id):
                results.append(True)
                break
            if not self.is_repo(id):
                self._error(1, UNKNOWN_REPO_ID %id)
                results.append(False)
                break
            try:
                self._installed_db.delete(self._installed_db.select(id))
                results.append(True)
            except Exception, e:
                self._error(ERROR_INTERNAL_ERROR,
                        "Failed to disable repository '"+id+"':\n"+str(e))
                results.append(False)
            self.get_installed(reload=True)
        if False in results:
            return False
        return True


    def add_repo(self, repos):
        """installs the seleted repo id
        
        @type repos: list
        @param repos: ['repo-id1', ...]
        @param output: method to handle output if desired
        @rtype dict
        """
        repos = self._check_repo_type(repos, "add_repo")
        results = []
        for id in repos:
            if self.is_installed(id):
                results.append(True)
                break
            if not self.is_repo(id):
                self._error(1, UNKNOWN_REPO_ID %id)
                results.append(False)
                break
            try:
                self._installed_db.add(self._available_db.select(id), quiet=True)
                results.append(True)
            except Exception, e:
                self._error(ERROR_INTERNAL_ERROR,
                        "Failed to enable repository '"+id+"' : "+str(e))
                results.append(False)
            self.get_installed(reload=True)
        if False in results:
            return False
        return True


    def get_info(self, repos):
        """retirves the recorded information about the repo specified by id
        
        @type repos: list
        @param repos: ['repo-id1', ...]
        @rtype list of tuples [(str, bool, bool),...]
        @return: dictionary  {'id': (info, official, supported)}
        """
        repos = self._check_repo_type(repos, "get_info")
        result = {}

        for id in repos:
            if not self.is_repo(id):
                self._error(1, UNKNOWN_REPO_ID %id)
                result[id] = ('', False, False)
            try:
                overlay = self._available_db.select(id)
            except UnknownOverlayException, error:
                self._error(2, "Error: %s" %str(error))
                result[id] = ('', False, False)
            else:
                # Is the overlay supported?
                info = overlay.__str__()
                official = overlay.is_official()
                supported = overlay.is_supported()
                result[id] = (info, official, supported)

        return result


    def sync(self, repos, output_results=True):
        """syncs the specified repo(s) specified by repos
        
        @type repos: list or string
        @param repos: ['repo-id1', ...] or 'repo-id'
        @rtype bool or {'repo-id': bool,...}
        """
        fatals = []
        warnings = []
        success  = []
        repos = self._check_repo_type(repos, "sync")

        for id in repos:
            try:
                odb = self._installed_db.select(id)
            except UnknownOverlayException, error:
                self._error(1,"Sync(), failed to select %s overlay.  Original error was: %s" %(id, str(error)))
                continue

            try:
                ordb = self._available_db.select(id)
            except UnknownOverlayException:
                message = 'Overlay "%s" could not be found in the remote lists.\n' \
                        'Please check if it has been renamed and re-add if necessary.' %id
                warnings.append((id, message))
            else:
                current_src = odb.sources[0].src
                available_srcs = set(e.src for e in ordb.sources)
                if ordb and odb and not current_src in available_srcs:
                    if len(available_srcs) == 1:
                        plural = ''
                        candidates = '  %s' % tuple(available_srcs)[0]
                    else:
                        plural = 's'
                        candidates = '\n'.join(('  %d. %s' % (id + 1, v)) for id, v in enumerate(available_srcs))

                    warnings.append((id,
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
                            'repo_name':id,
                            'current_src':current_src,
                            'candidates':candidates,
                            'plural':plural,
                            }))

            try:
                self._installed_db.sync(id, self.config['quiet'])
                success.append((id,'Successfully synchronized overlay "' + id + '".'))
            except Exception, error:
                fatals.append((id,
                    'Failed to sync overlay "' + id + '".\nError was: '
                    + str(error)))

        if output_results:
            if success:
                self.output.info('\nSuccess:\n------\n', 3)
                for id, result in success:
                    self.output.info(result, 3)
                    
            if warnings:
                self.output.warn('\nWarnings:\n------\n', 2)
                for id, result in warnings:
                    self.output.warn(result + '\n', 2)

            if fatals:
                self.output.error('\nErrors:\n------\n')
                for id, result in fatals:
                    self.output.error(result + '\n')
                return False

        self.sync_results = (success, warnings, fatals)

        return True


    def fetch_remote_list(self):
        """Fetches the latest remote overlay list"""
        try:
            self._available_db.cache()
        except Exception, error:
            self._error(-1,'Failed to fetch overlay list!\n Original Error was: '
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


    def _error(self, num, message):
        """outputs the error to the pre-determined output
        defaults to stderr.  This method may be removed, is here for now
        due to code taken from the packagekit backend.
        """
        m = "Error: %d," %num, message
        self._error_messages.append(m)
        if self.report_errors:
            print >>stderr, m


    def get_errors(self):
        """returns any warning or fatal messages that occurred during
        an operation and resets it back to None
        """
        if self._error_messages:
            return self._error_messages[:]
            self._error_messages = []


def create_fd():
    """creates file descriptor pairs an opens them ready for
    use in place of stdin, stdout, stderr.
    """
    fd_r, fd_w = os.pipe()
    w = os.fdopen(fd_w, 'w')
    r = os.fdopen(fd_r, 'r')
    return (r, w, fd_r, fd_w)
    
    
