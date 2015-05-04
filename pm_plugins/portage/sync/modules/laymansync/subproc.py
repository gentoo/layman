# Copyright 2014-2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
'''Layman module for portage using a subprocess call'''

import logging

import portage
from portage import os
from portage.util import writemsg_level
from portage.output import create_color_func
good = create_color_func("GOOD")
bad = create_color_func("BAD")
warn = create_color_func("WARN")
from portage.sync.syncbase import NewBase


class Layman(NewBase):
    '''
    Layman sync class which makes use of a subprocess call to
    execute desired layman actions.
    '''

    short_desc = "Perform sync operations on layman based repositories"

    @staticmethod
    def name():
        '''
        Returns sync plugin name.

        @rtype str
        '''
        return "Layman"


    def __init__(self):
        NewBase.__init__(self, 'layman', 'app-portage/layman')


    def _get_optargs(self, args):
        '''
        Gets optional layman arguments.

        @params args: dict of current subprocess args.
        '''
        if self.settings:
            if self.settings.get('NOCOLOR'):
                args.append('-N')
            if self.settings.get('PORTAGE_QUIET'):
                args.append('-q')


    def new(self, **kwargs):
        '''Use layman to install the repository'''
        if kwargs:
            self._kwargs(kwargs)
        args = []
        msg = '>>> Starting to add new layman overlay %(repo)s'\
            % ({'repo': self.repo.name})
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + '\n')

        location = self.repo.location.replace(self.repo.name, '')

        args.append('layman')
        self._get_optargs(args)
        args.append('--storage')
        args.append(location)
        args.append('-a')
        args.append(self.repo.name)

        command = ' '.join(args)

        exitcode = portage.process.spawn_bash("%(command)s" % \
            ({'command': command}),
            **portage._native_kwargs(self.spawn_kwargs))
        if exitcode != os.EX_OK:
            msg = "!!! layman add error in %(repo)s"\
                % ({'repo': self.repo.name})
            self.logger(self.xterm_titles, msg)
            writemsg_level(msg + "\n", level=logging.ERROR, noiselevel=-1)
            return (exitcode, False)
        msg = ">>> Addition of layman repo succeeded: %(repo)s"\
            % ({'repo': self.repo.name})
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + "\n")
        msg = '>>> laymansync sez... "Hasta la add ya, baby!"'
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + "\n")

        return (exitcode, True)


    def update(self):
        ''' Update existing repository'''
        args = []

        msg = '>>> Starting layman sync for %(repo)s...'\
            % ({'repo': self.repo.name})
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + '\n')

        location = self.repo.location.replace(self.repo.name, '')

        args.append('layman')
        self._get_optargs(args)
        args.append('--storage')
        args.append(location)
        args.append('-s')
        args.append(self.repo.name)

        command = ' '.join(args)
        exitcode = portage.process.spawn_bash("%(command)s" % \
            ({'command': command}),
            **portage._native_kwargs(self.spawn_kwargs))

        if exitcode != os.EX_OK:
            exitcode = self.new()[0]
            if exitcode != os.EX_OK:
                msg = "!!! layman sync error in %(repo)s"\
                    % ({'repo': self.repo.name})
                self.logger(self.xterm_titles, msg)
                writemsg_level(msg + "\n", level=logging.ERROR, noiselevel=-1)
                return (exitcode, False)
            else:
                return (exitcode, True)

        msg = ">>> layman sync succeeded: %(repo)s"\
            % ({'repo': self.repo.name})
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + "\n")
        msg = '>>> laymansync sez... "Hasta la sync ya, baby!"'
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + "\n")

        return (exitcode, True)

