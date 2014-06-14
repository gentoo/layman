#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# REPOS-DOT-CONF HANDLING
#################################################################################
# File:       reposconf.py
#
#             Handles modifications to /etc/portage/repos.conf/layman.conf
#
# Copyright:
#             (c) 2014 Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Devan Franchini <twitch153@gentoo.org>
#

import os

try:
    # Import for Python3
    import configparser as ConfigParser
except:
    # Import for Python2
    import ConfigParser

from   layman.compatibility  import fileopen
from   layman.utils          import path

class ConfigHandler:

    def __init__(self, config, overlays):
        
        self.config = config
        self.output = config['output']
        self.overlay = {}
        self.path = config['repos_conf']
        self.storage = config['storage']

        self.read()

    def _read_config(self, config=None):
        '''
        Reads the config file using a specified
        ConfigParser.ConfigParser instance.

        @param config: ConfigParser.ConfigParser instance.
        '''
        try:
            read_files = config.read(self.path)
                
            if not read_files:
                self.output.warn("Warning, not able to parse config file: %(path)s"\
                    % ({'path':self.path}))
        except IOError as error:
            self.output.error('ReposConf: ConfigHandler.read(); Failed to read "'\
                '%(path)s".\nError was:\n%(error)s'\
                % ({'path': self.path, 'error': str(error)}))


    def read(self):
        '''
        Reads the repos.conf config file from
        /etc/portage/repos.conf/layman.conf
        '''
        if os.path.isfile(self.path):
            self.repo_conf = ConfigParser.ConfigParser()
            self._read_config(self.repo_conf)
        else:
            self.output.error('ReposConf: ConfigHandler.read(); Failed to read "'\
                '%(path)s".\nFile not found.' % ({'path': self.path}))


    def add(self, overlay):
        '''
        Adds overlay information to the specified config file.

        @param overlay: layman.overlay.Overlay instance.
        @return boolean: reflects a successful/failed write to the config file.
        '''
        self.repo_conf.add_section(overlay.name)
        self.repo_conf.set(overlay.name, 'priority', overlay.priority)
        self.repo_conf.set(overlay.name, 'location', path((self.storage, overlay.name)))
        self.repo_conf.set(overlay.name, 'sync-uri', overlay.sources[0].src)
        self.repo_conf.set(overlay.name, 'auto-sync', self.config['auto_sync'])

        return self.write()


    def delete(self, overlay):
        '''
        Deletes overlay information from the specified config file.

        @param overlay: layman.overlay.Overlay instance.
        @return boolean: reflects a successful/failed write to the config file.
        '''
        self.repo_conf.remove_section(overlay.name)

        return self.write()


    def update(self, overlay):
        '''
        Updates the source URL for the specified config file.

        @param overlay: layman.overlay.Overlay instance.
        @return boolean: reflects a successful/failed write to the config file.
        '''
        self.repo_conf.set(overlay.name, 'sync-uri', overlay.sources[0].src)

        return self.write()


    def write(self):
        '''
        Writes changes from ConfigParser to /etc/portage/repos.conf/layman.conf.

        @return boolean: represents a successful write.
        '''
        try:
            with fileopen(self.path, 'w') as laymanconf:
                self.repo_conf.write(laymanconf)

            return True
        except IOError as error:
            self.output.error('ReposConf: ConfigHandler.write(); Failed to write "'\
                '%(path)s".\nError was:\n%(error)s'\
                % ({'path': self.path, 'error': str(error)}))
