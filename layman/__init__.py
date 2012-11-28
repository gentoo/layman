#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Layman is a complete library for the operation and maintainance
on all gentoo repositories and overlays
"""

import sys

try:
    from layman.api import LaymanAPI
    from layman.config import BareConfig
    from layman.output import Message
except ImportError:
    sys.stderr.write("!!! Layman API imports failed.")
    raise



class Layman(LaymanAPI):
    """A complete high level interface capable of performing all
    overlay repository actions."""

    def __init__(self, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr,
        config=None, read_configfile=True, quiet=False, quietness=4,
        verbose=False, nocolor=False, width=0, root=None
        ):
        """Input parameters are optional to override the defaults.
        sets up our LaymanAPI with defaults or passed in values
        and returns an instance of it"""
        self.message = Message(out=stdout, err=stderr)
        self.config = BareConfig(
                output=self.message,
                stdout=stdout,
                stdin=stdin,
                stderr=stderr,
                config=config,
                read_configfile=read_configfile,
                quiet=quiet,
                quietness=quietness,
                verbose=verbose,
                nocolor=nocolor,
                width=width,
                root=root
            )
        LaymanAPI.__init__(self, self.config,
                             report_errors=True,
                             output=self.config['output']
                            )
        return
