#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# POLYMERAZE XML UTILITIES
#################################################################################
# File:       xml.py
#
#             Utilities to deal with xml nodes.
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel
#             (c) 2009        Sebastian Pipping
#             (c) 2009        Christian Groschupp
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Sebastian Pipping <sebastian@pipping.org>
#             Christian Groschupp <christian@groschupp.org>
#

'''Utility functions to deal with xml nodes. '''

__version__ = '$Id: utils.py 236 2006-09-05 20:39:37Z wrobel $'

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import types, re, os
import sys
import locale
import codecs

from layman.debug import OUT


#===============================================================================
#
# Helper functions
#
#-------------------------------------------------------------------------------

def decode_selection(selection):
    '''utility function to decode a list of strings
    accoring to the filesystem encoding
    '''
    enc = sys.getfilesystemencoding()
    if enc:
        return [i.decode(enc) for i in selection]
    return selection


def encoder(unicode_text, _encoding_):
    return codecs.encode(unicode_text, _encoding_, 'replace')


def get_encoding(output):
    if hasattr(output, 'encoding') \
            and output.encoding != None:
        return output.encoding
    else:
        return locale.getpreferredencoding()


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


def ensure_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj

# From <http://effbot.org/zone/element-lib.htm>
# BEGIN
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
# END

def path(path_elements):
    '''
    Concatenate a path from several elements.

    >>> path([])
    ''
    >>> path(['a'])
    'a'
    >>> path(['a','b'])
    'a/b'
    >>> path(['a/','b'])
    'a/b'
    >>> path(['/a/','b'])
    '/a/b'
    >>> path(['/a/','b/'])
    '/a/b'
    >>> path(['/a/','b/'])
    '/a/b'
    >>> path(['/a/','/b/'])
    '/a/b'
    >>> path(['/a/','/b','c/'])
    '/a/b/c'
    '''
    pathname = ''

    if type(path_elements) in types.StringTypes:
        path_elements = [path_elements]

    # Concatenate elements and seperate with /
    for i in path_elements:
        pathname += i + '/'

    # Replace multiple consecutive slashes
    pathname = re.compile('/+').sub('/', pathname)

    # Remove the final / if there is one
    if pathname and pathname[-1] == '/':
        pathname = pathname[:-1]

    return pathname

def delete_empty_directory(mdir, output=OUT):
    if os.path.exists(mdir) and not os.listdir(mdir):
        # Check for sufficient privileges
        if os.access(mdir, os.W_OK):
            output.info('Deleting _empty_ directory "%s"' % mdir, 2)
            try:
                os.rmdir(mdir)
            except OSError, error:
                output.warn(str(error))
        else:
            output.warn('Insufficient permissions to delete _empty_ folder "%s".' % mdir)
            import getpass
            if getpass.getuser() != 'root':
                output.warn('Hint: You are not root.')

#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
