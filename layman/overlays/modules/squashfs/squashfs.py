#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# LAYMAN SQUASHFS OVERLAY HANDLER
################################################################################
# File:       squashfs.py
#
#             Handles squashfs overlays
#
# Copyright:
#             (c) 2014 Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Devan Franchini <twitch153@gentoo.org>
#
''' Squashfs overlay support.'''

from __future__ import unicode_literals

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os
import shutil
import sys

from   layman.constants        import FILE_EXTENSIONS
from   layman.overlays.archive import ArchiveOverlay
from   layman.overlays.source  import require_supported
from   layman.utils            import path

#===============================================================================
#
# Class SquashfsOverlay
#
#-------------------------------------------------------------------------------

class SquashfsOverlay(ArchiveOverlay):
    ''' Handles squashfs overlays.'''

    type = 'Squashfs'
    type_key = 'squashfs'

    def __init__(self, parent, config, _location, ignore=0):
        super(SquashfsOverlay, self).__init__(parent,
            config, _location, ignore)
        self.mounter = config.get_option('mounts')


    def get_extension(self):
        '''
        Determines squashfs file extension.

        @rtype str
        '''
        ext = ''
        for i in FILE_EXTENSIONS[self.type]:
            candidate_ext = i
            if self.src.endswith(candidate_ext):
                ext = candidate_ext
                break

        return ext


    def delete(self, base):
        '''
        Deletes the selected overlay.

        @params base: Base dir where the overlay is installed.
        @rtype bool
        '''
        mdir = path([base, self.parent.name])

        source = self.src
        if 'file://' in source:
            pkg = source.replace('file://', '')
        else:
            pkg_name = self.parent.name + self.get_extension()
            pkg = path([self.config['storage'], pkg_name])

        if os.path.ismount(mdir):
            result = self.mounter.umount([self.parent.name])
        else:
            result = 1

        shutil.rmtree(mdir)
        if self.clean_archive:
            if os.path.exists(pkg):
                os.unlink(pkg)

        return result


    def post_fetch(self, pkg, dest_dir):
        '''
        Runs initial squashfs archive mounting.

        @params pkg: string location where squashfs archive is located.
        @params dest_dir: string of mounting destination.
        @rtype bool
        '''
        result = self.mounter.mount([self.parent.name],
                                    dest_dir,
                                    install=True,
                                    ovl_type=self.type,
                                    pkg=pkg)
        # Warn the user that pkg is mounted r/o and will have to be mounted
        # again using the layman-mounter tool on the next boot.
        if result == 0:
            warning_1 = 'Overlay "%(ovl)s" has been mounted read-only at'\
                        ' %(loc)s.' % {'loc': dest_dir,
                                       'ovl': self.parent.name}
            warning_2 = 'Upon reboot the overlay will not be accessible until'\
                        ' you mount it either manually or via the'\
                        ' layman-mounter tool.'

            self.output.warn(warning_1)
            self.output.warn(warning_2)

        return result


    def is_supported(self):
        '''
        Determines if the overlay type is supported.

        @rtype bool
        '''
        return True

if __name__ == '__main__':
    import doctest

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
