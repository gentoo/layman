#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN CVS OVERLAY HANDLER
#################################################################################
# File:       cvs.py
#
#             Handles cvs overlays
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
''' Cvs overlay support.'''

from __future__ import unicode_literals

__version__ = "$Id$"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import re

from   layman.utils             import path, run_command
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class CvsOverlay
#
#-------------------------------------------------------------------------------

class CvsOverlay(OverlaySource):
    ''' Handles cvs overlays.'''

    type = 'cvs'
    type_key = 'cvs'

    def __init__(self, parent, config, _location, ignore = 0):

        super(CvsOverlay, self).__init__(parent, config, _location, ignore)
        self.branch = self.parent.branch


    def add(self, base):
        '''Add overlay.'''

        if not self.supported():
            return 1

        cfg_opts = self.config["cvs_addopts"]
        target = path([base, self.parent.name])

        # cvs [-q] co -d SOURCE SCOPE
        args = []
        if self.config['quiet']:
            args.append('-q')
        args.append('co')
        args.append('-d')
        if len(cfg_opts):
            args.extend(cfg_opts.split())
        args.append(self.parent.name)
        args.append(self.branch)

        return self.postsync(
            run_command(self.config, self.command(), args, cwd=base,
                env=dict(CVSROOT=self.src), cmd=self.type),
            cwd=target)

    def update(self, base, src):
        '''
        Updates overlay src-url.

        @params base: base location where all overlays are installed.
        @params src: source URL.
        '''

        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        # First echo the new repository to CVS/Root
        args = [src, '>', '/CVS/Root']
        result = run_command(self.config, 'echo', args, cmd='echo',
                             cwd=target)

        if result == 0:
            location = src.split(':')[3]
            old_location = self.src.split(':/')[3]

            # Check if the repository location needs to be updated too.
            if not location == old_location:
                location = re.sub('/', '\/', location)
                old_location = re.sub('/', '\/', old_location)

                expression = 's/' + old_location + '/' + location + '/'

                # sed -i 's/<old_location>/<new_location>/ <target>/CVS/Repository
                args = ['-i', expression, '/CVS/Repository']

                return run_command(self.config, 'sed', args, cmd='sed',
                                   cwd=target)

        return result


    def sync(self, base):
        '''Sync overlay.'''

        if not self.supported():
            return 1

        cfg_opts = self.config["cvs_syncopts"]
        target = path([base, self.parent.name])

        # cvs [-q] update -d
        args = []
        if self.config['quiet']:
            args.append('-q')
        args.append('update')
        args.append('-d')
        if len(cfg_opts):
            args.extend(cfg_opts.split())
        return self.postsync(
            run_command(self.config, self.command(), args, cwd=target,
                        cmd=self.type),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

        return require_supported(
            [(self.command(),  'cvs', 'dev-vcs/cvs'),],
            self.output.warn)
