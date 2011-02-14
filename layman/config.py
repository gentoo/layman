#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN CONFIGURATION
#################################################################################
# File:       config.py
#
#             Handles layman configuration
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

import sys, ConfigParser
import os

from optparse import OptionParser, OptionGroup

#from layman.debug import OUT
from layman.output import OUT

from layman.constants import OFF
from layman.version import VERSION


_USAGE = """
  layman (-a|-d|-s|-i) (OVERLAY|ALL)
  layman -f [-o URL]
  layman (-l|-L|-S)"""


def read_config(config=None, defaults=None):
    """reads the config file defined in defaults['config']
    and updates the config

    @param config: ConfigParser.ConfigParser(self.defaults) instance
    @param defaults: dict
    @modifies config['MAIN']['overlays']
    """
    config.read(defaults['config'])
    if config.get('MAIN', 'overlay_defs'):
        try:
            filelist = os.listdir(config.get('MAIN', 'overlay_defs'))
        except OSError:
            return
        filelist = [f for f in filelist if f.endswith('.xml')]
        overlays = set(config.get('MAIN', 'overlays').split('\n'))
        for _file in filelist:
            path = os.path.join(config.get('MAIN', 'overlay_defs'), _file)
            if os.path.isfile(path):
                overlays.update(["file://" + path])
        config.set('MAIN', 'overlays', '\n'.join(overlays))



class BareConfig(object):
    '''Handles the configuration only.'''

    def __init__(self, output=None, stdout=None, stdin=None, stderr=None):
        '''
        Creates a bare config with defaults and a few output options.

        >>> a = BareConfig()
        >>> a['overlays']
        '\\nhttp://www.gentoo.org/proj/en/overlays/repositories.xml'
        >>> sorted(a.keys())
        ['bzr_command', 'cache', 'config', 'cvs_command', 'darcs_command',
        'git_command', 'local_list', 'make_conf', 'mercurial_command',
        'nocheck', 'overlays', 'proxy', 'quietness', 'rsync_command', 'storage',
        'svn_command', 'tar_command', 'umask', 'width']
        '''
        self._defaults = {'config'    : '/etc/layman/layman.cfg',
                    'storage'   : '/var/lib/layman',
                    'cache'     : '%(storage)s/cache',
                    'local_list': '%(storage)s/overlays.xml',
                    'make_conf' : '%(storage)s/make.conf',
                    'nocheck'   : 'yes',
                    'proxy'     : '',
                    'umask'     : '0022',
                    'overlays'  :
                    'http://www.gentoo.org/proj/en/overlays/repositories.xml',
                    'overlay_defs': '/etc/layman/overlays',
                    'bzr_command': '/usr/bin/bzr',
                    'cvs_command': '/usr/bin/cvs',
                    'darcs_command': '/usr/bin/darcs',
                    'git_command': '/usr/bin/git',
                    'g-common_command': '/usr/bin/g-common',
                    'mercurial_command': '/usr/bin/hg',
                    'rsync_command': '/usr/bin/rsync',
                    'svn_command': '/usr/bin/svn',
                    'tar_command': '/bin/tar'
                    }
        self._options = {
                    'stdout': stdout if stdout else sys.stdout,
                    'stdin': stdin if stdin else sys.stdin,
                    'stderr': stderr if stderr else sys.stderr,
                    'output': output if output else OUT,
                    'quietness': '4',
                    'width': 0,
                    'verbose': False,
                    'quiet': False,
                    }


    def keys(self):
        '''Special handler for the configuration keys.
        '''
        self._options['output'].debug('Retrieving BareConfig options', 8)
        keys = [i for i in self._options]
        self._options['output'].debug('Retrieving BareConfig defaults', 8)
        keys += [i for i in self._defaults
                 if not i in keys]
        self._options['output'].debug('Retrieving BareConfig done...', 8)
        return keys


    def get_defaults(self):
        """returns our defaults dictionary"""
        return self._defaults


    def get_option(self, key):
        """returns the current option's value"""
        return self.__getitem__(key)


    def set_option(self, option, value):
        """Sets an option to the value """
        self._options[option] = value


    def __getitem__(self, key):
        self._options['output'].debug('Retrieving BareConfig option', 8)
        if (key in self._options
            and not self._options[key] is None):
            return self._options[key]
        self._options['output'].debug('Retrieving BareConfig default', 8)
        if key in self._defaults:
            if '%(storage)s' in self._defaults[key]:
                return self._defaults[key] %{'storage': self._defaults['storage']}
            return self._defaults[key]
        return None




class ArgsParser(object):
    '''Handles the configuration and option parser.'''

    def __init__(self, args=None, output=None,
        stdout=None, stdin=None, stderr=None):
        '''
        Creates and describes all possible polymeraZe options and creates
        a debugging object.

        >>> import os.path
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> sys.argv.append('--config')
        >>> sys.argv.append(here + '/../etc/layman.cfg')
        >>> a = ArgsParser()
        >>> a['overlays']
        '\\nhttp://www.gentoo.org/proj/en/overlays/repositories.xml'
        >>> sorted(a.keys())
        ['bzr_command', 'cache', 'config', 'cvs_command', 'darcs_command',
        'git_command', 'local_list', 'make_conf', 'mercurial_command',
        'nocheck', 'overlays', 'proxy', 'quietness', 'rsync_command', 'storage',
        'svn_command', 'tar_command', 'umask', 'width']
        '''
        if args == None:
            args = sys.argv

        self.stdout = stdout if stdout else sys.stdout
        self.stderr = stderr if stderr else sys.stderr
        self.stdin = stdin if stdin else sys.stdin
        self.output = output if output else OUT

        self.bare_config = BareConfig(self.output, self.stdout,
            self.stdin, self.stderr)
        self.defaults = self.bare_config.get_defaults()
        #print self.defaults

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

        self.parser.add_option_group(group)

        #-----------------------------------------------------------------
        # Debug Options

        #self.output.cli_opts(self.parser)

        # Parse the command line first since we need to get the config
        # file option.
        if len(args) == 1:
            print 'Usage:%s' % _USAGE
            sys.exit(0)

        (self.options, remain_args) = self.parser.parse_args(args)
        # remain_args starts with something like "bin/layman" ...
        if len(remain_args) > 1:
            self.parser.error("Unhandled parameters: %s"
                % ', '.join(('"%s"' % e) for e in remain_args[1:]))

        # handle debugging
        #self.output.cli_handle(self.options)

        # add output to the options
        self.options.__dict__['output'] = self.output

        # add the std in/out/err to the options
        self.options.__dict__['stdout'] = self.stdout
        self.options.__dict__['stdin'] = self.stdin
        self.options.__dict__['stderr'] = self.stderr


        if self.options.__dict__['nocolor']:
            self.output.set_colorize(OFF)

        # Fetch only an alternate config setting from the options
        if not self.options.__dict__['config'] is None:
            self.defaults['config'] = self.options.__dict__['config']

            #self.output.debug('Got config file at ' + self.defaults['config'], 8)

        # Now parse the config file
        self.config = ConfigParser.ConfigParser(self.defaults)
        self.config.add_section('MAIN')

        # handle quietness
        if self['quiet']:
            self.output.set_info_level(1)
            self.output.set_warn_level(1)
            self.defaults['quietness'] = 0
        elif 'quietness' in self.keys():
            self.output.set_info_level(int(self['quietness']))
            self.output.set_warn_level(int(self['quietness']))

        #self.output.debug('Reading config file at ' + self.defaults['config'], 8)

        read_config(self.config, self.defaults)

    def __getitem__(self, key):

        if key == 'overlays':
            overlays = ''
            if (key in self.options.__dict__.keys()
                and not self.options.__dict__[key] is None):
                overlays = '\n'.join(self.options.__dict__[key])
            if self.config.has_option('MAIN', 'overlays'):
                overlays += '\n' + self.config.get('MAIN', 'overlays')
            if overlays:
                return  overlays

        self.output.debug('Retrieving option', 8)

        if (key in self.options.__dict__.keys()
            and not self.options.__dict__[key] is None):
            return self.options.__dict__[key]

        self.output.debug('Retrieving option', 8)

        if self.config.has_option('MAIN', key):
            if key == 'nocheck':
                if self.config.get('MAIN', key).lower() == 'yes':
                    return True
                else:
                    return False
            return self.config.get('MAIN', key)

        self.output.debug('Retrieving option', 8)

        if key in self.defaults.keys():
            return self.defaults[key]

        self.output.debug('Retrieving option', 8)

        return None


    def keys(self):
        '''Special handler for the configuration keys.'''

        self.output.debug('Retrieving keys', 8)

        keys = [i for i in self.options.__dict__.keys()
                if not self.options.__dict__[i] is None]

        self.output.debug('Retrieving keys', 8)

        keys += [name for name, _ in self.config.items('MAIN')
                 if not name in keys]

        self.output.debug('Retrieving keys', 8)

        keys += [i for i in self.defaults.keys()
                 if not i in keys]

        self.output.debug('Retrieving keys', 8)

        return keys


#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(sys.modules[__name__])
