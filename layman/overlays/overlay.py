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
#             (c) 2005 - 2006 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
''' Basic overlay class.'''

__version__ = "$Id: overlay.py 273 2006-12-30 15:54:50Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import sys, types, re, os, os.path, shutil, popen2

from   layman.utils             import node_to_dict, dict_to_node, path

from   layman.debug             import OUT

#===============================================================================
#
# Class Overlay
#
#-------------------------------------------------------------------------------

class Overlay:
    ''' Derive the real implementations from this.'''

    type = 'None'

    def __init__(self, xml, ignore = 0, quiet = False):
        '''
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> document = open(here + '/../tests/testfiles/global-overlays.xml').read()
        >>> import xml.dom.minidom
        >>> document = xml.dom.minidom.parseString(document)
        >>> overlays = document.getElementsByTagName('overlay')
        >>> a = Overlay(overlays[0])
        >>> a.name
        u'wrobel'
        >>> a.is_official()
        True
        >>> a.src
        u'https://overlays.gentoo.org/svn/dev/wrobel'
        >>> a.contact
        u'nobody@gentoo.org'
        >>> a.description
        u'Test'
        >>> a.priority
        10
        >>> b = Overlay(overlays[1])
        >>> b.is_official()
        False
        '''
        self.quiet = quiet

        self.data = node_to_dict(xml)

        if '&name' in self.data.keys():
            self.name = self.data['&name']
        else:
            raise Exception('Overlay is missing a "name" attribute!')

        if '&src' in self.data.keys():
            self.src = self.data['&src']
        else:
            raise Exception('Overlay "' + self.name + '" is missing a "src" '
                            'attribute!')

        if '&contact' in self.data.keys():
            self.contact = self.data['&contact']
        else:
            self.contact = ''
            if not ignore:
                raise Exception('Overlay "' + self.name + '" is missing a '
				'"contact" attribute!')
            elif ignore == 1:
                OUT.warn('Overlay "' + self.name + '" is missing a '
                         '"contact" attribute!', 4)

        if '<description>1' in self.data.keys():
            self.description = self.data['<description>1']['@'].strip()
        else:
            self.description = ''
            if not ignore:
                raise Exception('Overlay "' + self.name + '" is missing a '
				'"description" entry!')
            elif ignore == 1:
                OUT.warn('Overlay "' + self.name + '" is missing a '
			 '"description" entry!', 4)

        if '&status' in self.data.keys():
            self.status = self.data['&status']
        else:
            self.status = ''

        if '&priority' in self.data.keys():
            self.priority = int(self.data['&priority'])
        else:
            self.priority = 50

    def set_priority(self, priority):
        '''Set the priority of this overlay.'''

        self.data['&priority'] = str(priority)
        self.priority = int(priority)

    def to_minidom(self, document):
        '''Convert to xml.'''

        return dict_to_node(self.data, document, 'overlay')

    def add(self, base):
        '''Add the overlay.'''

        mdir = path([base, self.name])

        if os.path.exists(mdir):
            raise Exception('Directory ' + mdir + ' already exists. Will not ov'
                            'erwrite its contents!')

        os.makedirs(mdir)

    def sync(self, base):
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
            command = command.encode(sys.stdout.encoding or 
                                     sys.getfilesystemencoding())

        if not self.quiet:
            return os.system(command)
        else:
            cmd = popen2.Popen4(command)
            cmd.fromchild.readlines()
            result = cmd.wait()
            cmd.fromchild.readlines()
            cmd.fromchild.close()
            cmd.tochild.close()
            return result

    def __str__(self):
        '''
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> document = open(here + '/../tests/testfiles/global-overlays.xml').read()
        >>> import xml.dom.minidom
        >>> document = xml.dom.minidom.parseString(document)
        >>> overlays = document.getElementsByTagName('overlay')
        >>> a = Overlay(overlays[0])
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
        result += u'\nContact : ' + self.contact
        result += u'\nType    : ' + self.type
        result += u'; Priority: ' + str(self.priority) + u'\n'

        description = self.description
        description = re.compile(u' +').sub(u' ', description)
        description = re.compile(u'\n ').sub(u'\n', description)
        result += u'\nDescription:'
        result += u'\n  '.join((u'\n' + description).split(u'\n'))
        result += u'\n'

        if '<link>1' in self.data.keys():
            link = self.data['<link>1']['@'].strip()
            link = re.compile(u' +').sub(u' ', link)
            link = re.compile(u'\n ').sub(u'\n', link)
            result += u'\nLink:\n'
            result += u'\n  '.join((u'\n' + link).split(u'\n'))
            result += u'\n'

        return result

    def short_list(self):
        '''
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> document = open(here + '/../tests/testfiles/global-overlays.xml').read()
        >>> import xml.dom.minidom
        >>> document = xml.dom.minidom.parseString(document)
        >>> overlays = document.getElementsByTagName('overlay')
        >>> a = Overlay(overlays[0])
        >>> print a.short_list()
        wrobel                    [None      ] (source: https://overlays.gentoo.or...)
        '''

        def pad(string, length):
            '''Pad a string with spaces.'''
            if len(string) <= length:
                return string + ' ' * (length - len(string))
            else:
                return string[:length - 3] + '...'

        name   = pad(self.name, 25)
        mtype  = ' [' + pad(self.type, 10) + ']'
        source = ' (source: ' + pad(self.src, 29) + ')'

        return name + mtype + source

    def supported(self, binaries = []):
        '''Is the overlay type supported?'''

        if binaries:
            for mpath, mtype, package in binaries:
                if not os.path.exists(mpath):
                    raise Exception('Binary ' + mpath + ' seems to be missing!'
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

#================================================================================
#
# Testing
#
#--------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
