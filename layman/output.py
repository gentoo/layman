#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Copyright 2005 - 2008 Gunnar Wrobel
              2011 - Brian Dolbec
 Distributed under the terms of the GNU General Public License v2
"""

from __future__ import print_function

__version__ = "0.1"


import sys, types

from layman.constants import codes, INFO_LEVEL, WARN_LEVEL, DEBUG_LEVEL, OFF


class MessageBase(object):
    """Base Message class helper functions and variables
    """

    def __init__(self,
                 out = sys.stdout,
                 err = sys.stderr,
                 info_level = INFO_LEVEL,
                 warn_level = WARN_LEVEL,
                 col = True,
                 error_callback=None
                 ):
        # Where should the error output go? This can also be a file
        self.error_out = err

        # Where should the normal output go? This can also be a file
        self.std_out = out

        # The higher the level the more information you will get
        self.warn_lev = warn_level

        # The higher the level the more information you will get
        self.info_lev = info_level

        # Should the output be colored?
        self.color_func = None
        self.set_colorize(col)

        self.debug_lev = OFF

        # callback function that gets passed any error messages
        # that have shown up.
        self.error_callback = error_callback


    def _color (self, col, text):
        return codes[col] + text + codes['reset']


    def _no_color (self, col, text):
        return text


    def set_colorize(self, state):
        if state:
            self.color_func = self._color
        else:
            self.color_func = self._no_color


    def set_info_level(self, info_level = INFO_LEVEL):
        self.info_lev = info_level


    def set_warn_level(self, warn_level = WARN_LEVEL):
        self.warn_lev = warn_level


    def set_debug_level(self, debugging_level = DEBUG_LEVEL):
        self.debug_lev = debugging_level

    def do_error_callback(self, error):
        """runs the error_callback function with the error
        that occurred
        """
        if self.error_callback:
            self.error_callback(error)


class Message(MessageBase):
    """Primary Message output methods
    """
    #FIXME: Think about some simple doctests before you modify this class the
    #       next time.

    def __init__(self,
                 out = sys.stdout,
                 err = sys.stderr,
                 info_level = INFO_LEVEL,
                 warn_level = WARN_LEVEL,
                 col = True,
                 error_callback = None
                ):

        MessageBase.__init__(self)


    ## Output Functions

    def debug(self, info, level = OFF):
        """empty debug function, does nothing,
        declared here for compatibility with DebugMessage
        """
        pass


    def notice (self, note):
        print(note, file=self.std_out)


    def info (self, info, level = INFO_LEVEL):

        if type(info) not in types.StringTypes:
            info = str(info)

        if level > self.info_lev:
            return

        for i in info.split('\n'):
            print(self.color_func('green', '* ') + i, file=self.std_out)


    def status (self, message, status, info = 'ignored'):

        if type(message) not in types.StringTypes:
            message = str(message)

        lines = message.split('\n')

        if not lines:
            return

        for i in lines[0:-1]:
            print(self.color_func('green', '* ') + i, file=self.std_out)

        i = lines[-1]

        if len(i) > 58:
            i = i[0:57]

        if status == 1:
            result = '[' + self.color_func('green', 'ok') + ']'
        elif status == 0:
            result = '[' + self.color_func('red', 'failed') + ']'
        else:
            result = '[' + self.color_func('yellow', info) + ']'

        print(self.color_func('green', '* ') + i + ' ' + \
            '.' * (58 - len(i)) + ' ' + result, file=self.std_out)


    def warn (self, warn, level = WARN_LEVEL):

        if type(warn) not in types.StringTypes:
            warn = str(warn)

        if level > self.warn_lev:
            return

        for i in warn.split('\n'):
            print(self.color_func('yellow', '* ') + i, file=self.std_out)


    def error (self, error):

        if type(error) not in types.StringTypes:
            error = str(error)

        for i in error.split('\n'):
            # NOTE: Forced flushing ensures that stdout and stderr
            # stay in nice order.  This is a workaround for calls like
            # "layman -L |& less".
            sys.stdout.flush()
            print(self.color_func('red', '* ') + i, file=self.error_out)
            self.error_out.flush()
        self.do_error_callback(error)


    def die (self, error):

        if type(error) not in types.StringTypes:
            error = str(error)

        for i in error.split('\n'):
            self.error(self.color_func('red', 'Fatal error: ') + i)
        self.error(self.color_func('red', 'Fatal error(s) - aborting'))
        sys.exit(1)
