#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Layman is a complete library for the operation and maintainance
on all gentoo repositories and overlays
"""



class Layman(object):
    """High level interface capable of performing all
    overlay repository actions."""

    def __init__(self, stdout=None, stdin=None, stderr=None,
        config=None, read_configfile=True, quiet=False, quietness=4,
        verbose=False, nocolor=False, width=0
        ):
        """Input parameters are optional to override the defaults.
        sets up our LaymanAPI with defaults or passed in values
        and returns an instance of it"""
        import sys
        try:
            from layman.api import LaymanAPI
            from layman.config import BareConfig
            from layman.output import Message
        except ImportError:
            sys.stderr.write("!!! Layman API import failed.")
            return None
        self.message = Message()
        self.config = BareConfig(
                output=message,
                stdout=None,
                stdin=None,
                stderr=None,
                config=None,
                read_configfile=True,
                quiet=False,
                quietness=4,
                verbose=False,
                nocolor=False,
                width=0
            )
        self.layman = LaymanAPI(self.config,
                             report_errors=True,
                             output=config['output']
                            )
        return _layman
