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

import sys, os, os.path
import xml
import xml.etree.ElementTree as ET # Python 2.5

from   layman.debug              import OUT
from   layman.utils              import indent
from   layman.overlays.overlay   import Overlay

#===============================================================================
#
# Class UnknownOverlayException
#
#-------------------------------------------------------------------------------

class UnknownOverlayException(Exception):
    def __init__(self, repo_name):
        message = 'Overlay "%s" does not exist.' % repo_name
        super(UnknownOverlayException, self).__init__(message)

#===============================================================================
#
# Class BrokenOverlayCatalog
#
#-------------------------------------------------------------------------------

class BrokenOverlayCatalog(ValueError):
    def __init__(self, origin, expat_error, hint=None):
        if hint == None:
            hint = ''
        else:
            hint = '\nHint: %s' % hint

        super(BrokenOverlayCatalog, self).__init__(
            'XML parsing failed for "%(origin)s" (line %(line)d, column %(column)d)%(hint)s' % \
            {'line':expat_error.lineno, 'column':expat_error.offset + 1, 'origin':origin, 'hint':hint})


#===============================================================================
#
# Class DbBase
#
#-------------------------------------------------------------------------------

class DbBase:
    ''' Handle a list of overlays.'''

    def __init__(self, paths, config, ignore = 0, quiet = False, ignore_init_read_errors=False):

        self.config = config
        self.quiet = quiet
        self.paths = paths
        self.ignore = ignore

        self.overlays = {}

        OUT.debug('Initializing overlay list handler', 8)

        for path in self.paths:
            if not os.path.exists(path):
                continue

            try:
                self.read_file(path)
            except Exception, error:
                if not ignore_init_read_errors: raise error

    def __eq__(self, other):
        for key in set(self.overlays.keys() + other.overlays.keys()):
            if self.overlays[key] != other.overlays[key]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def read_file(self, path):
        '''Read the overlay definition file.'''

        try:
            document = open(path, 'r').read()

        except Exception, error:
            raise IOError('Failed to read the overlay list at ("'
                          + path + '")!\nError was:\n' + str(error))

        self.read(document, origin=path)

    def _broken_catalog_hint(self):
        this_function_name = sys._getframe().f_code.co_name
        raise NotImplementedError('Method "%s.%s" not implemented' % \
                (self.__class__.__name__, this_function_name))

    def read(self, text, origin):
        '''
        Read an xml list of overlays (adding to and potentially overwriting existing entries)

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'svn_command': '/usr/bin/svn', 'rsync_command':'/usr/bin/rsync'}
        >>> a = DbBase([here + '/tests/testfiles/global-overlays.xml', ], config)
        >>> a.overlays.keys()
        [u'wrobel', u'wrobel-stable']

        >>> list(a.overlays['wrobel-stable'].source_uris())
        [u'rsync://gunnarwrobel.de/wrobel-stable']
        '''
        try:
            document = ET.fromstring(text)
        except xml.parsers.expat.ExpatError, error:
            raise BrokenOverlayCatalog(origin, error, self._broken_catalog_hint())

        overlays = document.findall('overlay') + \
                document.findall('repo')

        for overlay in overlays:
            OUT.debug('Parsing overlay entry', 8)
            try:
                ovl = Overlay(overlay, self.config, self.ignore, self.quiet)
            except Exception, error:
                OUT.warn(str(error), 3)
            else:
                self.overlays[ovl.name] = ovl


    def write(self, path):
        '''
        Write the list of overlays to a file.

        >>> write = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'svn_command': '/usr/bin/svn', 'rsync_command':'/usr/bin/rsync'}
        >>> a = DbBase([here + '/tests/testfiles/global-overlays.xml', ], config)
        >>> b = DbBase([write,], dict())
        >>> b.overlays['wrobel-stable'] = a.overlays['wrobel-stable']
        >>> b.write(write)
        >>> c = DbBase([write,], dict())
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
        >>> a = DbBase([here + '/tests/testfiles/global-overlays.xml', ], config)
        >>> list(a.select('wrobel-stable').source_uris())
        [u'rsync://gunnarwrobel.de/wrobel-stable']
        '''
        if not overlay in self.overlays.keys():
            raise UnknownOverlayException(overlay)
        return self.overlays[overlay]

    def list(self, verbose = False, width = 0):
        '''
        List all overlays.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'svn_command': '/usr/bin/svn', 'rsync_command':'/usr/bin/rsync'}
        >>> a = DbBase([here + '/tests/testfiles/global-overlays.xml', ], config)
        >>> for i in a.list(True):
        ...     print i[0]
        wrobel
        ~~~~~~
        Source  : https://overlays.gentoo.org/svn/dev/wrobel
        Contact : nobody@gentoo.org
        Type    : Subversion; Priority: 10
        Quality : experimental
        <BLANKLINE>
        Description:
          Test
        <BLANKLINE>
        wrobel-stable
        ~~~~~~~~~~~~~
        Source  : rsync://gunnarwrobel.de/wrobel-stable
        Contact : nobody@gentoo.org
        Type    : Rsync; Priority: 50
        Quality : experimental
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

        for _, overlay in self.overlays.items():

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
    import doctest

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
