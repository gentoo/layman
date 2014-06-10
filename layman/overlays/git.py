#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN GIT OVERLAY HANDLER
#################################################################################
# File:       git.py
#
#             Handles git overlays
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel, Stefan Schweizer
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Stefan Schweizer <genstef@gentoo.org>
''' Git overlay support.'''

from __future__ import unicode_literals

__version__ = "$Id: git.py 146 2006-05-27 09:52:36Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import xml.etree.ElementTree as ET

from   layman.utils             import path
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class GitOverlay
#
#-------------------------------------------------------------------------------

class GitOverlay(OverlaySource):
    ''' Handles git overlays.'''

    type = 'Git'
    type_key = 'git'

    def __init__(self, parent, config, _location, ignore = 0):
        super(GitOverlay, self).__init__(parent, config,
            _location, ignore)
        self.branch = self.parent.branch


    def _fix_git_source(self, source):
        '''
        Adds trailing slash to http sources

        @param source: source URL, string.
        '''
        # http:// should get trailing slash, other protocols shouldn't
        if source.split(':')[:1] == 'http':
            if not source.endswith('/'):
                return source + '/'
        return source

    def add(self, base):
        '''Add overlay.'''

        if not self.supported():
            return 1

        cfg_opts = self.config["git_addopts"]
        target = path([base, self.parent.name])

        # git clone [-q] SOURCE TARGET
        args = ['clone']
        if self.config['quiet']:
            args.append('-q')
        if len(cfg_opts):
            args.append(cfg_opts)
        args.append(self._fix_git_source(self.src))
        args.append(target)

        if self.branch:
            args.append('-b')
            args.append(self.branch)
        success = False
        # adding cwd=base due to a new git bug in selinux due to
        # not having user_home_dir_t and portage_fetch_t permissions
        # but changing dir works around it.
        success = self.run_command(self.command(), args, cmd=self.type, cwd=base)
        self.output.debug("cloned git repo...success=%s" % str(success), 8)
        success = self.set_user(target)
        return self.postsync(success, cwd=target)

    def set_user(self, target):
        '''Set dummy user.name and user.email to prevent possible errors'''
        user = '"%s"' % self.config['git_user']
        email = '"%s"' % self.config['git_email']
        args = ['config', 'user.name', user]
        self.output.debug("set git user info...args=%s" % ' '.join(args), 8)
        failure = self.run_command(self.command(), args, cmd=self.type, cwd=target)
        if failure:
            self.output.debug("set git user info...failure setting name")
            return failure
        args = ['config', 'user.email', email]
        self.output.debug("set git user info...args=%s" % ' '.join(args), 8)
        return self.run_command(self.command(), args, cmd=self.type, cwd=target)

    def update(self, base, src):
        '''
        Update overlay src-url
        
        @params base: base location where all overlays are installed.
        @params src:  source URL.
        '''
        self.output.debug("git.update(); starting...%s" % self.parent.name, 6)
        target = path([base, self.parent.name])

        # git remote set-url <name> <newurl> <oldurl>
        args = ['remote', 'set-url', 'origin', self._fix_git_source(src), self._fix_git_source(self.src)]

        return self.run_command(self.command(), args, cmd=self.type, cwd=target)

    def sync(self, base):
        '''Sync overlay.'''

        self.output.debug("git.sync(); starting...%s" % self.parent.name, 6)
        if not self.supported():
            return 1

        cfg_opts = self.config["git_syncopts"]
        target = path([base, self.parent.name])

        args = ['pull']
        if self.config['quiet']:
            args.append('-q')
        if len(cfg_opts):
            args.append(cfg_opts)

        return self.postsync(
            self.run_command(self.command(), args, cwd=target, cmd=self.type),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
            [(self.command(),  'git', 'dev-vcs/git'),],
            self.output.warn)
