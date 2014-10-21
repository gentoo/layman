#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
# LAYMAN MOUNTING OVERLAY HANDLER
###############################################################################
# File:       mounter.py
#
#             Controls all mountable overlay types
#
# Copyright:
#             (c) 2014 Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#            
# Author(s):
#             Devan Franchini <twitch153@gentoo.org>
#
'''
Controls all mountable overlay types.
'''
#==============================================================================
#
# Dependencies
#
#------------------------------------------------------------------------------
from __future__ import unicode_literals

import argparse
import copy
import os
import sys

from  layman.constants  import MOUNT_TYPES
from  layman.utils      import path, run_command
from  layman.version    import __version__


if sys.hexversion >= 0x30200f0:
    STR = str
else:
    STR = basestring

MOUNT_ARGS = {'Squashfs': ['-o', 'loop', '-t', 'squashfs']}
_USAGE = 'layman-mounter [-h] [-l] [-L] [-m MOUNT [MOUNT ...]]\n'\
         '                      [-u UMOUNT [UMOUNT ...]] [-V]'

def is_mounted(mdir):
    '''
    Determines whether or not an overlay is mounted at it's
    installed overlay.

    @rtype bool
    '''
    return os.path.ismount(mdir)


class Mounter(object):
    '''
    Handles all mountable overlays.
    '''
    def __init__(self, database, overlays, config=None):
        self.config = config
        self.database = database
        self.output = self.config['output']
        self.overlays = overlays
        self.storage = self.config['storage']


    @property
    def installed(self):
        '''
        Returns a dictionary of all installed overlays
        and their overlay objects.

        @rtype dict {'ovl1', <layman.overlays.Overlay object>,...}
        '''
        installed_db = {}

        for overlay in self.overlays():
            ovl_db = self.database().select(overlay)
            installed_db[overlay] = ovl_db
        return installed_db


    @property
    def mountables(self):
        '''
        Returns a dictionary of all mountable overlays and their
        types.

        @rtype dict {'ovl1': 'Squashfs',...}
        '''
        mountable_ovls = {}

        for key in sorted(self.installed):
            for ovl_type in self.installed[key].source_types():
                if ovl_type in MOUNT_TYPES:
                    mountable_ovls[key] = ovl_type
        return mountable_ovls


    @property
    def mounted(self):
        '''
        Returns a dictionary of all mountable overlays and a
        boolean reflecting their mounted status.

        @rtype dict {'ovl1': True, 'ovl2': False,...}
        '''
        mounted_ovls = {}

        for ovl in self.mountables:
            mdir = path([self.storage, ovl])
            mounted_ovls[ovl] = is_mounted(mdir)
        return mounted_ovls


    def _check_selection(self, repos):
        '''
        Internal function to validate the repo parameter.

        @rtype tuple
        '''
        if 'ALL' in repos:
            repos = sorted(self.mountables)
        elif isinstance(repos, STR):
            repos = [repos]

        return repos


    def mount(self, repo, dest=None, install=False, ovl_type=None, pkg=None):
        '''
        Mounts an overlay to it's installation directory.

        @params repo: str of overlay name or "ALL".
        @params dest: str of optional destination dir.
        @params install: bool to reflect whether or not the overlay is being
        installed.
        @params ovl_type: str of optional overlay type.
        @params pkg: str of optional location of package to mount.
        @rtype int: reflects whether or not the overlay was mounted.
        '''
        result = 1

        selection = self._check_selection(repo)

        for i in selection:
            name = {'ovl': i}

            if i not in self.mountables and not install:
                self.output.error('Overlay "%(ovl)s" cannot be mounted!'\
                                    % name)
                continue
            if dest:
                mdir = dest
            else:
                mdir = path([self.storage, i])

            if not is_mounted(mdir):
                if install:
                    args = copy.deepcopy(MOUNT_ARGS[ovl_type])
                else:
                    args = copy.deepcopy(MOUNT_ARGS[self.mountables[i]])
                
                if not pkg:
                    source = self.installed[i].sources[0].src

                    if 'file://' in source:
                        pkg = source.replace('file://', '')
                    else:
                        pkg = path([self.storage, i, source.get_extension()])

                args.append(pkg)
                args.append(mdir)
                result = run_command(self.config, 'mount', args, cmd='mount')
            else:
                self.output.warn('Overlay "%(ovl)s" is already mounted!'\
                                    % name)
        return result


    def umount(self, repo, dest=None, sync=False):
        '''
        Unmounts an overlay from it's installation directory.

        @params repo: str of overlay name or "ALL".
        @params dest: str of optional path to unmount.
        @params sync: bool to reflect whether or not the overlay is being
        synced.
        @rtype int: reflects whether or not it was a successful unmount.
        '''
        result = 1

        selection = self._check_selection(repo)
            
        for i in selection:
            name = {'ovl': i}

            if i not in self.mountables and not sync:
                self.output.error('Overlay "%(ovl)s" cannot be mounted!'\
                                    % name)
                continue
            if dest:
                mdir = dest
            else:
                mdir = path([self.storage, i])

            if is_mounted(mdir):
                args = ['-l', mdir]
                result = run_command(self.config, 'umount', args, cmd='umount')
            else:
                self.output.warn('Overlay "%(ovl)s" is already unmounted!'\
                                    % name)

        return result


class Interactive(object):
    '''
    Interactive CLI session for the Mounter class
    '''
    def __init__(self, config=None, mounter=None):
        self.args = None
        self.parser = None
        self.output = config['output']
        self.storage = config['storage']
        self.mount = mounter
        self.mountables = self.mount.mountables


    def args_parser(self):
        '''
        Parses all command line arguments.

        @rtype argparse.NameSpace object.
        '''
        self.parser = argparse.ArgumentParser(prog='layman-mounter',
            description='Layman\'s utility script to handle mountable '\
                        'overlays.')
        self.parser.add_argument('-l',
                                 '--list-mountables',
                                 action='store_true',
                                 help='Lists all available overlays that'
                                 ' support mounting')
        self.parser.add_argument('-L',
                                 '--list-mounted',
                                 action='store_true',
                                 help='Lists all mounted overlays')
        self.parser.add_argument('-m',
                                 '--mount',
                                 nargs='+',
                                 help='Mounts the selected overlay. Specify '\
                                 '"ALL" to mount all possible overlays')
        self.parser.add_argument('-u',
                                 '--umount',
                                 nargs='+',
                                 help='Unmounts the selected overlay. Specify'\
                                 ' "ALL" to unmount all possible overlays')
        self.parser.add_argument('-V',
                                 '--version',
                                 action='version',
                                 version='%(prog)s ' + __version__)
        self.args = self.parser.parse_args()


    def __call__(self):
        self.args_parser()
        if len(sys.argv) == 1:
            self.output.notice('usage: %(USAGE)s' % {'USAGE':_USAGE})
            sys.exit(0)
        options = {}

        for key in vars(self.args):
            options[key] = vars(self.args)[key]

        for i in ('list_mountables', 'list_mounted'):
            if options[i]:
                getattr(self, i)()
                self.output.notice('')

        for i in ('umount', 'mount'):
            if options[i]:
                getattr(self.mount, '%(action)s' % {'action': i})(options[i])


    def list_mountables(self):
        '''
        Lists all overlays that can be mounted.
        '''
        self.output.info('Mountable overlays:')
        self.output.info('~~~~~~~~~~~~~~~~~~~')
        if self.mountables:
            for ovl in sorted(self.mountables):
                self.output.info(ovl)
        else:
            self.output.warn('N/A')


    def list_mounted(self):
        '''
        Lists all mounted overlays.
        '''
        mounted = self.mount.mounted

        self.output.info('Overlays:')
        self.output.info('~~~~~~~~~')
        for i in mounted:
            if mounted[i]:
                status = 'Mounted'
            else:
                status = 'Unmounted'
            stat_dict = {'ovl': i, 'status': status}
            self.output.info('Name: %(ovl)s, Status: %(status)s' % stat_dict)
