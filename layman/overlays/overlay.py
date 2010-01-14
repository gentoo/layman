#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN OVERLAY BASE CLASS
#################################################################################
# File:       overlay.py
#
#             Base class for the different overlay types.
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
''' Basic overlay class.'''

__version__ = "$Id: overlay.py 273 2006-12-30 15:54:50Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys, re, os, os.path
import codecs
import locale
import xml.etree.ElementTree as ET # Python 2.5

from   layman.utils             import path, ensure_unicode

from   layman.debug             import OUT

from   layman.overlays.bzr       import BzrOverlay
from   layman.overlays.darcs     import DarcsOverlay
from   layman.overlays.git       import GitOverlay
from   layman.overlays.mercurial import MercurialOverlay
from   layman.overlays.cvs       import CvsOverlay
from   layman.overlays.svn       import SvnOverlay
from   layman.overlays.rsync     import RsyncOverlay
from   layman.overlays.tar       import TarOverlay

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
# Class Overlay
#
#-------------------------------------------------------------------------------

class Overlay(object):
    ''' Derive the real implementations from this.'''

    def __init__(self, xml, config, ignore = 0, quiet = False):
        '''
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> import xml.etree.ElementTree as ET # Python 2.5
        >>> document = ET.parse(here + '/../tests/testfiles/global-overlays.xml')
        >>> overlays = document.findall('overlay') + document.findall('repo')
        >>> a = Overlay(overlays[0], dict())
        >>> a.name
        u'wrobel'
        >>> a.is_official()
        True
        >>> list(a.source_uris())
        [u'https://overlays.gentoo.org/svn/dev/wrobel']
        >>> a.owner_email
        u'nobody@gentoo.org'
        >>> a.description
        u'Test'
        >>> a.priority
        10
        >>> b = Overlay(overlays[1], dict())
        >>> b.is_official()
        False
        '''
        self.config = config
        self.quiet = quiet

        _name = xml.find('name')
        if _name != None:
            self.name = ensure_unicode(_name.text.strip())
        elif 'name' in xml.attrib:
            self.name = ensure_unicode(xml.attrib['name'])
        else:
            raise Exception('Overlay is missing a "name" entry!')

        _sources = xml.findall('source')
        if _sources:
            _sources = [e for e in _sources if 'type' in e.attrib]
        elif ('src' in xml.attrib) and ('type' in xml.attrib):
                s = ET.Element('source', type=xml.attrib['type'])
                s.text = xml.attrib['src']
                _sources = [s]
                del s

        if not _sources:
            raise Exception('Overlay "' + self.name + '" is missing a "source" entry!')


        def create_overlay_source(source_elem):
            _type = source_elem.attrib['type']
            try:
                _class = OVERLAY_TYPES[_type]
            except KeyError:
                raise Exception('Unknown overlay type "%s"!' % _type)
            _location = ensure_unicode(source_elem.text.strip())
            return _class(self, xml, config, _location, ignore, quiet)

        self.sources = map(create_overlay_source, _sources)


        _owner = xml.find('owner')
        if _owner == None:
            _email = None
        else:
            _email = _owner.find('email')
        if _owner != None and _email != None:
            self.owner_email = ensure_unicode(_email.text.strip())
            _name = _owner.find('name')
            if _name != None:
                self.owner_name = ensure_unicode(_name.text.strip())
            else:
                self.owner_name = None
        elif 'contact' in xml.attrib:
            self.owner_email = ensure_unicode(xml.attrib['contact'])
            self.owner_name = None
        else:
            self.owner_email = ''
            self.owner_name = None
            if not ignore:
                raise Exception('Overlay "' + self.name + '" is missing a '
                                '"owner.email" entry!')
            elif ignore == 1:
                OUT.warn('Overlay "' + self.name + '" is missing a '
                         '"owner.email" entry!', 4)


        _desc = xml.find('description')
        if _desc != None:
            self.description = ensure_unicode(_desc.text.strip())
        else:
            self.description = ''
            if not ignore:
                raise Exception('Overlay "' + self.name + '" is missing a '
	                                '"description" entry!')
            elif ignore == 1:
                OUT.warn('Overlay "' + self.name + '" is missing a '
                         '"description" entry!', 4)

        if 'status' in xml.attrib:
            self.status = ensure_unicode(xml.attrib['status'])
        else:
            self.status = None

        if 'priority' in xml.attrib:
            self.priority = int(xml.attrib['priority'])
        else:
            self.priority = 50

        h = xml.find('homepage')
        l = xml.find('link')
        if h != None:
            self.homepage = ensure_unicode(h.text.strip())
        elif l != None:
            self.homepage = ensure_unicode(l.text.strip())
        else:
            self.homepage = None

    def __eq__(self, other):
        for i in ('description', 'homepage', 'name', 'owner_email',
                'owner_name', 'priority', 'status'):
            if getattr(self, i) != getattr(other, i):
                return False
        if set(self.source_uris()) != set(other.source_uris()):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_priority(self, priority):
        '''Set the priority of this overlay.'''

        self.priority = int(priority)

    def to_xml(self):
        '''Convert to xml.'''

        repo = ET.Element('repo')
        if self.status != None:
            repo.attrib['status'] = self.status
        repo.attrib['priority'] = str(self.priority)
        name = ET.Element('name')
        name.text = self.name
        repo.append(name)
        desc = ET.Element('description')
        desc.text = self.description
        repo.append(desc)
        if self.homepage != None:
            homepage = ET.Element('homepage')
            homepage.text = self.homepage
            repo.append(homepage)
        owner = ET.Element('owner')
        repo.append(owner)
        owner_email = ET.Element('email')
        owner_email.text = self.owner_email
        owner.append(owner_email)
        if self.owner_name != None:
            owner_name = ET.Element('name')
            owner_name.text = self.owner_name
            owner.append(owner_name)
        for i in self.sources:
            source = ET.Element('source', type=i.__class__.type_key)
            source.text = i.src
            repo.append(source)
            del source
        for i in self.sources:
            # NOTE: Two loops on purpose so the
            # hooks are called with all sources in
            i.to_xml_hook(repo)
        return repo

    def add(self, base, quiet = False):
        res = 1
        for s in self.sources:
            try:
                res = s.add(base, quiet)
                if res == 0:
                    # Worked, throw other sources away
                    self.sources = [s]
                    break
            except Exception, error:
                OUT.warn(str(error), 4)
        return res

    def sync(self, base, quiet = False):
        assert len(self.sources) == 1
        return self.sources[0].sync(base, quiet)

    def delete(self, base):
        assert len(self.sources) == 1
        return self.sources[0].delete(base)

    def _get_encoding(self):
        if hasattr(sys.stdout, 'encoding') \
                and sys.stdout.encoding != None:
            return sys.stdout.encoding
        else:
            return locale.getpreferredencoding()

    def _encode(self, unicode_text):
        return codecs.encode(unicode_text, self._get_encoding(), 'replace')

    def __str__(self):
        '''
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> import xml.etree.ElementTree as ET # Python 2.5
        >>> document = ET.parse(here + '/../tests/testfiles/global-overlays.xml')
        >>> overlays = document.findall('overlay') + document.findall('repo')
        >>> a = Overlay(overlays[0], dict())
        >>> print str(a)
        wrobel
        ~~~~~~
        Source  : https://overlays.gentoo.org/svn/dev/wrobel
        Contact : nobody@gentoo.org
        Type    : Subversion; Priority: 10
        <BLANKLINE>
        Description:
          Test
        <BLANKLINE>
        '''

        result = u''

        result += self.name + u'\n' + (len(self.name) * u'~')

        if len(self.sources) == 1:
            result += u'\nSource  : ' + self.sources[0].src
        else:
            result += u'\nSources:'
            for i, v in enumerate(self.sources):
                result += '\n  %d. %s' % (i + 1, v.src)
            result += '\n'

        if self.owner_name != None:
            result += u'\nContact : %s <%s>' % (self.owner_name, self.owner_email)
        else:
            result += u'\nContact : ' + self.owner_email
        if len(self.sources) == 1:
            result += u'\nType    : ' + self.sources[0].type
        else:
            result += u'\nType    : ' + '/'.join(sorted(set(e.type for e in self.sources)))
        result += u'; Priority: ' + str(self.priority) + u'\n'

        description = self.description
        description = re.compile(u' +').sub(u' ', description)
        description = re.compile(u'\n ').sub(u'\n', description)
        result += u'\nDescription:'
        result += u'\n  '.join((u'\n' + description).split(u'\n'))
        result += u'\n'

        if self.homepage != None:
            link = self.homepage
            link = re.compile(u' +').sub(u' ', link)
            link = re.compile(u'\n ').sub(u'\n', link)
            result += u'\nLink:\n'
            result += u'\n  '.join((u'\n' + link).split(u'\n'))
            result += u'\n'

        return self._encode(result)

    def short_list(self, width = 0):
        '''
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> import xml.etree.ElementTree as ET # Python 2.5
        >>> document = ET.parse(here + '/../tests/testfiles/global-overlays.xml')
        >>> overlays = document.findall('repo') + document.findall('overlay')
        >>> a = Overlay(overlays[0], dict())
        >>> print a.short_list(80)
        wrobel                    [Subversion] (https://o.g.o/svn/dev/wrobel         )
        '''

        def pad(string, length):
            '''Pad a string with spaces.'''
            if len(string) <= length:
                return string + ' ' * (length - len(string))
            else:
                return string[:length - 3] + '...'

        def terminal_width():
            '''Determine width of terminal window.'''
            try:
                width = int(os.environ['COLUMNS'])
                if width > 0:
                    return width
            except:
                pass
            try:
                import struct, fcntl, termios
                query = struct.pack('HHHH', 0, 0, 0, 0)
                response = fcntl.ioctl(1, termios.TIOCGWINSZ, query)
                width = struct.unpack('HHHH', response)[1]
                if width > 0:
                    return width
            except:
                pass
            return 80

        name   = pad(self.name, 25)

        if len(set(e.type for e in self.sources)) == 1:
            _type = self.sources[0].type
        else:
            _type = '%s/..' % self.sources[0].type

        mtype  = ' [' + pad(_type, 10) + ']'
        if not width:
            width = terminal_width()
        srclen = width - 43
        source = ', '.join(self.source_uris())
        if len(source) > srclen:
            source = source.replace("overlays.gentoo.org", "o.g.o")
        source = ' (' + pad(source, srclen) + ')'

        return self._encode(name + mtype + source)

    def is_official(self):
        '''Is the overlay official?'''

        return self.status == 'official'

    def is_supported(self):
        return any(e.is_supported() for e in self.sources)

    def source_uris(self):
        for i in self.sources:
            yield i.src

#================================================================================
#
# Testing
#
#--------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
