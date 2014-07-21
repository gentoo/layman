#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN CONFIGURATION
#################################################################################
# File:       argsparser.py
#
#             Handles layman command line interface configuration
#
# Copyright:
#             (c) 2005 - 2009 Gunnar Wrobel
#             (c) 2009        Sebastian Pipping
#             (c) 2010 - 2011 Brian Dolbec
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Sebastian Pipping <sebastian@pipping.org>
#             Brian Dolbec <brian.dolbec@gmail.com>
#
'''Defines the configuration options and provides parsing functionality.'''

from __future__ import unicode_literals

__version__ = "$Id: config.py 286 2007-01-09 17:48:23Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys

from argparse import ArgumentParser

from layman.config import BareConfig
from layman.constants import OFF
from layman.version import VERSION


_USAGE = """
  layman (-a|-d|-r|-s|-i) (OVERLAY|ALL)
  # it also supports multiple actions
  layman (-a|-d|-r|-s|-i) (OVERLAY|ALL) [ [(-a|-d|-r|-s|-i) (OVERLAY)] ...]
  layman -f [-o URL]
  layman (-l|-L|-S)"""


class ArgsParser(BareConfig):
    '''Handles the configuration and option parser.'''

    def __init__(self, args=None, stdout=None, stdin=None, stderr=None,
                root=None
                ):
        '''
        Creates and describes all possible polymeraZe options and creates
        a Message object.
        '''
        BareConfig.__init__(self, stdout=stdout, stderr=stderr,
                            stdin=stdin, root=root)

        # get a couple BareConfig items
        self.defaults = self.get_defaults()
        self.output = self.get_option('output')

        self.parser = ArgumentParser(
            usage   = _USAGE)

        self.parser.add_argument('-H',
                        '--setup_help',
                        action = 'store_true',
                        help = 'Print the NEW INSTALL help messages.')

        self.parser.add_argument('-V',
                          '--version',
                          action = 'version',
                          version = VERSION)

        #-----------------------------------------------------------------
        # Main Options

        actions = self.parser.add_argument_group('<Actions>')

        actions.add_argument('-a',
                             '--add',
                             action = 'append',
                             help = 'Add the given overlay from the cached remote li'
                             'st to your locally installed overlays.. Specify "ALL" '
                             'to add all overlays from the remote list.')

        actions.add_argument('-d',
                             '--delete',
                             action = 'append',
                             help = 'Remove the given overlay from your locally inst'
                             'alled overlays. Specify "ALL" to remove all overlays.')

        actions.add_argument('-f',
                             '--fetch',
                             action = 'store_true',
                             help = 'Fetch a remote list of overlays. This option is'
                             ' deprecated. The fetch operation will be performed by '
                             'default when you run sync, sync-all, or list.')

        actions.add_argument('-i',
                             '--info',
                             action = 'append',
                             help = 'Display information about the specified overlay'
                             '.')

        actions.add_argument('-L',
                             '--list',
                             action = 'store_true',
                             help = 'List the contents of the remote list.')

        actions.add_argument('-l',
                             '--list-local',
                             action = 'store_true',
                             help = 'List the locally installed overlays.')

        actions.add_argument('-n',
                             '--nofetch',
                             action = 'store_true',
                             help = 'Do not fetch a remote list of overlays.')

        actions.add_argument('-p',
                             '--priority',
                             action = 'store',
                             help = 'Use this with the --add switch to set the prior'
                             'ity of the added overlay. This will influence the sort'
                             'ing order of the overlays in the PORTDIR_OVERLAY varia'
                             'ble.')

        actions.add_argument('-r',
                             '--readd',
                             action = 'append',
                             help = 'Remove and re-add the given overlay from the cached'
                             ' remote list to your locally installed overlays... Specify'
                             ' "ALL" to re-add all local overlays.')

        actions.add_argument('-s',
                             '--sync',
                             action = 'append',
                             help = 'Update the specified overlay. Use "ALL" as para'
                            'meter to synchronize all overlays.')

        actions.add_argument('-S',
                             '--sync-all',
                             action = 'store_true',
                             help = 'Update all overlays.')

        #-----------------------------------------------------------------
        # Additional Options

        path_opts = self.parser.add_argument_group('<Path options>')

        path_opts.add_argument('-c',
                               '--config',
                               action = 'store',
                               default = self.defaults['config'],
                               # Force interpolation (to prevent argparse tracebacks)
                               help = 'Path to the config file [default: '
                               '%s].' % (self.defaults['config'] %self.defaults))

        path_opts.add_argument('-C',
                               '--configdir',
                               action = 'store',
                               default = '/etc/layman',
                               help = 'Directory path to user for all layman configu'
                               'ration information [default: /etc/layman].')

        path_opts.add_argument('-o',
                               '--overlays',
                               action = 'append',
                               help = 'The list of overlays [default: ' \
                               + self.defaults['overlays'] + '].')

        path_opts.add_argument('-O',
                               '--overlay_defs',
                               action = 'store',
                               default = self.defaults['overlay_defs'],
                               # Force interpolation (to prevent argparse tracebacks)
                               help = 'Path to aditional overlay.xml files [default: '
                               '%s].' % (self.defaults['overlay_defs'] %self.defaults))

        #-----------------------------------------------------------------
        # Output Options

        out_opts = self.parser.add_argument_group('<Output options>')

        out_opts.add_argument('--debug-level',
                              action = 'store',
                              type = int,
                              help = 'A value between 0 and 10. 0 means no debugging '
                              'messages will be selected, 10 selects all debugging me'
                              'ssages. Default is "4".')

        out_opts.add_argument('-k',
                              '--nocheck',
                              action = 'store_true',
                              help = 'Do not check overlay definitions and do not i'
                              'ssue a warning if description or contact information'
                              ' are missing.')

        out_opts.add_argument('-N',
                              '--nocolor',
                              action = 'store_true',
                              help = 'Remove color codes from the layman output.')

        out_opts.add_argument('-q',
                              '--quiet',
                              action = 'store_true',
                              help = 'Yield no output. Please be careful with this op'
                              'tion: If the processes spawned by layman when adding o'
                              'r synchronizing overlays require any input layman will'
                              ' hang without telling you why. This might happen for e'
                              'xample if your overlay resides in subversion and the S'
                              'SL certificate of the server needs acceptance.')

        out_opts.add_argument('-Q',
                              '--quietness',
                              action = 'store',
                              type = int,
                              default = 4,
                              help = 'Set the level of output (0-4). Default: 4. Once'
                              ' you set this below 2 the same warning as given for --'
                              'quiet applies!')

        out_opts.add_argument('-v',
                              '--verbose',
                              action = 'store_true',
                              help = 'Increase the amount of output and describe the '
                              'overlays.')

        out_opts.add_argument('-W',
                              '--width',
                              action = 'store',
                              type = int,
                              default = 0,
                              help = 'Sets the screen width. This setting is usually '
                              'not required as layman is capable of detecting the '
                              'available number of columns automatically.')

        #-----------------------------------------------------------------
        # Debug Options

        #self.output.cli_opts(self.parser)

        # Parse the command line first since we need to get the config
        # file option.

        # If no flags are present print out usage
        if len(sys.argv) == 1:
            self.output.notice('usage:%s' % _USAGE)
            sys.exit(0)

        self.options = self.parser.parse_args()
        self.options = vars(self.options)
        # Applying interpolation of values
        for v in ['configdir', 'config', 'overlay_defs']:
            self.options[v] = self.options[v] % self.options
            self.defaults[v] = self.options[v]

        if ('debug_level' in self.options and
            self.options['debug_level']):
            dbglvl = int(self.options['debug_level'])
            if dbglvl < 0:
                dbglvl = 0
            if dbglvl > 10:
                dbglvl = 10
            self.output.set_debug_level(dbglvl)

        if self.options['nocolor']:
            self.output.set_colorize(OFF)

        # Set only alternate config settings from the options
        if self.options['config'] is not None:
            self.defaults['config'] = self.options['config']
            self.output.debug('ARGSPARSER: Got config file at ' + \
                self.defaults['config'], 8)
        else: # fix the config path
            self.defaults['config'] = self.defaults['config'] \
                % {'configdir': self.defaults['configdir']}

        if self.options['overlay_defs'] is not None:
            self.defaults['overlay_defs'] = self.options['overlay_defs']
            self.output.debug('ARGSPARSER: Got overlay_defs location at ' + \
                self.defaults['overlay_defs'], 8)

        self._options['setup_help'] = self.options['setup_help']

        # Now parse the config file
        self.output.debug('ARGSPARSER: Reading config file at ' + \
            self.defaults['config'], 8)
        self.read_config(self.defaults)

        # handle quietness
        if self.options['quiet']:
            self.set_option('quiet', True)
        elif self.options['quietness']:
            self.set_option('quietness', self.options['quietness'])


    def __getitem__(self, key):

        if key == 'overlays':
            overlays = ''
            if (key in self.options.keys()
                and not self.options[key] is None):
                overlays = '\n'.join(self.options[key])
            if self.config.has_option('MAIN', 'overlays'):
                overlays += '\n' + self.config.get('MAIN', 'overlays')
            if len(overlays):
                return  overlays

        self.output.debug('ARGSPARSER: Retrieving options option: %s' % key, 9)

        if (key in self.options.keys()
            and not self.options[key] is False):
            return self.options[key]

        self.output.debug('ARGSPARSER: Retrieving config option: %s' % key, 9)

        if self.config.has_option('MAIN', key):
            if key in self._defaults['t/f_options']:
                return self.t_f_check(self.config.get('MAIN', key))
            return self.config.get('MAIN', key)

        self.output.debug('ARGSPARSER: Retrieving option: %s' % key, 9)

        if key in self._options.keys():
            return self._options[key]

        if key in self.defaults.keys():
            return self.defaults[key]

        self.output.debug('ARGSPARSER: Retrieving option failed. returning None', 9)

        return None


    def keys(self):
        '''Special handler for the configuration keys.'''

        self.output.debug('ARGSPARSER: Retrieving keys', 9)

        keys = [i for i in self.options
                if not self.options[i] is False
                and not self.options[i] is None]

        self.output.debug('ARGSPARSER: Retrieving keys 2', 9)

        keys += [name for name, _ in self.config.items('MAIN')
                 if not name in keys]

        self.output.debug('ARGSPARSER: Retrieving keys 3', 9)

        keys += [i for i in self.defaults.keys()
                 if not i in keys]
        self.output.debug('ARGSPARSER: Returning keys', 9)

        return keys


#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(sys.modules[__name__])
