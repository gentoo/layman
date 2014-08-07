#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
 LAYMAN CONFIGURATION

 File:       config.py

             Handles Basic layman configuration

 Copyright:
             (c) 2005 - 2009 Gunnar Wrobel
             (c) 2009        Sebastian Pipping
             (c) 2010 - 2011 Brian Dolbec
             Distributed under the terms of the GNU General Public License v2

 Author(s):
             Gunnar Wrobel <wrobel@gentoo.org>
             Sebastian Pipping <sebastian@pipping.org>
             Brian Dolbec <brian.dolbec@gmail.com>
"""

'''Defines the configuration options.'''

__version__ = "0.2"


import sys
import os

try:
    # Import for Python3
    import configparser as ConfigParser
except:
    # Import for Python2
    import ConfigParser

from layman.output import Message
from layman.utils import path

# establish the eprefix, initially set so eprefixify can
# set it on install
EPREFIX = "@GENTOO_PORTAGE_EPREFIX@"
# check and set it if it wasn't
if "GENTOO_PORTAGE_EPREFIX" in EPREFIX:
    EPREFIX = ''

def read_layman_config(config=None, defaults=None, output=None):
    """reads the config file defined in defaults['config']
    and updates the config

    @param config: ConfigParser.ConfigParser(self.defaults) instance
    @param defaults: dict
    @modifies config['MAIN']['overlays']
    """
    read_files = config.read(defaults['config'])
    if read_files == [] and output is not None:
        output.warn("Warning: not able to parse config file: %s"
            % defaults['config'])
    if config.get('MAIN', 'overlay_defs'):
        try:
            filelist = os.listdir(config.get('MAIN', 'overlay_defs'))
        except OSError:
            return
        filelist = [f for f in filelist if f.endswith('.xml')]
        overlays = set(config.get('MAIN', 'overlays').split('\n'))
        for _file in filelist:
            _path = os.path.join(config.get('MAIN', 'overlay_defs'), _file)
            if os.path.isfile(_path):
                overlays.update(["file://" + _path])
        config.set('MAIN', 'overlays', '\n'.join(overlays))


class BareConfig(object):
    '''Handles the configuration only.'''

    def __init__(self, output=None, stdout=None, stdin=None, stderr=None,
        config=None, read_configfile=False, quiet=False, quietness=4,
        verbose=False, nocolor=False, width=0, root=None
        ):
        '''
        Creates a bare config with defaults and a few output options.
        '''

        if root is None:
            self.root = ''
        else:
            self.root = root

        self._defaults = {
            'configdir': path([self.root, EPREFIX,'/etc/layman']),
            'config'    : '%(configdir)s/layman.cfg',
            'storage'   : path([self.root, EPREFIX,'/var/lib/layman']),
            'cache'     : '%(storage)s/cache',
            'local_list': '%(storage)s/overlays.xml',
            'installed': '%(storage)s/installed.xml',
            'auto_sync': 'No',
            'conf_type': 'make.conf',
            'require_repoconfig': 'Yes',
            'clean_tar': 'yes',
            'make_conf' : '%(storage)s/make.conf',
            'repos_conf': '/etc/portage/repos.conf/layman.conf',
            'conf_module': ['make_conf', 'repos_conf'],
            'nocheck'   : 'yes',
            'http_proxy'     : '',
            'https_proxy'     : '',
            'umask'     : '0022',
            'news_reporter': 'portage',
            'custom_news_pkg': '',
            'gpg_detached_lists':
                'https://api.gentoo.org/overlays/repositories.xml https://api.gentoo.org/overlays/repositories.xml.asc',
            'gpg_signed_lists': '',
            'overlays'  :
                'https://api.gentoo.org/overlays/repositories.xml',
            'overlay_defs': '%(configdir)s/overlays',
            'bzr_command': path([self.root, EPREFIX,'/usr/bin/bzr']),
            'cvs_command': path([self.root, EPREFIX,'/usr/bin/cvs']),
            'darcs_command': path([self.root, EPREFIX,'/usr/bin/darcs']),
            'git_command': path([self.root, EPREFIX,'/usr/bin/git']),
            'g-common_command': path([self.root, EPREFIX,'/usr/bin/g-common']),
            'g-sorcery_command': path([self.root, EPREFIX,'/usr/bin/g-sorcery']),
            'mercurial_command': path([self.root, EPREFIX,'/usr/bin/hg']),
            'rsync_command': path([self.root, EPREFIX,'/usr/bin/rsync']),
            'svn_command': path([self.root, EPREFIX,'/usr/bin/svn']),
            'tar_command': path([self.root, EPREFIX,'/bin/tar']),
            't/f_options': ['clean_tar', 'nocheck', 'require_repoconfig'],
            'bzr_addopts' : '',
            'bzr_syncopts' : '',
            'cvs_addopts' : '',
            'cvs_syncopts' : '',
            'darcs_addopts' : '',
            'darcs_syncopts' : '',
            'git_addopts' : '',
            'git_syncopts' : '',
            'mercurial_addopts' : '',
            'mercurial_syncopts' : '',
            'rsync_syncopts' : '',
            'svn_addopts' : '',
            'svn_syncopts' : '',
            'g-common_generateopts' : '',
            'g-common_syncopts' : '',
            'g-sorcery_generateopts' : '',
            'g-sorcery_syncopts' : '',
            'bzr_postsync' : '',
            'cvs_postsync' : '',
            'darcs_postsync' : '',
            'git_postsync' : '',
            'mercurial_postsync' : '',
            'rsync_postsync' : '',
            'svn_postsync' : '',
            'tar_postsync' : '',
            'g-common_postsync' : '',
            'g-sorcery_postsync' : '',
            'git_user': 'layman',
            'git_email': 'layman@localhost',
            'support_url_updates': ['Bzr', 'cvs', 'Git', 'Mercurial', 'Subversion'],
            }
        self._options = {
            'config': config if config else self._defaults['config'],
            'stdout': stdout if stdout else sys.stdout,
            'stdin': stdin if stdin else sys.stdin,
            'stderr': stderr if stderr else sys.stderr,
            'output': output if output else Message(),
            'quietness': quietness,
            'nocolor': nocolor,
            'width': width,
            'verbose': verbose,
            'quiet': quiet,
            'custom_news_func': None,
            }
        self._set_quietness(quietness)
        self.config = None
        if read_configfile:
            defaults = self.get_defaults()
            if "%(configdir)s" in defaults['config']:
                # fix the config path
                defaults['config'] = defaults['config'] \
                    % {'configdir': defaults['configdir']}
            self.read_config(defaults)


    def read_config(self, defaults):
        self.config = ConfigParser.ConfigParser(defaults)
        self.config.add_section('MAIN')
        read_layman_config(self.config, defaults, self._options['output'])


    def keys(self):
        '''Special handler for the configuration keys.
        '''
        self._options['output'].debug(
            'Retrieving %s options' % self.__class__.__name__, 9)
        keys = [i for i in self._options]
        self._options['output'].debug(
            'Retrieving %s defaults' % self.__class__.__name__, 9)
        keys += [i for i in self._defaults
                 if not i in keys]
        self._options['output'].debug(
            'Retrieving %s done...' % self.__class__.__name__, 9)
        return keys


    def get_defaults(self):
        """returns our defaults dictionary"""
        _defaults = self._defaults.copy()
        _defaults['config'] = self._options['config']
        return _defaults


    def get_option(self, key):
        """returns the current option's value"""
        return self._get_(key)


    def set_option(self, option, value):
        """Sets an option to the value"""
        self._options[option] = value
        # handle quietness
        if option == 'quiet':
            if self._options['quiet']:
                self._set_quietness(1)
                self._options['quietness'] = 1
            else:
                self._set_quietness(4)
        if option == 'quietness':
            self._set_quietness(value)

    def _set_quietness(self, value):
            self._options['output'].set_info_level(value)
            self._options['output'].set_warn_level(value)
            self._options['output'].set_note_level(value)

    def __getitem__(self, key):
        return self._get_(key)

    def _get_(self, key):
        self._options['output'].debug(
            'Retrieving %s option: %s' % (self.__class__.__name__, key), 9)
        if key == 'overlays':
            overlays = ''
            if (key in self._options
                and not self._options[key] is None):
                overlays = '\n'.join(self._options[key])
            if self.config and self.config.has_option('MAIN', 'overlays'):
                overlays += '\n' + self.config.get('MAIN', 'overlays')
            if overlays:
                return  overlays
        if (key in self._options
            and not self._options[key] is None):
            return self._options[key]
        if self.config and self.config.has_option('MAIN', key):
            if key in self._defaults['t/f_options']:
                return self.t_f_check(self.config.get('MAIN', key))
            return self.config.get('MAIN', key)
        self._options['output'].debug('Retrieving BareConfig default', 9)
        if key in self._defaults['t/f_options']:
            return self.t_f_check(self._defaults[key])
        if key in self._defaults:
            if '%(storage)s' in self._defaults[key]:
                return self._defaults[key] %{'storage': self._defaults['storage']}
            return self._defaults[key]
        return None

    @staticmethod
    def t_f_check(option):
        """evaluates the option and returns
        True or False
        """
        return option.lower() in ['yes', 'true', 'y', 't']

    @property
    def proxies(self):
        """
        Reads the config options to determine the available proxies.

        @param config: config options dict.
        @rtype dict
        """
        proxies = {}

        for proxy in ['http_proxy', 'https_proxy']:
            if self.config and self.config.get('MAIN', proxy):
                proxies[proxy.split('_')[0]] = self.config.get('MAIN', proxy)
            elif self.get_option(proxy):
                proxies[proxy.split('_')[0]] = self.get_option(proxy)
            elif os.getenv(proxy):
                proxies[proxy.split('_')[0]] = os.getenv(proxy)
        if self.config and proxies == {}:
            self.output.debug("Warning: unable to determine proxies.", 6)

        return proxies


class OptionConfig(BareConfig):
    """This subclasses BareConfig adding functions to make overriding
    or resetting defaults and/or setting options much easier
    by using dictionaries.
    """

    def __init__(self, options=None, defaults=None, root=None):
        """
        @param options: dictionary of {'option': value, ...}
        @rtype OptionConfig class instance.
        """
        BareConfig.__init__(self, root=root)

        self.update_defaults(defaults)

        self.update(options)

        return

    def update(self, options):
        """update the options with new values passed in via options

        @param options
        """
        if options is not None:
            keys = sorted(options)
            if 'quiet' in keys:
                self.set_option('quiet', options['quiet'])
                options.pop('quiet')
            elif 'quietness' in keys:
                self._set_quietness(options['quietness'])
                options.pop('quietness')
            self._options.update(options)
        return

    def update_defaults(self, new_defaults):
        """update the options with new values passed in via options

        @param options
        """
        if new_defaults is not None:
            self._defaults.update(new_defaults)
        return

#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(sys.modules[__name__])
