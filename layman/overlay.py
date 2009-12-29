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
#             (c) 2009        Christian Groschupp
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Sebastian Pipping <sebastian@pipping.org>
#             Christian Groschupp <christian@groschupp.org>
#
'''Main handler for overlays.'''

__version__ = "$Id: overlay.py 273 2006-12-30 15:54:50Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys, codecs, os, os.path
import xml.etree.ElementTree as ET # Python 2.5

from   layman.overlays.bzr       import BzrOverlay
from   layman.overlays.darcs     import DarcsOverlay
from   layman.overlays.git       import GitOverlay
from   layman.overlays.mercurial import MercurialOverlay
from   layman.overlays.cvs       import CvsOverlay
from   layman.overlays.svn       import SvnOverlay
from   layman.overlays.rsync     import RsyncOverlay
from   layman.overlays.tar       import TarOverlay

from   layman.debug              import OUT
from   layman.utils              import indent

#===============================================================================
#
# Constants
#
#-------------------------------------------------------------------------------

OVERLAY_TYPES = dict((e.type_key, e) for e in (
    GitOverlay,
    CvsOverlay,
    SvnOverlay,
    RsyncOverlay,
    TarOverlay,
    BzrOverlay,
    MercurialOverlay,
    DarcsOverlay
))

#===============================================================================
#
# Class Overlays
#
#-------------------------------------------------------------------------------

class Overlays:
    ''' Handle a list of overlays.'''

    def __init__(self, paths, config, ignore = 0, quiet = False):

        self.config = config
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
            document = open(path, 'r').read()

        except Exception, error:
            raise IOError('Failed to read the overlay list at ("'
                          + path + '")!\nError was:\n' + str(error))

        self.read(document)

    def read(self, text):
        '''
        Read an xml list of overlays.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'svn_command': '/usr/bin/svn', 'rsync_command':'/usr/bin/rsync'}
        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ], config)
        >>> a.overlays.keys()
        [u'wrobel', u'wrobel-stable']

        >>> a.overlays['wrobel-stable'].src
        u'rsync://gunnarwrobel.de/wrobel-stable'
        '''
        document = ET.fromstring(text)
        overlays = document.findall('overlay') + \
                document.findall('repo')

        for overlay in overlays:
            OUT.debug('Parsing overlay entry', 8)
            
            _source = overlay.find('source')
            if _source != None:
                element_to_scan = _source
            else:
                element_to_scan = overlay

            for attr_name in element_to_scan.attrib.keys():
                if attr_name == 'type':
                    overlay_type = element_to_scan.attrib['type']
                    if overlay_type in OVERLAY_TYPES.keys():
                        try:
                            ovl = OVERLAY_TYPES[overlay_type](overlay,
                                                                self.config,
                                                                self.ignore,
                                                                self.quiet)
                            self.overlays[ovl.name] = ovl
                        except Exception, error:
                            OUT.warn(str(error), 3)
                    else:
                        raise Exception('Unknown overlay type "' +
                                        overlay_type + '"!')
                    break

    def write(self, path):
        '''
        Write the list of overlays to a file.

        >>> write = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'svn_command': '/usr/bin/svn', 'rsync_command':'/usr/bin/rsync'}
        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ], config)
        >>> b = Overlays([write,], dict())
        >>> b.overlays['wrobel-stable'] = a.overlays['wrobel-stable']
        >>> b.write(write)
        >>> c = Overlays([write,], dict())
        >>> c.overlays.keys()
        [u'wrobel-stable']

        >>> os.unlink(write)
        '''

        xml = ET.Element('repositories', version="1.0")
        xml[:] = [e.to_xml() for e in self.overlays.values()]
        indent(xml)
        tree = ET.ElementTree(xml)
        try:
            f = open(path, 'w')
            f.write("""\
<?xml version="1.0" encoding="UTF-8"?>
""")
            tree.write(f, encoding='utf-8')
            f.close()
        except Exception, error:
            raise Exception('Failed to write to local overlays file: '
                            + path + '\nError was:\n' + str(error))

    def select(self, overlay):
        '''
        Select an overlay from the list.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'svn_command': '/usr/bin/svn', 'rsync_command':'/usr/bin/rsync'}
        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ], config)
        >>> a.select('wrobel-stable').src
        u'rsync://gunnarwrobel.de/wrobel-stable'
        '''
        if overlay in self.overlays.keys():
            return self.overlays[overlay]

    def list(self, verbose = False, width = 0):
        '''
        List all overlays.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'svn_command': '/usr/bin/svn', 'rsync_command':'/usr/bin/rsync'}
        >>> a = Overlays([here + '/tests/testfiles/global-overlays.xml', ], config)
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
