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

import codecs
import copy
import locale
import os
import re
import subprocess
import sys
import types

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
    '''
    pathname = ''

    if isinstance(path_elements, STR):
        path_elements = [path_elements]

    # Concatenate elements and separate with /
    for i in path_elements:
        pathname += i + '/'

    # Replace multiple consecutive slashes
    pathname = re.compile('/+').sub('/', pathname)

    # Remove the final / if there is one
    if pathname and pathname[-1] == '/':
        pathname = pathname[:-1]

    return pathname


def reload_config(config):
    '''
    Rereads the layman config.

    @params config: layman.config object.
    '''
    defaults = config.get_defaults()
    defaults['config'] = defaults['config'] \
                             % {'configdir': defaults['configdir']}
    config.update_defaults({'config': defaults['config']})
    config.read_config(defaults)


def resolve_command(command, output):
    if os.path.isabs(command):
        if not os.path.exists(command):
            output('Program "%s" not found' % command)
            return ('File', None)
        return ('File', command)
    else:
        kind = 'Command'
        env_path = os.environ['PATH']
        for d in env_path.split(os.pathsep):
            f = os.path.join(d, command)
            if os.path.exists(f):
                return ('Command', f)
        output('Cound not resolve command ' +\
            '"%s" based on PATH "%s"' % (command, env_path))
        return ('Command', None)


def run_command(config, command, args, **kwargs):
    output = config['output']
    output.debug("Utils.run_command(): " + command, 6)

    file_to_run = resolve_command(command, output.error)[1]
    args = [file_to_run] + args
    assert('pwd' not in kwargs)  # Bug detector

    output.debug("OverlaySource.run_command(): cleared 'assert'", 7)
    cwd = kwargs.get('cwd', None)
    env = None
    env_updates = None
    if 'env' in kwargs:
        # Build actual env from surrounding plus updates
        env_updates = kwargs['env']
        env = copy.copy(os.environ)
        env.update(env_updates)

    command_repr = ' '.join(args)
    if env_updates is not None:
        command_repr = '%s %s' % (' '.join('%s=%s' % (k, v) for (k, v)
            in sorted(env_updates.items())), command_repr)
    if cwd is not None:
        command_repr = '( cd %s  && %s )' % (cwd, command_repr)

    cmd = kwargs.get('cmd', '')
    output.info('Running %s... # %s' % (cmd, command_repr), 2)

    if config['quiet']:

        input_source = subprocess.PIPE
        output_target = open('/dev/null', 'w')
    else:
        # Re-use parent file descriptors
        input_source = None
        output_target = None

    proc = subprocess.Popen(args,
        stdin=input_source,
        stdout=output_target,
        stderr=config['stderr'],
        cwd=cwd,
        env=env)

    if config['quiet']:
        # Make child non-interactive
        proc.stdin.close()

    try:
        result = proc.wait()
    except KeyboardInterrupt:
        output.info('Interrupted manually', 2)
        result = 1
    except Exception as err:
        output.error(
            'Unknown exception running command: %s' % command_repr)
        output.error('Original error was: %s' % str(err))
        result = 1

    if config['quiet']:
        output_target.close()

    if result:
        output.info('Failure result returned from %s' % cmd , 2)

    return result


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
