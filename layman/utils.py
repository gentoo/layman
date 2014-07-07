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

from __future__ import unicode_literals

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

from  layman.output         import Message

if sys.hexversion >= 0x30200f0:
    STR = str
else:
    STR = basestring

#===============================================================================
#
# Helper functions
#
#-------------------------------------------------------------------------------

def encoder(text, _encoding_):
    return codecs.encode(text, _encoding_, 'replace')


def decode_selection(selection):
    '''utility function to decode a list of strings
    accoring to the filesystem encoding
    '''
    # fix None passed in, return an empty list
    selection = selection or []
    enc = sys.getfilesystemencoding()
    if enc is not None:
        return [encoder(i, enc) for i in selection]
    return selection


def get_encoding(output):
    if hasattr(output, 'encoding') \
            and output.encoding != None:
        return output.encoding
    else:
        encoding = locale.getpreferredencoding()
        # Make sure that python knows the encoding. Bug 350156
        try:
            # We don't care about what is returned, we just want to
            # verify that we can find a codec.
            codecs.lookup(encoding)
        except LookupError:
            # Python does not know the encoding, so use utf-8.
            encoding = 'utf_8'
        return encoding


def get_ans(msg, color='green'):
    '''
    Handles yes/no input

    @params msg: message prompt for user
    @rtype boolean: reflects whether the user answered yes or no.
    '''
    ans = get_input(msg, color=color).lower()

    while ans not in ('y', 'yes', 'n', 'no'):
        ans = get_input('Please respond with [y/n]: ', color='yellow').lower()

    return ans in ('y', 'yes')


def get_input(msg, color='green', output=None):
    '''
    py2, py3 compatibility function
    to obtain user input.

    @params msg: message prompt for user
    @rtype str: input from user
    '''
    if not output:
        output = Message()

    try:
        value = raw_input(' %s %s' % (output.color_func(color, '*'), msg))
    except NameError:
        value = input(' %s %s' % (output.color_func(color, '*'), msg))

    return value


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

    if isinstance(path_elements, STR):
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

def verify_overlay_src(current_src, remote_srcs):
    '''
    Verifies that the src-url of the overlay in
    that database is in the set of reported src_urls
    by the remote database.

    @param current_src: current source URL.
    @param remote_srcs: set of available sources reported by remote database.
    @rtype tuple: returns tuple of set/str of source(s), and boolean reflecting
    whether current_src is valid or not.
    '''
    if current_src not in remote_srcs:
        # return remote_srcs and boolean
        # stating that it's not valid.
        return remote_srcs, False
    return current_src, True

def delete_empty_directory(mdir, output=None):
    # test for a usable output parameter,
    # and make it usable if not
    if output is None:
        output = Message()
    if os.path.exists(mdir) and not os.listdir(mdir):
        # Check for sufficient privileges
        if os.access(mdir, os.W_OK):
            output.info('Deleting _empty_ directory "%s"' % mdir, 2)
            try:
                os.rmdir(mdir)
            except OSError as error:
                output.warn(str(error))
        else:
            output.warn('Insufficient permissions to delete _empty_ folder "%s".' % mdir)
            import getpass
            if getpass.getuser() != 'root':
                output.warn('Hint: You are not root.')


def create_overlay_dict(**kwargs):
    """Creates a complete empty reository definition.
    Then fills it with values passed in
    """
    result = {
        'name': '',
        'owner_name': '',
        'owner_email': '',
        'homepage': '',
        'irc': '',
        'description': '',
        'feeds': [],
        'sources': [('','','')],
        'priority': 50,
        'quality': 'experimental',
        'status': '',
        'official': False,
        'supported': False,
        }
    for key in kwargs:
        result[key] = kwargs[key]
    return result


#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(sys.modules[__name__])
