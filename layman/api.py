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

from __future__ import print_function

from sys import stderr
import os

from layman.config import BareConfig

from layman.dbbase import UnknownOverlayException, UnknownOverlayMessage
from layman.db import DB, RemoteDB
#from layman.utils import path, delete_empty_directory

# give them some values for now, these are from the packagekit backend
# TODO  establish some proper errors for the api.
ERROR_REPO_NOT_FOUND = -1
ERROR_INTERNAL_ERROR = -2
UNKNOWN_REPO_ID = "Repo ID '%s' " + \
        "is not listed in the current available overlays list"


class LaymanAPI(object):
    """class to hold and run a layman instance for use by API consumer apps, guis, etc.
    """
    ## hell, even the current cli should probably be converted to use this one.
    ## It is a near duplicate of the actions classes.

    def __init__(self, config=None, report_errors=False, output=None):
        """
        @param configfile: optional config file to use instead of the default.
                                        can be a BareConfig or ArgsParser config class.
                                        default is BareConfig(output=output)
        @param report_errors: optional bool to silence some error reporting to stdout
                                                default is False
        @param output: optional Message class instance created with your settings.
                                    default is Message(module='layman') other params are defaults.
        """

        self.config = config if config is not None else BareConfig(output=output)

        self.output = self.config['output']

        self.report_errors = report_errors

        # add our error recording function to output
        self.output.error_callback = self._error

        # get installed and available dbs
        self._installed_db = None
        self._installed_ids = None
        self._available_db = None
        self._available_ids = None
        self._error_messages = []
        self.sync_results = []


    def is_repo(self, ovl):
        """validates that the ovl given is a known repo id

        @param ovl: repo id
        @type ovl: str
        @rtype boolean
        """
        return ovl in self.get_available()


    def is_installed(self, ovl):
        """checks that ovl is a known installed repo id

        @param ovl: repo id
        @type ovl: str
        @rtype boolean
        """
        return ovl in self.get_installed()


    @staticmethod
    def _check_repo_type( repos, caller):
        """internal function that validates the repos parameter,
        converting a string to a list[string] if it is not already a list.
        produces and error message if it is any other type
        returns repos as list always"""
        if isinstance(repos, basestring):
            repos = [repos]
        # else assume it is an iterable, if not it will error
        return repos


    def delete_repos(self, repos):
        """delete the selected repo from the system

        @type repos: list of strings or string
        @param repos: ['repo-id1', ...] or 'repo-id'
        @param output: method to handle output if desired
        @rtype dict
        """
        repos = self._check_repo_type(repos, "delete_repo")
        results = []
        for ovl in repos:
            if not self.is_installed(ovl):
                self._error("Repository '"+ovl+"' was not installed")
                results.append(False)
                continue
            success = False
            try:
                success = self._get_installed_db().delete(
                    self._get_installed_db().select(ovl))
            except Exception as e:
                self._error(
                        "Exception caught disabling repository '"+ovl+"':\n"+str(e))
            results.append(success)
            self.get_installed(dbreload=True)
        if False in results:
            return False
        return True


    def add_repos(self, repos):
        """installs the seleted repo id

        @type repos: list of strings or string
        @param repos: ['repo-id', ...] or 'repo-id'
        @param output: method to handle output if desired
        @rtype dict
        """
        repos = self._check_repo_type(repos, "add_repo")
        results = []
        for ovl in repos:
            if self.is_installed(ovl):
                self._error("Repository '"+ovl+"' was already installed")
                results.append(False)
                continue
            if not self.is_repo(ovl):
                self._error(UnknownOverlayMessage(ovl))
                results.append(False)
                continue
            success = False
            try:
                success = self._get_installed_db().add(
                    self._get_remote_db().select(ovl), quiet=True)
            except Exception as e:
                self._error("Exception caught enabling repository '"+ovl+"' : "+str(e))
            results.append(success)
            self.get_installed(dbreload=True)
        if False in results:
            return False
        return True


    def get_all_info(self, repos, local=False):
        """retrieves the recorded information about the repo(s)
        specified by repo-id

        @type repos: list of strings or string
        @param repos: ['repo-id1', ...] or 'repo-id'
        @rtype list of tuples [(str, bool, bool),...]
        @return: dictionary of dictionaries
        {'ovl1':
            {'name': str,
            'owner_name': str,
            'owner_email': str,
            ' homepage': str,
            'description': str,
            'src_uris': list of str ['uri1',...]
            'src_type': str,
            'priority': int,
            'quality': str
            'status':,
            'official': bool,
            'supported': bool,
            },
        'ovl2': {...}
        }
        """

        repos = self._check_repo_type(repos, "get_info")
        result = {}

        if local:
            db = self._get_installed_db()
        else:
            db = self._get_remote_db()

        for ovl in repos:
            if not self.is_repo(ovl):
                self._error(UnknownOverlayMessage(ovl))
                result[ovl] = ('', False, False)
                continue
            try:
                overlay = db.select(ovl)
            except UnknownOverlayException as error:
                self._error(error)
                result[ovl] = ('', False, False)
            else:
                result[ovl] = {
                    'name': overlay.name,
                    'owner_name': overlay.owner_name,
                    'owner_email': overlay.owner_email,
                    'homepage': overlay.homepage,
                    'irc': overlay.irc,
                    'description': overlay.description,
                    'feeds': overlay.feeds,
                    'sources': [(e.src, e.type, e.subpath) \
                        for e in overlay.sources],
                    #'src_uris': [e.src for e in overlay.sources],
                    'src_uris': overlay.source_uris(),
                    'src_types': overlay.source_types(),
                    #'src_types': [e.type for e in overlay.sources],
                    'priority': overlay.priority,
                    'quality': overlay.quality,
                    'status': overlay.status,
                    'official': overlay.is_official(),
                    'supported': overlay.is_supported(),
                    }

        return result


    def get_info_str(self, repos, local=True, verbose=False, width=0):
        """retrieves the string representation of the recorded information
        about the repo(s) specified by ovl

        @type repos: list of strings or string
        @param repos: ['repo-id1', ...] or 'repo-id'
        @rtype list of tuples [(str, bool, bool),...]
        @return: dictionary  {'repo-id': (info string, official, supported)}
        """
        repos = self._check_repo_type(repos, "get_info")
        result = {}

        if local:
            db = self._get_installed_db()
        else:
            db = self._get_remote_db()

        for ovl in repos:
            if not self.is_repo(ovl):
                self._error(UnknownOverlayMessage(ovl))
                result[ovl] = ('', False, False)
                continue
            try:
                overlay = db.select(ovl)
                #print("overlay = ", ovl)
                #print("!!!", overlay)
            except UnknownOverlayException as error:
                #print("ERRORS", str(error))
                self._error(error)
                result[ovl] = ('', False, False)
            else:
                # Is the overlay supported?
                if verbose:
                    info = overlay.get_infostr()
                else:
                    info = overlay.short_list(width)
                official = overlay.is_official()
                supported = overlay.is_supported()
                result[ovl] = (info, official, supported)

        return result

    def get_info_list(self, local=True, verbose=False, width=0):
        """retrieves the string representation of the recorded information
        about the repo(s)

        @param local: bool (defaults to True)
        @param verbose: bool(defaults to False)
        @param width: int (defaults to 0)
        @rtype list of tuples [(str, bool, bool),...]
        @return: list  [(info string, official, supported),...]
        """

        if local:
            return self._get_installed_db().list(verbose=verbose, width=width)
        else:
            return self._get_remote_db().list(verbose=verbose, width=width)


    def sync(self, repos, output_results=True):
        """syncs the specified repo(s) specified by repos

        @type repos: list of strings or string
        @param repos: ['repo-id1', ...] or 'repo-id'
        @rtype bool or {'repo-id': bool,...}
        """
        fatals = []
        warnings = []
        success  = []
        repos = self._check_repo_type(repos, "sync")
        db = self._get_installed_db()

        for ovl in repos:
            try:
                odb = db.select(ovl)
            except UnknownOverlayException as error:
                self._error(UnknownOverlayException(error))
                continue

            try:
                ordb = self._get_remote_db().select(ovl)
            except UnknownOverlayException:
                message = 'Overlay "%s" could not be found in the remote lists.\n' \
                        'Please check if it has been renamed and re-add if necessary.' % ovl
                warnings.append((ovl, message))
            else:
                current_src = odb.sources[0].src
                available_srcs = set(e.src for e in ordb.sources)
                if ordb and odb and not current_src in available_srcs:
                    if len(available_srcs) == 1:
                        plural = ''
                        candidates = '  %s' % tuple(available_srcs)[0]
                    else:
                        plural = 's'
                        candidates = '\n'.join(('  %d. %s' % (ovl + 1, v)) \
                         for ovl, v in enumerate(available_srcs))

                    warnings.append((ovl,
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
                            'repo_name':ovl,
                            'current_src':current_src,
                            'candidates':candidates,
                            'plural':plural,
                            }))

            try:
                db.sync(ovl, self.config['quiet'])
                success.append((ovl,'Successfully synchronized overlay "' + ovl + '".'))
            except Exception as error:
                fatals.append((ovl,
                    'Failed to sync overlay "' + ovl + '".\nError was: '
                    + str(error)))

        if output_results:
            if success:
                self.output.info('\nSucceeded:\n------\n', 3)
                for ovl, result in success:
                    self.output.info(result, 3)

            if warnings:
                self.output.warn('\nWarnings:\n------\n', 2)
                for ovl, result in warnings:
                    self.output.warn(result + '\n', 2)

            if fatals:
                self.output.error('\nErrors:\n------\n')
                for ovl, result in fatals:
                    self.output.error(result + '\n')

        self.sync_results = (success, warnings, fatals)

        return fatals == []


    def fetch_remote_list(self):
        """Fetches the latest remote overlay list"""
        try:
            dbreload = self._get_remote_db().cache()
            self.output.debug(
                'LaymanAPI.fetch_remote_list(); cache updated = %s'
                % str(dbreload),8)
        except Exception as error:
            self._error('Failed to fetch overlay list!\n Original Error was: '
                    + str(error))
            return False
        self.get_available(dbreload)
        return True


    def get_available(self, dbreload=False):
        """returns the list of available overlays"""
        self.output.debug('LaymanAPI.get_available() dbreload = %s'
            % str(dbreload), 8)
        if self._available_ids is None or dbreload:
            self._available_ids = self._get_remote_db(dbreload).list_ids()
        return self._available_ids[:] or ['None']


    def get_installed(self, dbreload=False):
        """returns the list of installed overlays"""
        if self._installed_ids is None or dbreload:
            self._installed_ids = self._get_installed_db(dbreload).list_ids()
        return self._installed_ids[:]


    def _get_installed_db(self, dbreload=False):
        """returns the list of installed overlays"""
        if not self._installed_db or dbreload:
            self._installed_db = DB(self.config)
        return self._installed_db


    def _get_remote_db(self, dbreload=False):
        """returns the list of installed overlays"""
        if self._available_db is None or dbreload:
            self._available_db = RemoteDB(self.config)
        return self._available_db


    def reload(self):
        """reloads the installed and remote db's to the data on disk"""
        result = self.get_available(dbreload=True)
        result = self.get_installed(dbreload=True)


    def _error(self, message):
        """outputs the error to the pre-determined output
        defaults to stderr.  This method may be removed, is here for now
        due to code taken from the packagekit backend.
        """
        self._error_messages.append(message)
        if self.report_errors:
            print(message, file=self.config['stderr'])


    def get_errors(self):
        """returns any warning or fatal messages that occurred during
        an operation and resets it back to None

        @rtype: list
        @return: list of error strings
        """
        if len(self._error_messages):
            messages =  self._error_messages[:]
            self._error_messages = []
            return messages
        return []


def create_fd():
    """creates file descriptor pairs an opens them ready for
    use in place of stdin, stdout, stderr.
    """
    fd_r, fd_w = os.pipe()
    write = os.fdopen(fd_w, 'w')
    rread = os.fdopen(fd_r, 'r')
    return (read, write, fd_r, fd_w)


