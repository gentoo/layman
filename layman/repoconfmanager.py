#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# REPO-CONFIG-MANAGER
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
import re
import sys

from layman.module import Modules, InvalidModuleName

if sys.hexversion >= 0x30200f0:
    STR = str
else:
    STR = basestring

MOD_PATH = path = os.path.join(os.path.dirname(__file__), 'config_modules')

class RepoConfManager:

    def __init__(self, config, overlays):

        #TODO add custom_conf_type support
        self.config = config
        self.conf_types = config['conf_type']
        self.output = config['output']
        self.overlays = overlays
        self.module_controller = Modules(path=MOD_PATH,
                                         namepath='layman.config_modules',
                                         output=self.output)

        if isinstance(self.conf_types, STR):
            self.conf_types = [x.strip() for x in self.conf_types.split(',')]

        if not self.conf_types and self.config['require_repoconfig']:
            self.output.error('No Repo configuration type found, but'
                + '\nis required in order to continue...')


    def add(self, overlay):
        '''
        Adds overlay information to the specified config type(s).

        @param overlay: layman.overlay.Overlay instance.
        @return boolean: represents success or failure.
        '''
        if self.config['require_repoconfig']:
            results = []
            for types in self.conf_types:
                types = types.replace('.', '')
                conf = self.module_controller.get_class(types)\
                                  (self.config, self.overlays)
                conf_ok = conf.add(overlay)
                results.append(conf_ok)
            return results
        return [True]



    def delete(self, overlay):
        '''
        Deletes overlay information from the specified config type(s).

        @param overlay: layman.overlay.Overlay instance.
        @return boolean: represents success or failure.
        '''
        if self.config['require_repoconfig']:
            results = []
            for types in self.conf_types:
                types = types.replace('.', '')
                conf = self.module_controller.get_class(types)\
                                  (self.config, self.overlays)
                conf_ok = conf.delete(overlay)
                results.append(conf_ok)
            return results
        return [True]


    def disable(self, overlay):
        '''
        Allows an overlay to become no longer accessible to portage
        without deleting the overlay.

        @param overlay: layman.overlay.Overlay instance.
        @return boolean: represents success or failure.
        '''
        if self.config['require_repoconfig']:
            for types in self.conf_types:
                types = types.replace('.', '')
                conf = self.module_controller.get_class(types)\
                                  (self.config, self.overlays)
                conf_ok = conf.disable(overlay)
            return conf_ok
        return True
                                                                                                                                                

    def enable(self, overlay):
        '''
        Allows an overlay to become accessible to portage
        after overlay was "forgotten".

        @param overlay: layman.overlay.Overlay instance.
        @return boolean: represents success or failure.
        '''
        if self.config['require_repoconfig']:
            for types in self.conf_types:
                types = types.replace('.', '')
                conf = self.module_controller.get_class(types)\
                                  (self.config, self.overlays)
                conf_ok = conf.enable(overlay)
            return conf_ok
        return True

    
    def update(self, overlay):
        '''
        Updates the source URL for the specified config type(s).
    
        @param overlay: layman.overlay.Overlay instance.
        @return boolean: represents success or failure.
        '''
        if self.config['require_repoconfig']:
            results = []
            for types in self.conf_types:
                types = types.replace('.', '')
                conf = self.module_controller.get_class(types)\
                                  (self.config, self.overlays)
                conf_ok = conf.update(overlay)
                results.append(conf_ok)
            return results
        return [True]
