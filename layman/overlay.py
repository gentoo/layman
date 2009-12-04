#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN OVERLAY HANDLER
#################################################################################
# File:       overlay.py
#
#             Access to an xml list of overlays
#
# Copyright:
#             (c) 2005 - 2009 Gunnar Wrobel
#             (c) 2009        Sebastian Pipping
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Sebastian Pipping <sebastian@pipping.org>
#
'''Main handler for overlays.'''

__version__ = "$Id: overlay.py 273 2006-12-30 15:54:50Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys, codecs, os, os.path, xml.dom.minidom

from   layman.overlays.bzr       import BzrOverlay
from   layman.overlays.darcs     import DarcsOverlay
from   layman.overlays.git       import GitOverlay
from   layman.overlays.mercurial import MercurialOverlay
from   layman.overlays.cvs       import CvsOverlay
from   layman.overlays.svn       import SvnOverlay
from   layman.overlays.rsync     import RsyncOverlay
from   layman.overlays.tar       import TarOverlay

from   layman.debug              import OUT

#===============================================================================
#
# Constants
#
#-------------------------------------------------------------------------------

OVERLAY_TYPES = {'git'       : GitOverlay,
                 'cvs'       : CvsOverlay,
                 'svn'       : SvnOverlay,
                 'rsync'     : RsyncOverlay,
                 'tar'       : TarOverlay,
                 'bzr'       : BzrOverlay,
                 'mercurial' : MercurialOverlay,
                 'darcs'     : DarcsOverlay}

#===============================================================================
#
# Class Overlays
#
#-------------------------------------------------------------------------------

class Overlays:
    ''' Handle a list of overlays.'''

    def __init__(self, paths, ignore = 0, quiet = False):

        self.quiet = quiet
        self.paths = paths
        self.ignore = ignore

        self.overlays = {}

        OUT.debug('Initializing overlay list handler', 8)

        for path in self.paths:
            if os.path.exists(path):
                self.read_file(path)

    def read_file(self, path):
        '''Read the overlay definition file.'''

        try:

            document = open(path).read()

        except Exception, error:
            raise IOError('Failed to read the overlay list at ("'
                          + path + '")!\nError was:\n' + str(error))


        self.read(document)

    def read(self, document):
        '''
        Read an xml list of overlays.

        >>> here = os.path.dirname(os.path.realpath(__file__))

        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ])
        >>> a.overlays.keys()
        [u'wrobel', u'wrobel-stable']

        >>> a.overlays['wrobel-stable'].data['&src']
        u'rsync://gunnarwrobel.de/wrobel-stable'
        '''
        try:

            document = xml.dom.minidom.parseString(document)

        except Exception, error:
            raise Exception('Failed to parse the overlay list!\nError was:\n'
                            + str(error))

        overlays = document.getElementsByTagName('overlay') + \
                document.getElementsByTagName('repo')

        for overlay in overlays:

            OUT.debug('Parsing overlay entry', 8)
            try:
                element_to_scan = overlay.getElementsByTagName('source')[0]
            except IndexError:
                element_to_scan = overlay

            for index in range(0, element_to_scan.attributes.length):
                attr = element_to_scan.attributes.item(index)
                if attr.name == 'type':
                    if attr.nodeValue in OVERLAY_TYPES.keys():
                        try:
                            ovl = OVERLAY_TYPES[attr.nodeValue](overlay,
                                                                self.ignore,
                                                                self.quiet)
                            self.overlays[ovl.name] = ovl
                        except Exception, error:
                            OUT.warn(str(error), 3)
                    else:
                        raise Exception('Unknown overlay type "' +
                                        attr.nodeValue + '"!')

    def write(self, path):
        '''
        Write the list of overlays to a file.

        >>> write = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))

        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ])
        >>> b = Overlays([write,])
        >>> b.overlays['wrobel-stable'] = a.overlays['wrobel-stable']
        >>> b.write(write)
        >>> c = Overlays([write,])
        >>> c.overlays.keys()
        [u'wrobel-stable']

        >>> os.unlink(write)
        '''

        imp = xml.dom.minidom.getDOMImplementation()

        doc = imp.createDocument('layman', 'repositories', None)

        root =  doc.childNodes[0]

        for name, overlay in self.overlays.items():

            root.appendChild(overlay.to_minidom(doc))

        try:

            out_file = codecs.open(path, 'w', 'utf-8')

            doc.writexml(out_file, '', '  ', '\n')

        except Exception, error:
            raise Exception('Failed to write to local overlays file: '
                            + path + '\nError was:\n' + str(error))

    def select(self, overlay):
        '''
        Select an overlay from the list.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ])
        >>> a.select('wrobel-stable').data['&src']
        u'rsync://gunnarwrobel.de/wrobel-stable'
        '''
        if overlay in self.overlays.keys():
            return self.overlays[overlay]

    def list(self, verbose = False, width = 0):
        '''
        List all overlays.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ])
        >>> for i in a.list(True):
        ...     print i[0]
        wrobel
        ~~~~~~
        Source  : https://overlays.gentoo.org/svn/dev/wrobel
        Contact : nobody@gentoo.org
        Type    : Subversion; Priority: 10
        <BLANKLINE>
        Description:
          Test
        <BLANKLINE>
        wrobel-stable
        ~~~~~~~~~~~~~
        Source  : rsync://gunnarwrobel.de/wrobel-stable
        Contact : nobody@gentoo.org
        Type    : Rsync; Priority: 50
        <BLANKLINE>
        Description:
          A collection of ebuilds from Gunnar Wrobel [wrobel@gentoo.org].
        <BLANKLINE>

        >>> for i in a.list(False, 80):
        ...     print i[0]
        wrobel                    [Subversion] (https://o.g.o/svn/dev/wrobel         )
        wrobel-stable             [Rsync     ] (rsync://gunnarwrobel.de/wrobel-stable)
        '''
        result = []

        for name, overlay in self.overlays.items():

            if verbose:
                result.append((str(overlay), overlay.is_supported(),
                               overlay.is_official()))
            else:
                result.append((overlay.short_list(width), overlay.is_supported(),
                               overlay.is_official()))

        result = sorted(result)

        return result

#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest, sys

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
