# Copyright 2014-2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
'''Layman module for portage using the lyman api'''

import logging

import layman.overlays.overlay as Overlay
from layman.api import LaymanAPI
from layman.config import BareConfig, OptionConfig
from layman.maker import Interactive
from layman.output import Message
from layman.utils import reload_config


from portage import os
from portage.util import writemsg_level
from portage.output import create_color_func
good = create_color_func("GOOD")
bad = create_color_func("BAD")
warn = create_color_func("WARN")
from portage.sync.syncbase import NewBase

import sys

def create_overlay_package(config=None, repo=None, logger=None, xterm_titles=None):
    '''
    Creates a layman overlay object
    from the given repos.conf repo info.

    @params config: layman.config class object
    @params repo: portage.repo class object
    @rtype tuple: overlay name and layman.overlay object or None
    '''
    if repo:
        overlay = {'sources': []}
        desc = 'Defined and created from info in %(repo)s config file...'\
                % ({'repo': repo.name})
        if not config:
            config = BareConfig()
        if not repo.branch:
            repo.branch = ''

        overlay['name'] = repo.name
        overlay['descriptions'] = [desc]
        overlay['owner_name'] = 'repos.conf'
        overlay['owner_email'] = '127.0.0.1'
        overlay['sources'].append([repo.sync_uri, repo.layman_type, repo.branch])
        overlay['priority'] = repo.priority

        ovl = Overlay.Overlay(config=config, ovl_dict=overlay, ignore=1)
        return (repo.name, ovl)

    msg = '!!! laymansync sez... Error: repo not found.'
    if logger and xterm_titles:
        logger(xterm_titles, msg)
    writemsg_level(msg + '\n', level=logging.ERROR, noiselevel=-1)
    return None



class PyLayman(NewBase):
    '''
    Layman sync class which makes use of layman's modules to
    perform desired actions.
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

        self._layman = None
        self.storage = ''
        self.current_storage = ''


    def _get_layman_api(self):
        '''
        Initializes layman api.

        @rtype layman.api.LaymanAPI instance
        '''
        # Make it so that we aren't initializing the
        # LaymanAPI instance if it already exists and
        # if the current storage location hasn't been
        # changed for the new repository.
        self.storage = self.repo.location.replace(self.repo.name, '')

        if self._layman and self.storage in self.current_storage:
            return self._layman

        config = BareConfig()
        configdir = {'configdir': config.get_option('configdir')}

        self.message = Message(out=sys.stdout, err=sys.stderr)
        self.current_storage = self.storage
        options = {
            'config': config.get_option('config') % (configdir),
            'quiet': self.settings.get('PORTAGE_QUIET'),
            'quietness': config.get_option('quietness'),
            'overlay_defs': config.get_option('overlay_defs') % (configdir),
            'output': self.message,
            'nocolor': self.settings.get('NOCOLOR'),
            'root': self.settings.get('EROOT'),
            'storage': self.current_storage,
            'verbose': self.settings.get('PORTAGE_VERBOSE'),
            'width': self.settings.get('COLUMNWIDTH'),

        }
        self.config = OptionConfig(options=options, root=options['root'])

        # Reloads config to read custom overlay
        # xml files.
        reload_config(self.config)

        layman_api = LaymanAPI(self.config,
                               report_errors=True,
                               output=self.config['output']
                               )

        self._layman = layman_api

        return layman_api


    def _eval_exitcode(self, exitcode):
        '''
        Evaluates the boolean returned by layman's API
        when performing a task and returns the proper exitcode.

        @params exitcode: boolean value reflecting the successful
                          execution of a task.
        @rtype int
        '''
        if exitcode == True:
            return 0
        return 1


    def new(self, **kwargs):
        '''Do the initial download and install of the repository'''
        layman_inst = self._get_layman_api()
        # Update the remote list before adding anything.
        layman_inst.fetch_remote_list()
        available_overlays = layman_inst.get_available(dbreload=True)

        msg = '>>> Starting to add new layman overlay %(repo)s'\
            % ({'repo': self.repo.name})
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + '\n')

        if self.repo.name not in available_overlays:
            overlay_package = create_overlay_package(repo=self.repo,\
                                logger=self.logger,\
                                xterm_titles=self.xterm_titles)
            create_overlay_xml = Interactive(config=self.config)
            path = self.config.get_option('overlay_defs') + '/reposconf.xml'
            result = create_overlay_xml(overlay_package=overlay_package,
                        path=path)

            if not result:
                msg = '!!! layman add error in %(repo)s: Failed to add'\
                      '%(repo)s to %(path)s' % ({'repo': self.repo.name,
                                                  'path': path})
                self.logger(self.xterm_titles, msg)
                writemsg_level(msg + '\n', level=logging.ERROR, noiselevel=-1)
                return (1, False)

        results = layman_inst.add_repos(self.repo.name)
        exitcode = self._eval_exitcode(results)

        if exitcode != os.EX_OK:
            msg = "!!! layman add error in %(repo)s"\
                % ({'repo': self.repo.name})
            self.logger(self.xterm_titles, msg)
            writemsg_level(msg + "\n", level=logging.ERROR, noiselevel=-1)
            return (exitcode, False)
        msg = ">>> Addition of layman repo succeeded: %(repo)s"\
            % ({'repo': self.repo.name})
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + '\n')
        msg = '>>> laymansync sez... "Hasta la add ya, baby!"'
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + '\n')

        return (exitcode, True)

    def update(self):
        ''' Update existing repository'''
        layman_inst = self._get_layman_api()

        msg = '>>> Starting layman sync for %(repo)s...'\
            % ({'repo': self.repo.name})
        self.logger(self.xterm_titles, msg)
        writemsg_level(msg + '\n')

        results = layman_inst.sync(self.repo.name)
        exitcode = self._eval_exitcode(results)

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
