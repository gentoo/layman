# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN OVERLAY SOURCE BASE CLASS
#################################################################################
# File:       source.py
#
#             Base class for the different overlay types.
#
# Copyright:
#             (c) 2010        Sebastian Pipping
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Sebastian Pipping <sebastian@pipping.org>

import os
import sys
import shutil
import subprocess
from layman.debug import OUT
from layman.utils import path


def require_supported(binaries):
    for command, mtype, package in binaries:
        found = False
        if os.path.isabs(command):
            kind = 'Binary'
            found = os.path.exists(command)
        else:
            kind = 'Command'
            for d in os.environ['PATH'].split(os.pathsep):
                f = os.path.join(d, command)
                if os.path.exists(f):
                    found = True
                    break

        if not found:
            raise Exception(kind + ' ' + command + ' seems to be missing!'
                            ' Overlay type "' + mtype + '" not support'
                            'ed. Did you emerge ' + package + '?')
    return True


class OverlaySource(object):

    def __init__(self, parent, xml, config, _location, ignore = 0, quiet = False):
        self.parent = parent
        self.src = _location
        self.config = config
        self.ignore = ignore
        self.quiet = quiet

    def __eq__(self, other):
        return self.src == other.src

    def __ne__(self, other):
        return not self.__eq__(other)

    def add(self, base, quiet = False):
        '''Add the overlay.'''

        mdir = path([base, self.parent.name])

        if os.path.exists(mdir):
            raise Exception('Directory ' + mdir + ' already exists. Will not ov'
                            'erwrite its contents!')

        os.makedirs(mdir)

    def sync(self, base, quiet = False):
        '''Sync the overlay.'''
        pass

    def delete(self, base):
        '''Delete the overlay.'''
        mdir = path([base, self.parent.name])

        if not os.path.exists(mdir):
            OUT.warn('Directory ' + mdir + ' did not exist, no files deleted.')
            return

        OUT.info('Deleting directory "%s"' % mdir, 2)
        shutil.rmtree(mdir)

    def supported(self):
        '''Is the overlay type supported?'''
        return True

    def is_supported(self):
        '''Is the overlay type supported?'''

        try:
            self.supported()
            return True
        except Exception, error:
            return False

    def command(self):
        return self.config['%s_command' % self.__class__.type_key]

    def cmd(self, command):
        '''Run a command.'''

        OUT.info('Running command "' + command + '"...', 2)

        if hasattr(sys.stdout,'encoding'):
            enc = sys.stdout.encoding or sys.getfilesystemencoding()
            if enc:
                command = command.encode(enc)

        if not self.quiet:
            return os.system(command)
        else:
            cmd = subprocess.Popen([command], shell = True,
                                   stdout = subprocess.PIPE,
                                   stderr = subprocess.PIPE,
                                   close_fds = True)
            result = cmd.wait()
            return result

    def to_xml_hook(self, repo_elem):
        pass
