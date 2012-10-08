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


__version__ = "$Id: config.py 286 2007-01-09 17:48:23Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys

from optparse import OptionParser, OptionGroup

from layman.config import BareConfig
from layman.constants import OFF
from layman.version import VERSION


_USAGE = """
  layman (-a|-d|-s|-i) (OVERLAY|ALL)
  # it also supports multiple actions
  layman (-a|-d|-s|-i) (OVERLAY|ALL) [ [(-a|-d|-s|-i) (OVERLAY)] ...]
  layman -f [-o URL]
  layman (-l|-L|-S)"""


class ArgsParser(BareConfig):
    '''Handles the configuration and option parser.'''

    def __init__(self, args=None, stdout=None, stdin=None, stderr=None):
        '''
        Creates and describes all possible polymeraZe options and creates
        a Message object.

        >>> import os.path
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> sys.argv.append('--config')
        >>> sys.argv.append(here + '/../etc/layman.cfg')
        >>> sys.argv.append('--overlay_defs')
        >>> sys.argv.append('')
        >>> a = ArgsParser()
        >>> a['overlays']
        '\\nhttp://www.gentoo.org/proj/en/overlays/repositories.xml'
        >>> sorted(a.keys())
        ['bzr_addopts', 'bzr_command', 'bzr_postsync', 'bzr_syncopts', 'cache', 'config', 'configdir', 'custom_news_pkg', 'cvs_addopts', 'cvs_command', 'cvs_postsync', 'cvs_syncopts', 'darcs_addopts', 'darcs_command', 'darcs_postsync', 'darcs_syncopts', 'g-common_command', 'g-common_generateopts', 'g-common_postsync', 'g-common_syncopts', 'git_addopts', 'git_command', 'git_email', 'git_postsync', 'git_syncopts', 'git_user', 'installed', 'local_list', 'make_conf', 'mercurial_addopts', 'mercurial_command', 'mercurial_postsync', 'mercurial_syncopts', 'news_reporter', 'nocheck', 'overlay_defs', 'overlays', 'proxy', 'quietness', 'rsync_command', 'rsync_postsync', 'rsync_syncopts', 'storage', 'svn_addopts', 'svn_command', 'svn_postsync', 'svn_syncopts', 't/f_options', 'tar_command', 'tar_postsync', 'umask', 'width']
                '''

        BareConfig.__init__(self, stdout=stdout, stderr=stderr, stdin=stdin)
        if args == None:
            args = sys.argv

        # get a couple BareConfig items
        self.defaults = self.get_defaults()
        self.output = self.get_option('output')

        self.parser = OptionParser(
            usage   = _USAGE,
            version = VERSION)

        #-----------------------------------------------------------------
        # Main Options

        group = OptionGroup(self.parser,
                            '<Actions>')

        group.add_option('-a',
                         '--add',
                         action = 'append',
                         help = 'Add the given overlay from the cached remote li'
                         'st to your locally installed overlays.. Specify "ALL" '
                         'to add all overlays from the remote list.')

        group.add_option('-d',
                         '--delete',
                         action = 'append',
                         help = 'Remove the given overlay from your locally inst'
                         'alled overlays. Specify "ALL" to remove all overlays')

        group.add_option('-s',
                         '--sync',
                         action = 'append',
                         help = 'Update the specified overlay. Use "ALL" as para'
                         'meter to synchronize all overlays')

        group.add_option('-i',
                         '--info',
                         action = 'append',
                         help = 'Display information about the specified overlay'
                         '.')

        group.add_option('-S',
                         '--sync-all',
                         action = 'store_true',
                         help = 'Update all overlays.')

        group.add_option('-L',
                         '--list',
                         action = 'store_true',
                         help = 'List the contents of the remote list.')

        group.add_option('-l',
                         '--list-local',
                         action = 'store_true',
                         help = 'List the locally installed overlays.')

        group.add_option('-f',
                         '--fetch',
                         action = 'store_true',
                         help = 'Fetch a remote list of overlays. This option is'
                         ' deprecated. The fetch operation will be performed by '
                         'default when you run sync, sync-all, or list.')

        group.add_option('-n',
                         '--nofetch',
                         action = 'store_true',
                         help = 'Do not fetch a remote list of overlays.')

        group.add_option('-p',
                         '--priority',
                         action = 'store',
                         help = 'Use this with the --add switch to set the prior'
                         'ity of the added overlay. This will influence the sort'
                         'ing order of the overlays in the PORTDIR_OVERLAY varia'
                         'ble.')

        self.parser.add_option_group(group)

        #-----------------------------------------------------------------
        # Additional Options

        group = OptionGroup(self.parser,
                            '<Path options>')

        group.add_option('-c',
                         '--config',
                         action = 'store',
                         help = 'Path to the config file [default: ' \
                         + self.defaults['config'] + '].')

        group.add_option('-O',
                         '--overlay_defs',
                         action = 'store',
                         help = 'Path to aditional overlay.xml files [default: '\
                         + self.defaults['overlay_defs'] + '].')

        group.add_option('-o',
                         '--overlays',
                         action = 'append',
                         help = 'The list of overlays [default: ' \
                         + self.defaults['overlays'] + '].')

        self.parser.add_option_group(group)

        #-----------------------------------------------------------------
        # Output Options

        group = OptionGroup(self.parser,
                            '<Output options>')

        group.add_option('-v',
                         '--verbose',
                         action = 'store_true',
                         help = 'Increase the amount of output and describe the '
                         'overlays.')

        group.add_option('-q',
                         '--quiet',
                         action = 'store_true',
                         help = 'Yield no output. Please be careful with this op'
                         'tion: If the processes spawned by layman when adding o'
                         'r synchronizing overlays require any input layman will'
                         ' hang without telling you why. This might happen for e'
                         'xample if your overlay resides in subversion and the S'
                         'SL certificate of the server needs acceptance.')

        group.add_option('-N',
                         '--nocolor',
                         action = 'store_true',
                         help = 'Remove color codes from the layman output.')

        group.add_option('-Q',
                         '--quietness',
                         action = 'store',
                         type = 'int',
                         default = '4',
                         help = 'Set the level of output (0-4). Default: 4. Once'
                         ' you set this below 2 the same warning as given for --'
                         'quiet applies! ')

        group.add_option('-W',
                         '--width',
                         action = 'store',
                         type = 'int',
                         default = '0',
                         help = 'Sets the screen width. This setting is usually '
                         'not required as layman is capable of detecting the '
                         'available number of columns automatically.')

        group.add_option('-k',
                         '--nocheck',
                         action = 'store_true',
                         help = 'Do not check overlay definitions and do not i'
                         'ssue a warning if description or contact information'
                         ' are missing.')

        group.add_option('--debug-level',
                         action = 'store',
                         type = 'int',
                         help = 'A value between 0 and 10. 0 means no debugging '
                         'messages will be selected, 10 selects all debugging me'
                         'ssages. Default is "4".')


        self.parser.add_option_group(group)

        #-----------------------------------------------------------------
        # Debug Options

        #self.output.cli_opts(self.parser)

        # Parse the command line first since we need to get the config
        # file option.
        if len(args) == 1:
            self.output.notice('Usage:%s' % _USAGE)
            sys.exit(0)

        (self.options, remain_args) = self.parser.parse_args(args)
        # remain_args starts with something like "bin/layman" ...
        if len(remain_args) > 1:
            self.parser.error("ArgsParser(): Unhandled parameters: %s"
                % ', '.join(('"%s"' % e) for e in remain_args[1:]))

        # handle debugging
        #self.output.cli_handle(self.options)

        if (self.options.__dict__.has_key('debug_level') and
            self.options.__dict__['debug_level']):
            dbglvl = int(self.options.__dict__['debug_level'])
            if dbglvl < 0:
                dbglvl = 0
            if dbglvl > 10:
                dbglvl = 10
            self.output.set_debug_level(dbglvl)

        if self.options.__dict__['nocolor']:
            self.output.set_colorize(OFF)

        # Set only alternate config settings from the options
        if self.options.__dict__['config'] is not None:
            self.defaults['config'] = self.options.__dict__['config']
            self.output.debug('ARGSPARSER: Got config file at ' + \
                self.defaults['config'], 8)
        else: # fix the config path
            self.defaults['config'] = self.defaults['config'] \
                % {'configdir': self.defaults['configdir']}
        if self.options.__dict__['overlay_defs'] is not None:
            self.defaults['overlay_defs'] = self.options.__dict__['overlay_defs']
            self.output.debug('ARGSPARSER: Got overlay_defs location at ' + \
                self.defaults['overlay_defs'], 8)

        # Now parse the config file
        self.output.debug('ARGSPARSER: Reading config file at ' + \
            self.defaults['config'], 8)
        self.read_config(self.defaults)

        # handle quietness
        if self.options.__dict__['quiet']:
            self.set_option('quiet', True)
        elif self.options.__dict__['quietness']:
            self.set_option('quietness', self.options.__dict__['quietness'])


    def __getitem__(self, key):

        if key == 'overlays':
            overlays = ''
            if (key in self.options.__dict__.keys()
                and not self.options.__dict__[key] is None):
                overlays = '\n'.join(self.options.__dict__[key])
            if self.config.has_option('MAIN', 'overlays'):
                overlays += '\n' + self.config.get('MAIN', 'overlays')
            if len(overlays):
                return  overlays

        self.output.debug('ARGSPARSER: Retrieving options option: %s' % key, 9)

        if (key in self.options.__dict__.keys()
            and not self.options.__dict__[key] is None):
            return self.options.__dict__[key]

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

        keys = [i for i in self.options.__dict__.keys()
                if not self.options.__dict__[i] is None]

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
