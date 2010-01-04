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

import os, os.path, sys, urllib2, shutil
import xml.etree.ElementTree as ET # Python 2.5

from   layman.utils             import path
from   layman.overlays.overlay  import Overlay

#===============================================================================
#
# Class TarOverlay
#
#-------------------------------------------------------------------------------

class TarOverlay(Overlay):
    ''' Handles tar overlays.

    A dummy tar handler that overwrites the __init__ method
    so that we don't need to provide xml input:

    >>> from   layman.debug             import OUT
    >>> class DummyTar(TarOverlay):
    ...   def __init__(self):
    ...     self.name = 'dummy'
    ...     here = os.path.dirname(os.path.realpath(__file__))
    ...     self.src  = 'file://' + here + '/../tests/testfiles/layman-test.tar.bz2'
    ...     self.subpath = 'layman-test'
    ...     self.format = 'bz2'
    ...     self.quiet = False
    ...     self.config = {'tar_command':'/bin/tar'}
    >>> testdir = os.tmpnam()
    >>> os.mkdir(testdir)
    >>> a = DummyTar()
    >>> OUT.color_off()
    >>> a.add(testdir) #doctest: +ELLIPSIS
    * Running command "/bin/tar -v -x -j -f...
    >>> sorted(os.listdir(testdir + '/dummy'))
    ['app-admin', 'app-portage']
    >>> shutil.rmtree(testdir)
    '''

    type = 'Tar'
    type_key = 'tar'

    def __init__(self, xml, config, ignore = 0, quiet = False):

        Overlay.__init__(self, xml, config, ignore)

        if 'format' in xml.attrib:
            self.format = xml.attrib['format']
        else:
            self.format = ''

        if 'subpath' in xml.attrib:
            self.subpath = xml.attrib['subpath']
        else:
            self.subpath = ''

        if 'category' in xml.attrib:
            if self.subpath:
                raise Exception('Cannot use "category" and "subpath" at the same'
                                ' time!')

            self.category = xml.attrib['category']
        else:
            self.category = ''

    def __eq__(self, other):
        res = super(TarOverlay, self).__eq__(other) \
            and self.format == other.format \
            and self.subpath == other.subpath \
            and self.category == other.category
        return res

    def __ne__(self, other):
        return not self.__eq__(other)

    # overrider
    def to_xml(self):
        repo = super(TarOverlay, self).to_xml()
        if self.format:
            repo.find('source').attrib['format'] = self.format
        if self.subpath:
            _subpath = ET.Element('subpath')
            _subpath.text = self.subpath
            repo.append(_subpath)
        if self.category:
            _category = ET.Element('category')
            _category.text = self.category
            repo.append(_category)
        return repo

    def add(self, base, quiet = False):
        '''Add overlay.'''

        self.supported()

        mdir = path([base, self.name])

        if os.path.exists(mdir):
            raise Exception('Directory ' + mdir + ' already exists. Will not ov'
                            'erwrite its contents!')

        if self.format == 'bz2' or (not self.format and self.src[-3:] == 'bz2'):
            ext = 'bz2'
            opt = '-j'
        elif self.format == 'gz' or (not self.format and self.src[-2:] == 'gz'):
            ext = 'gz'
            opt = '-z'
        else:
            raise Exception('Unsupported file format!')

        try:

            tar = urllib2.urlopen(self.src).read()

        except Exception, error:
            raise Exception('Failed to fetch the tar package from: '
                            + self.src + '\nError was:' + str(error))

        pkg = path([base, self.name + '.tar.' + ext])

        try:

            out_file = open(pkg, 'w')
            out_file.write(tar)
            out_file.close()

        except Exception, error:
            raise Exception('Failed to store tar package in '
                            + pkg + '\nError was:' + str(error))

        if self.subpath:
            target = path([base, 'tmp'])
        else:
            if self.category:
                target = mdir + '/' + self.category
            else:
                target = mdir

        os.makedirs(target)

        result = self.cmd(self.command() + u' -v -x ' + opt + u' -f "' + pkg
                          + u'" -C "' + target + u'"')

        if self.subpath:
            source = target + '/' + self.subpath
            if os.path.exists(source):
                try:
                    os.rename(source, mdir)
                except Exception, error:
                    raise Exception('Failed to rename tar subdirectory ' +
                                    source + ' to ' + mdir + '\nError was:'
                                    + str(error))
            else:
                raise Exception('Given subpath "' + source + '" does not exist '
                                ' in the tar package!')
            try:
                shutil.rmtree(target)
            except Exception, error:
                raise Exception('Failed to remove unnecessary tar structure "'
                                + target + '"\nError was:' + str(error))

        os.unlink(pkg)

        return result

    def sync(self, base, quiet = False):
        '''Sync overlay.'''

        self.supported()

        self.delete(base)

        self.add(base)

    def supported(self):
        '''Overlay type supported?'''

        return Overlay.supported(self, [(self.command(),  'tar', 'app-arch/tar'), ])

if __name__ == '__main__':
    import doctest

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
