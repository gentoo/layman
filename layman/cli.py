#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN ACTIONS
#################################################################################
# File:       cli.py
#
#             Handles layman actions via the command line interface.
#
# Copyright:
#             (c) 2010 - 2011
#                   Gunnar Wrobel
#                   Brian Dolbec
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Brian Dolbec <brian.dolbec@gmail.com
#
''' Provides the command line actions that can be performed by layman.'''

from __future__ import unicode_literals

__version__ = "$Id: cli.py 2011-01-15 23:52 PST Brian Dolbec$"


import os, sys

from layman.api import LaymanAPI
from layman.utils import (decode_selection, encoder, get_encoding,
    pad, terminal_width)
from layman.constants import (NOT_OFFICIAL_MSG, NOT_SUPPORTED_MSG,
    FAILURE, SUCCEED)

if sys.hexversion >= 0x30200f0:
    ALL_KEYWORD = b'ALL'
else:
    ALL_KEYWORD = 'ALL'

class ListPrinter(object):
    def __init__(self, config):
        self.config = config
        self.output = self.config['output']
        if not self.config['width']:
            self.width = terminal_width()-1
        else:
            self.width = self.config['width']
        self.srclen = self.width - 43
        self._encoding_ = get_encoding(self.output)
        if config['verbose']:
            self.my_lister = self.short_list # self.long_list
        else:
            self.my_lister = self.short_list

    def print_shortdict(self, info, complain):
        #print "ListPrinter.print_shortdict()",info, "\n\n"
        overlays = sorted(info)
        #print "ids =======>", overlays, "\n"
        for ovl in overlays:
            overlay = info[ovl]
            #print "overlay =", overlay
            summary, supported, official = overlay
            self.print_overlay(summary, supported, official, complain)

    def print_shortlist(self, info, complain):
        for summary, supported, official in info:
            self.print_overlay(summary, supported, official, complain)


    def print_fulldict(self, info, complain):
        ids = sorted(info)
        #print "ids =======>", ids, "\n"
        for ovl in ids:
            overlay = info[ovl]
            #print overlay
            self.print_overlay(self.my_lister(overlay),
                               overlay['supported'],
                               overlay['official'],
                               complain)


    def print_overlay(self, summary, supported, official, complain):
        # Is the overlay supported?
        if supported:
            # Is this an official overlay?
            if official:
                self.output.info(summary, 1)
            # Unofficial overlays will only be listed if we are not
            # checking or listing verbose
            elif complain:
                # Give a reason why this is marked yellow if it is a verbose
                # listing
                if self.config['verbose']:
                    self.output.warn(NOT_OFFICIAL_MSG, 1)
                self.output.warn(summary, 1)
        # Unsupported overlays will only be listed if we are not checking
        # or listing verbose
        elif complain:
            # Give a reason why this is marked red if it is a verbose
            # listing
            prev_state = self.output.block_callback
            self.output.block_callback = True
            if self.config['verbose']:
                self.output.error(NOT_SUPPORTED_MSG)
            self.output.error(summary)
            self.output.block_callback = prev_state


    def short_list(self, overlay):
        '''
        >>> print(short_list(overlay))
        wrobel                    [Subversion] (https://o.g.o/svn/dev/wrobel         )
        '''
        name   = pad(overlay['name'], 25)

        if len(set(e for e in overlay['src_types'])) == 1:
            _type = overlay['src_types'][0]
        else:
            _type = '%s/..' % overlay['src_type'][0]
        mtype  = ' [' + pad(_type, 10) + ']'

        source = ', '.join(overlay['src_uris'])

        if len(source) > self.srclen:
            source = source.replace("overlays.gentoo.org", "o.g.o")
        source = ' (' + pad(source, self.srclen) + ')'

        return encoder(name + mtype + source, self._encoding_)


class Main(object):
    '''Performs the actions the user selected.
    '''

    def __init__(self, config):
        self.config = config
        self.output = config['output']
        self.api = LaymanAPI(config,
                             report_errors=False,
                             output=config.output)
        # Given in order of precedence
        self.actions = [('fetch',      'Fetch'),
                        ('add',        'Add'),
                        ('sync',       'Sync'),
                        ('info',       'Info'),
                        ('sync_all',   'Sync'),
                        ('readd',      'Readd'),
                        ('delete',     'Delete'),
                        ('list',       'ListRemote'),
                        ('list_local', 'ListLocal'),]

    def __call__(self):
        self.output.debug("CLI.__call__(): self.config.keys()"
            " %s" % str(self.config.keys()), 6)
        # blank newline  -- no " *"
        self.output.notice('')

        # check for and handle setup-help option
        if self.config.get_option('setup_help'):
            from layman.updater import Main as Updater
            updater = Updater(config=self.config, output=self.output)
            updater.print_instructions()

        # Make fetching the overlay list a default action
        if not 'nofetch' in self.config.keys():
            # Actions that implicitely call the fetch operation before
            fetch_actions = ['sync', 'sync_all', 'list']
            for i in fetch_actions:
                if i in self.config.keys():
                    # Implicitely call fetch, break loop
                    self.Fetch()
                    break

        result = 0

        # Set the umask
        umask = self.config['umask']
        try:
            new_umask = int(umask, 8)
            old_umask = os.umask(new_umask)
        except Exception as error:
            self.output.die('Failed setting to umask "' + umask +
                '"!\nError was: ' + str(error))

        action_errors = []
        results = []
        act=set([x[0] for x in self.actions])
        k=set([x for x in self.config.keys()])
        a=act.intersection(k)
        self.output.debug('Actions = %s' % str(a), 4)
        for action in self.actions:
            self.output.debug('Checking for action %s' % action[0], 4)

            if action[0] in self.config.keys():
                result += getattr(self, action[1])()
                _errors = self.api.get_errors()
                if _errors:
                    self.output.debug("CLI: found errors performing "
                        "action %s" % action[0], 2)
                    action_errors.append((action[0], _errors))
                    result = -1  # So it cannot remain 0, i.e. success
            results.append(result)
            self.output.debug('Completed action %s, result %s'
                % (action[0], result==0), 4)

        self.output.debug('Checking for action errors', 4)
        if action_errors:
            for action, _errors in action_errors:
                self.output.warn("CLI: Errors occurred processing action"
                    " %s" % action)
                for _error in _errors:
                    self.output.error(_error)
                self.output.notice("")

        # Reset umask
        os.umask(old_umask)

        if -1 in results:
            sys.exit(FAILURE)
        else:
            sys.exit(SUCCEED)


    def Fetch(self):
        ''' Fetches the overlay listing.
        '''
        self.output.info("Fetching remote list,...", 2)
        result = self.api.fetch_remote_list()
        if result:
            self.output.info('Fetch Ok', 2)
        # blank newline  -- no " *"
        self.output.notice('')
        return result


    def Add(self):
        ''' Adds the selected overlays.
        '''
        self.output.info("Adding overlay,...", 2)
        selection = decode_selection(self.config['add'])
        if ALL_KEYWORD in selection:
            selection = self.api.get_available()
        self.output.debug('Adding selected overlays', 6)
        result = self.api.add_repos(selection, update_news=True)
        if result:
            self.output.info('Successfully added overlay(s) ' +
                ', '.join((x.decode('UTF-8') if isinstance(x, bytes) else x) for x in selection) +
                '.', 2)
        # blank newline  -- no " *"
        self.output.notice('')
        return result


    def Readd(self):
        '''Readds the selected overlay(s).
        '''
        self.output.info('Reinstalling overlay(s),...', 2)
        selection = decode_selection(self.config['readd'])
        if ALL_KEYWORD in selection:
            selection = self.api.get_installed()
        self.output.debug('Reinstalling selected overlay(s)', 6)
        result = self.api.readd_repos(selection, update_news=True)
        if result:
            self.output.info('Successfully reinstalled overlay(s) ' +
                ', '.join((x.decode('UTF-8') if isinstance(x, bytes) else x) for x in selection)
                + '.', 2)
        self.output.notice('')
        return result


    def Sync(self):
        ''' Syncs the selected overlays.
        '''
        self.output.info("Syncing selected overlays,...", 2)
        # Note api.sync() defaults to printing results
        selection = decode_selection(self.config['sync'])
        if self.config['sync_all'] or ALL_KEYWORD in selection:
            selection = self.api.get_installed()
        self.output.debug('Updating selected overlays', 6)
        result = self.api.sync(selection, update_news=True)
        # blank newline  -- no " *"
        self.output.notice('')
        return result


    def Delete(self):
        ''' Deletes the selected overlays.
        '''
        self.output.info('Deleting selected overlays,...', 2)
        selection = decode_selection(self.config['delete'])
        if ALL_KEYWORD in selection:
            selection = self.api.get_installed()
        result = self.api.delete_repos(selection)
        if result:
            self.output.info('Successfully deleted overlay(s) ' +
                ', '.join((x.decode('UTF-8') if isinstance(x, bytes) else x) for x in selection) +
                '.', 2)
        # blank newline  -- no " *"
        self.output.notice('')
        return result


    def Info(self):
        ''' Print information about the specified overlays.
        '''
        selection = decode_selection(self.config['info'])
        if ALL_KEYWORD in selection:
            selection = self.api.get_available()

        list_printer = ListPrinter(self.config)
        _complain = self.config['nocheck'] or self.config['verbose']

        info = self.api.get_info_str(selection, local=False,
            verbose=True, width=list_printer.width)
        list_printer.print_shortdict(info, complain=_complain)
        # blank newline  -- no " *"
        self.output.notice('')
        return info != {}


    def ListRemote(self):
        ''' Lists the available overlays.
        '''

        self.output.debug('Printing remote overlays.', 6)
        list_printer = ListPrinter(self.config)

        _complain = self.config['nocheck'] or self.config['verbose']
        info = self.api.get_info_list(local=False,
            verbose=self.config['verbose'], width=list_printer.width)
        list_printer.print_shortlist(info, complain=_complain)
        # blank newline  -- no " *"
        self.output.notice('')

        return info != {}


    def ListLocal(self):
        ''' Lists the local overlays.
        '''
        #print "ListLocal()"
        self.output.debug('Printing installed overlays.', 6)
        list_printer = ListPrinter(self.config)

        #
        # fast way
        info = self.api.get_info_list(verbose=self.config['verbose'],
                                      width=list_printer.width)
        #self.output.debug('CLI: ListLocal() info = %s' % len(info), 4)
        #self.output.debug('\n'.join([ str(x) for x in info]), 4)
        list_printer.print_shortlist(info, complain=True)
        #
        # slow way
        #info = self.api.get_all_info(self.api.get_installed(), local=True)
        #list_printer.print_fulldict(info, complain=_complain)

        # blank newline  -- no " *"
        self.output.notice('')
        return info != {}


if __name__ == '__main__':
    import doctest

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
