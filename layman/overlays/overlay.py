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

import sys, types, re, os, os.path, shutil, subprocess
import xml.etree.ElementTree as ET # Python 2.5

from   layman.utils             import path, ensure_unicode

from   layman.debug             import OUT

#===============================================================================
#
# Class Overlay
#
#-------------------------------------------------------------------------------

class Overlay:
    ''' Derive the real implementations from this.'''

    type = 'None'

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
        >>> a.src
        u'https://overlays.gentoo.org/svn/dev/wrobel'
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
            self.name = ensure_unicode(_name.text)
        elif 'name' in xml.attrib:
            self.name = ensure_unicode(xml.attrib['name'])
        else:
            raise Exception('Overlay is missing a "name" entry!')

        _source = xml.find('source')
        if _source != None:
            self.src = ensure_unicode(_source.text.strip())
        elif 'src' in xml.attrib:
            self.src = ensure_unicode(xml.attrib['src'])
        else:
            raise Exception('Overlay "' + self.name + '" is missing a "source" entry!')

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

    def set_priority(self, priority):
        '''Set the priority of this overlay.'''

        self.priority = int(priority)

    def to_minidom(self):
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
        source = ET.Element('source', type=self.__class__.type_key)
        source.text = self.src
        repo.append(source)
        return repo

    def add(self, base, quiet = False):
        '''Add the overlay.'''

        mdir = path([base, self.name])

        if os.path.exists(mdir):
            raise Exception('Directory ' + mdir + ' already exists. Will not ov'
                            'erwrite its contents!')

        os.makedirs(mdir)

    def sync(self, base, quiet = False):
        '''Sync the overlay.'''
        pass

    def delete(self, base):
        '''Delete the overlay.'''
        mdir = path([base, self.name])

        if not os.path.exists(mdir):
            raise Exception('Directory ' + mdir + ' does not exist. Cannot remo'
                            've the overlay!')

        shutil.rmtree(mdir)

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
        Type    : None; Priority: 10
        <BLANKLINE>
        Description:
          Test
        <BLANKLINE>
        '''

        result = u''

        result += self.name + u'\n' + (len(self.name) * u'~')

        result += u'\nSource  : ' + self.src
        if self.owner_name != None:
            result += u'\nContact : %s <%s>' % (self.owner_name, self.owner_email)
        else:
            result += u'\nContact : ' + self.owner_email
        result += u'\nType    : ' + self.type
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

        return result

    def short_list(self, width = 0):
        '''
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> import xml.etree.ElementTree as ET # Python 2.5
        >>> document = ET.parse(here + '/../tests/testfiles/global-overlays.xml')
        >>> overlays = document.findall('repo') + document.findall('overlay')
        >>> a = Overlay(overlays[0], dict())
        >>> print a.short_list(80)
        wrobel                    [None      ] (https://o.g.o/svn/dev/wrobel         )
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
        mtype  = ' [' + pad(self.type, 10) + ']'
        if not width:
            width = terminal_width()
        srclen = width - 43
        source = self.src
        if len(source) > srclen:
            source = source.replace("overlays.gentoo.org", "o.g.o")
        source = ' (' + pad(source, srclen) + ')'

        return name + mtype + source

    def supported(self, binaries = []):
        '''Is the overlay type supported?'''

        if binaries:
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

    def is_supported(self):
        '''Is the overlay type supported?'''

        try:
            self.supported()
            return True
        except Exception, error:
            return False

    def is_official(self):
        '''Is the overlay official?'''

        return self.status == 'official'

    def command(self):
        return self.config['%s_command' % self.__class__.type_key]

#================================================================================
#
# Testing
#
#--------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
