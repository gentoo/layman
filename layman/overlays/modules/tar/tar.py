#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN TAR OVERLAY HANDLER
#################################################################################
# File:       tar.py
#
#             Handles tar overlays
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
''' Tar overlay support.'''

from __future__ import unicode_literals

__version__ = "$Id: tar.py 310 2007-04-09 16:30:40Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys

from   layman.constants        import FILE_EXTENSIONS
from   layman.overlays.archive import ArchiveOverlay
from   layman.overlays.source  import require_supported
from   layman.utils            import run_command

#===============================================================================
#
# Class TarOverlay
#
#-------------------------------------------------------------------------------

class TarOverlay(ArchiveOverlay):
    '''Handles tar overlays.'''

    type = 'Tar'
    type_key = 'tar'

    def __init__(self, parent, config, _location, ignore=0):

        super(TarOverlay, self).__init__(parent,
            config, _location, ignore)

        self.output = config['output']


    def get_extension(self):
        '''
        Determines tar file extension.

        @rtype str
        '''
        ext = '.tar.noidea'
        for i in [('tar.%s' % e) for e in FILE_EXTENSIONS[self.type]]:
            candidate_ext = '.%s' % i
            if self.src.endswith(candidate_ext):
                ext = candidate_ext
                break

        return ext


    def post_fetch(self, pkg, dest_dir):
        '''
        Extracts tar archive.

        @params pkg: string location where tar archive is located.
        @params dest_dir: string of destination of extracted archive.
        @rtype bool
        '''
        # tar -v -x -f SOURCE -C TARGET
        args = ['-v', '-x', '-f', pkg, '-C', dest_dir]
        result = run_command(self.config, self.command(), args, cmd=self.type)

        return result


    def is_supported(self):
        '''
        Determines if overlay type is supported.

        @rtype bool
        '''

        return require_supported(
            [(self.command(),  'tar', 'app-arch/tar'), ],
            self.output.warn)

if __name__ == '__main__':
    import doctest

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
