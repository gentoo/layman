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

__version__ = "$Id: tar.py 310 2007-04-09 16:30:40Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os, os.path, sys, urllib2, shutil, tempfile
import xml.etree.ElementTree as ET # Python 2.5

from   layman.utils             import path
#from   layman.debug             import OUT
from   layman.overlays.source   import OverlaySource, require_supported

#===============================================================================
#
# Class TarOverlay
#
#-------------------------------------------------------------------------------

class TarOverlay(OverlaySource):
    ''' Handles tar overlays.

    >>> from   layman.output import Message
    >>> import xml.etree.ElementTree as ET # Python 2.5
    >>> repo = ET.Element('repo')
    >>> repo_name = ET.Element('name')
    >>> repo_name.text = 'dummy'
    >>> desc = ET.Element('description')
    >>> desc.text = 'Dummy description'
    >>> owner = ET.Element('owner')
    >>> owner_email = ET.Element('email')
    >>> owner_email.text = 'dummy@example.org'
    >>> owner[:] = [owner_email]
    >>> source = ET.Element('source', type='tar')
    >>> here = os.path.dirname(os.path.realpath(__file__))
    >>> source.text = 'file://' + here + '/../tests/testfiles/layman-test.tar.bz2'
    >>> subpath = ET.Element('subpath')
    >>> subpath.text = 'layman-test'
    >>> repo[:] = [repo_name, desc, owner, source, subpath]
    >>> from layman.config import BareConfig
    >>> config = BareConfig()
    >>> import tempfile
    >>> testdir = tempfile.mkdtemp(prefix="laymantmp_")
    >>> from layman.overlays.overlay import Overlay
    >>> a = Overlay(config, repo)
    >>> config['output'].set_colorize(False)
    >>> a.add(testdir)
    0
    >>> os.listdir(testdir + '/dummy/')
    ['layman-test']
    >>> sorted(os.listdir(testdir + '/dummy/layman-test/'))
    ['app-admin', 'app-portage']
    >>> shutil.rmtree(testdir)
    '''

    type = 'Tar'
    type_key = 'tar'

    def __init__(self, parent, config, _location, ignore = 0):

        super(TarOverlay, self).__init__(parent,
            config, _location, ignore)

        self.output = config['output']
        self.subpath = None

    def __eq__(self, other):
        res = super(TarOverlay, self).__eq__(other) \
            and self.subpath == other.subpath
        return res

    def __ne__(self, other):
        return not self.__eq__(other)

    # overrider
    def to_xml_hook(self, repo_elem):
        if self.subpath:
            _subpath = ET.Element('subpath')
            _subpath.text = self.subpath
            repo_elem.append(_subpath)
            del _subpath

    def _extract(self, base, tar_url, dest_dir):
        ext = '.tar.noidea'
        for i in [('tar.%s' % e) for e in ('bz2', 'gz', 'lzma', 'xz', 'Z')] \
                + ['tgz', 'tbz', 'taz', 'tlz', 'txz']:
            candidate_ext = '.%s' % i
            if self.src.endswith(candidate_ext):
                ext = candidate_ext
                break

        try:
            tar = urllib2.urlopen(tar_url).read()
        except Exception as error:
            raise Exception('Failed to fetch the tar package from: '
                            + self.src + '\nError was:' + str(error))

        pkg = path([base, self.parent.name + ext])

        try:
            out_file = open(pkg, 'w+b')
            out_file.write(tar)
            out_file.close()
        except Exception as error:
            raise Exception('Failed to store tar package in '
                            + pkg + '\nError was:' + str(error))

        # tar -v -x -f SOURCE -C TARGET
        args = ['-v', '-x', '-f', pkg, '-C', dest_dir]
        result = self.run_command(self.command(), args, cmd=self.type)

        os.unlink(pkg)
        return result

    def _add_unchecked(self, base):
        def try_to_wipe(folder):
            if not os.path.exists(folder):
                return

            try:
                self.output.info('Deleting directory "%s"' % folder, 2)
                shutil.rmtree(folder)
            except Exception as error:
                raise Exception('Failed to remove unnecessary tar structure "'
                                + folder + '"\nError was:' + str(error))

        final_path = path([base, self.parent.name])
        temp_path = tempfile.mkdtemp(dir=base)
        try:
            result = self._extract(base=base, tar_url=self.src,
                dest_dir=temp_path)
        except Exception as error:
            try_to_wipe(temp_path)
            raise error

        if result == 0:
            if self.subpath:
                source = temp_path + '/' + self.subpath
            else:
                source = temp_path

            if os.path.exists(source):
                if os.path.exists(final_path):
                    self.delete(base)

                try:
                    os.rename(source, final_path)
                except Exception as error:
                    raise Exception('Failed to rename tar subdirectory ' +
                                    source + ' to ' + final_path +
                                    '\nError was:' + str(error))
                os.chmod(final_path, 0755)
            else:
                raise Exception('Given subpath "' + source + '" does not exist '
                                ' in the tar package!')

        try_to_wipe(temp_path)
        return result

    def add(self, base):
        '''Add overlay.'''

        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        if os.path.exists(target):
            raise Exception('Directory ' + target + ' already exists.' +\
                ' Will not overwrite its contents!')

        return self.postsync(
            self._add_unchecked(base),
            cwd=target)

    def sync(self, base):
        '''Sync overlay.'''

        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        return self.postsync(
            self._add_unchecked(base),
            cwd=target)

    def supported(self):
        '''Overlay type supported?'''

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
