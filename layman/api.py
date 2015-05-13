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

from __future__ import unicode_literals
from __future__ import print_function

import os
import sys

from layman.config          import BareConfig
from layman.dbbase          import UnknownOverlayException, UnknownOverlayMessage
from layman.db              import DB
from layman.remotedb        import RemoteDB
from layman.overlays.source import require_supported
#from layman.utils import path, delete_empty_directory
from layman.compatibility   import encode
from layman.utils           import get_ans, verify_overlay_src
from layman.mounter         import Mounter

if sys.hexversion >= 0x30200f0:
    STR = str
else:
    STR = basestring

UNKNOWN_REPO_ID = "Repo ID '%s' " + \
        "is not listed in the current available overlays list"

class LaymanAPI(object):
    """class to hold and run a layman instance for use by API consumer apps, guis, etc.
    """

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

        self.config.set_option('mounts', Mounter(self._get_installed_db,
                                                 self.get_installed,
                                                 config=self.config))


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
        if isinstance(repos, STR):
            repos = [repos]
        # else assume it is an iterable, if not it will error
        return [encode(i) for i in repos]


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
                self.output.error("Repository '"+ovl+"' was not installed")
                results.append(False)
                continue
            success = False
            try:
                success = self._get_installed_db().delete(
                    self._get_installed_db().select(ovl))
            except Exception as e:
                self._error('Exception caught removing repository "%(repo)s":\n'
                            '%(err)s' % {'repo': ovl, 'err': e})
            results.append(success)
            self.get_installed(dbreload=True)
        if False in results:
            return False
        return True


    def add_repos(self, repos, update_news=False):
        """installs the seleted repo id

        @type repos: list of strings or string
        @param repos: ['repo-id', ...] or 'repo-id'
        @param update_news: bool, defaults to False
        @rtype dict
        """
        repos = self._check_repo_type(repos, "add_repo")
        results = []
        for ovl in repos:
            if self.is_installed(ovl):
                self.output.error("Repository '"+ovl+"' was already installed")
                results.append(False)
                continue
            if not self.is_repo(ovl):
                self.output.error(UnknownOverlayMessage(ovl))
                results.append(False)
                continue
            success = False
            try:
                success = self._get_installed_db().add(
                    self._get_remote_db().select(ovl))
            except Exception as e:
                self._error('Exception caught installing repository "%(repo)s":'
                            '\n%(err)s' % {'repo': ovl, 'err': e})
            results.append(success)
            self.get_installed(dbreload=True)
        if (True in results) and update_news:
            self.update_news(repos)

        if False in results:
            return False
        return True


    def readd_repos(self, repos, update_news=False):
        """reinstalls any given amount of repos
        by deleting them and readding them

        @type repos: list of strings or string
        @param repos: ['repo-id1', ...] or 'repo-id'
        """
        success = self.delete_repos(repos)
        if not success:
            return success
        success = self.add_repos(repos)
        if update_news:
            self.update_news(repos)
        return success


    def disable_repos(self, repos, update_news=False):
        repos = self._check_repo_type(repos, "disable_repo")
        results = []
        for ovl in repos:
            if not self.is_repo(ovl):
                self.output.error(UnknownOverlayMessage(ovl))
                result.append(False)
                continue
            success = False
            try:
                success = self._get_installed_db().disable(
                    self._get_installed_db().select(ovl))
            except Exception as e:
                self._error('Exception caught disabling repository "%(repo)s"'\
                            ':\n%(err)s' % {'repo': ovl, 'err': e})
            results.append(success)
            self.get_installed(dbreload=True)
        if (True in results) and update_news:
            self.update_news(repos)

        if False in results:
            return False
        return True


    def enable_repos(self, repos, update_news=False):
        repos = self._check_repo_type(repos, "enable_repo")
        results = []
        for ovl in repos:
            if not self.is_repo(ovl):
                self.output.error(UnknownOverlayMessage(ovl))
                result.append(False)
                continue
            success = False
            try:
                success = self._get_installed_db().enable(
                    self._get_installed_db().select(ovl))
            except Exception as e:
                self._error('Exception caught enabling repository "%(repo)s"'\
                            ':\n%(err)s' % {'repo': ovl, 'err': e})
            results.append(success)
            self.get_installed(dbreload=True)
        if (True in results) and update_news:
            self.update_news(repos)

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
                self.output.error(UnknownOverlayMessage(ovl))
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
                    'description': [e for e in overlay.descriptions],
                    'feeds': overlay.feeds,
                    'sources': [(e.src, e.type, e.branch) \
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
                self.output.error(UnknownOverlayMessage(ovl))
                result[ovl] = ('', False, False)
                continue
            try:
                overlay = db.select(ovl)
                #print "overlay = ", ovl
                #print "!!!", overlay
            except UnknownOverlayException as error:
                #print "ERRORS", str(error)
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


    def _verify_overlay_type(self, odb, ordb):
        """
        Verifies the overlay type against the type reported by
        remote database.

        @param odb: local database of overlay information.
        @param ordb: remote database of overlay information.
        @rtype (boolean, msg)
        """
        remote_type = ordb.sources[0].type
        current_type = odb.sources[0].type

        if remote_type not in current_type:
            msg = 'The overlay type of overlay "%(repo_name)s" seems to have changed.\n'\
                  'The current overlay type is:\n'\
                  '\n'\
                  '  %(current_type)s\n'\
                  '\n'\
                  'while the remote overlay is of type:\n'\
                  '\n'\
                  '  %(remote_type)s\n'\
                  '\n'\
                  'the overlay will be readded using %(remote_type)s' %\
                  ({
                      'repo_name': odb.name,
                      'current_type': current_type,
                      'remote_type': remote_type,
                  })
            return True, msg
        return False, ''

    def _verify_overlay_source(self, odb, ordb):
        """
        Verifies the overlay source url against the source url(s)
        reported by the remote database.

        @param odb: local database of overlay information.
        @param ordb: remote database of overlay information.
        @rtype (boolean, msg)
        """
        current_src = odb.sources[0].src
        (available_srcs, valid) = verify_overlay_src(current_src,
            set(e.src for e in ordb.sources))

        if ordb and odb and not valid:
            if len(available_srcs) == 1:
                plural = ''
                candidates = '  %s' % tuple(available_srcs)[0]
            else:
                plural = 's'
                candidates = '\n'.join(('  %d. %s' % (ovl + 1, v)) \
                    for ovl, v in enumerate(available_srcs))
            msg = 'The source of the overlay "%(repo_name)s" seems to have changed.\n'\
                  'You currently sync from\n'\
                  '\n'\
                  '  %(current_src)s\n'\
                  '\n'\
                  'while the remote lists report\n'\
                  '\n'\
                  '%(candidates)s\n'\
                  '\n'\
                  'as correct location%(plural)s.\n'\
                  '\n'\
                  'Repo: "%(repo_name)s" was automatically updated...' %\
                  ({
                     'repo_name':odb.name,
                     'current_src':current_src,
                     'candidates':candidates,
                     'plural':plural,
                  })
            return True, msg, available_srcs
        return False, '', available_srcs

    def sync(self, repos, output_results=True, update_news=False):
        """syncs the specified repo(s) specified by repos

        @type repos: list of strings or string
        @param repos: ['repo-id1', ...] or 'repo-id'
        @param output_results: bool, defaults to True
        @param update_news: bool, defaults to False
        @rtype bool or {'repo-id': bool,...}
        """
        self.output.debug("API.sync(); repos to sync = %s" % ', '.join((x.decode() if isinstance(x, bytes) else x) for x in repos), 5)
        fatals = []
        warnings = []
        success  = []
        repos = self._check_repo_type(repos, "sync")
        db = self._get_installed_db()

        self.output.debug("API.sync(); starting ovl loop", 5)
        for ovl in repos:
            update_url = False
            self.output.debug("API.sync(); starting ovl = %s" %ovl, 5)
            try:
                #self.output.debug("API.sync(); selecting %s, db = %s" % (ovl, str(db)), 5)
                odb = db.select(ovl)
                self.output.debug("API.sync(); %s now selected" %ovl, 5)
            except UnknownOverlayException as error:
                #self.output.debug("API.sync(); UnknownOverlayException selecting %s" %ovl, 5)
                #self._error(str(error))
                fatals.append((ovl,
                    'Failed to select overlay "%(repo)s".\nError was: %(error)s'
                     % {'repo': ovl, 'err': error}))
                self.output.debug("API.sync(); UnknownOverlayException "
                    "selecting %(repo)s.   continuing to next ovl..."
                    % {'repo': ovl}, 5)
                continue

            try:
                self.output.debug("API.sync(); try: self._get_remote_db().select(ovl)", 5)
                ordb = self._get_remote_db().select(ovl)
            except UnknownOverlayException:
                message = 'Overlay "%(repo)s" could not be found in the remote '\
                        'lists.\nPlease check if it has been renamed and '\
                        're-add if necessary.' % {'repo': ovl}
                warnings.append((ovl, message))
                (diff_type, update_url) = (False, False)
            else:
                self.output.debug("API.sync(); else: self._get_remote_db().select(ovl)", 5)

                (diff_type, type_msg) = self._verify_overlay_type(odb, ordb)
                (update_url, url_msg, available_srcs) = self._verify_overlay_source(odb, ordb)

                try:
                    if diff_type:
                        self.output.debug("API.sync(); starting API.readd_repos(ovl)", 5)
                        warnings.append((ovl, type_msg))
                        self.readd_repos(ovl)
                        success.append((ovl, 'Successfully readded overlay "' + ovl + '".'))
                    else:
                        if update_url:
                            self.output.debug("API.sync() starting db.update(ovl)", 5)
                            warnings.append((ovl, url_msg))
                            update_success = db.update(ordb, available_srcs)
                            if not update_success:
                                msg = 'Failed to update source URL for overlay'\
                                      '"%(ovl)s". Re-add overlay? [y/n]'\
                                      % {'ovl': ovl}
                                if get_ans(msg, color='yellow'):
                                    self.readd_repos(ovl)
                except Exception as error:
                    self.output.warn('Failed to perform overlay type or url updates', 2)
                    self.output.warn('    for Overlay: %s' % ovl, 2)
                    self.output.warn('    Error was: %s' % str(error))
                    continue

            try:
                    self.output.debug("API.sync(); starting db.sync(ovl)", 5)
                    db.sync(ovl)
                    success.append((ovl,'Successfully synchronized overlay "' + ovl + '".'))
            except Exception as error:
                fatals.append((ovl,
                    'Failed to sync overlay "%(repo)s".\nError was: %(err)s'
                    % {'repo': ovl, 'err': error}))

        if output_results:
            if success:
                message = '\nSucceeded:\n------\n'
                for ovl, result in success:
                    message += result + '\n'
                self.output.info(message, 3)

            if warnings:
                message = '\nWarnings:\n------\n'
                for ovl, result in warnings:
                    message += result + '\n'
                self.output.warn(message, 2)

            if fatals:
                message = '\nErrors:\n------\n'
                for ovl, result in fatals:
                    message += result + '\n'
                self.output.error(message)

        self.sync_results = (success, warnings, fatals)

        if update_news:
            self.update_news(repos)

        return fatals == []


    def fetch_remote_list(self):
        """
        Fetches the latest remote overlay list.

        @rtype bool: reflects success/failure to fetch remote list.
        """

        try:
            dbreload, succeeded = self._get_remote_db().cache()
            self.output.debug(
                'LaymanAPI.fetch_remote_list(); cache updated = %s'
                % str(dbreload),8)
        except Exception as error:
            self.output.error('Failed to fetch overlay list!\n Original Error'
                              'was:\n%(err)s' % {'err': error})
            return False
        self.get_available(dbreload)
        return succeeded


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
        self.output.debug("API._get_installed_db; len(installed) = %s, %s"
            %(len(self._installed_db.list_ids()), self._installed_db.list_ids()), 5)
        return self._installed_db


    def _get_remote_db(self, dbreload=False):
        """returns the list of installed overlays"""
        if self._available_db is None or dbreload:
            self._available_db = RemoteDB(self.config)
        return self._available_db


    def reload(self):
        """reloads the installed and remote db's to the data on disk"""
        self.get_available(dbreload=True)
        self.get_installed(dbreload=True)


    def _error(self, message):
        """outputs the error to the pre-determined output
        defaults to stderr.  This method may be removed, is here for now
        due to code taken from the packagekit backend.
        """
        self._error_messages.append(message)
        self.output.debug("API._error(); _error_messages = %s" % str(self._error_messages), 4)
        if self.report_errors:
            print(message, file=self.config['stderr'])


    def get_errors(self):
        """returns any warning or fatal messages that occurred during
        an operation and resets it back to None

        @rtype: list
        @return: list of error strings
        """
        self.output.debug("API.get_errors(); _error_messages = %s" % str(self._error_messages), 4)
        if len(self._error_messages):
            messages =  self._error_messages[:]
            self._error_messages = []
            return messages
        return []


    def supported_types(self):
        """returns a dictionary of all repository types,
        with boolean values"""
        here = os.path.dirname(os.path.realpath(__file__))
        modpath = os.path.join('overlays', 'modules')
        modules = os.listdir(os.path.join(here, modpath))

        cmds = [x for x in self.config.keys() if '_command' in x]
        supported = {}
        for cmd in cmds:
            type_key = cmd.split('_')[0]
            # The module dir might be named differently from the type_key.
            # ex.) g-common and g-sorcery are named g_common and g_sorcery.
            module = type_key.replace('-', '_')

            # Don't bother executing require_supported() if the user didn't
            # bring in support for the overlay type in the first place.
            if module in modules:
                supported[type_key] = require_supported(
                    [(self.config[cmd],type_key, '')], self.output.warn)
            else:
                supported[type_key] = False
        return supported


    def update_news(self, repos=None):
        try:
            if self.config['news_reporter'] == 'portage':
                try:
                    from portage import db, root
                    from portage.news import count_unread_news, \
                        display_news_notifications
                    portdb = db[root]["porttree"].dbapi
                    vardb = db[root]["vartree"].dbapi
                    # get the actual repo_name from portage
                    # because it may be different than layman's name for it
                    repo_names = []
                    for repo in repos:
                        if isinstance(repo, bytes):
                            repo = repo.decode('UTF-8')
                        ovl = self._get_installed_db().select(repo)
                        ovl_path = os.path.join(ovl.config['storage'], repo)
                        name = portdb.getRepositoryName(ovl_path)
                        if name:
                            repo_names.append(name)
                    self.output.debug("LaymanAPI: update_news(); repo_names = "
                        + str(repo_names), 4)
                    news_counts = count_unread_news(portdb, vardb, repo_names)
                    display_news_notifications(news_counts)
                except ImportError:
                    # deprecated funtionality, remove when the above method
                    # is available in all portage versions
                    self.output.info("New portage news functionality not "
                        "available, using fallback method", 5)
                    from _emerge.actions import (display_news_notification,
                        load_emerge_config)
                    settings, trees, mtimedb = load_emerge_config()
                    display_news_notification(
                        trees[settings["ROOT"]]["root_config"], {})

            elif self.config['news_reporter'] == 'custom':
                if self.config['custom_news_func'] is None:
                    _temp = __import__(
                        'custom_news_pkg', globals(), locals(),
                        ['layman_news_func'], -1)
                    self.config['custom_news_func'] = _temp.custom_news_func
                self.config['custom_news_func'](repos)

            elif self.config['news_reporter'] == 'pkgcore':
                # pkgcore is not yet capable
                return
        except Exception as err:
            msg = "update_news() failed running %s news reporter function\n" +\
                  "Error was; %s"
            self._error(msg % (self.config['news_reporter'], err))
        return



def create_fd():
    """creates file descriptor pairs an opens them ready for
    use in place of stdin, stdout, stderr.
    """
    fd_r, fd_w = os.pipe()
    write = os.fdopen(fd_w, 'w')
    read = os.fdopen(fd_r, 'r')
    return (read, write, fd_r, fd_w)
