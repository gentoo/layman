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

import re
import sys

import layman.reposconf as reposconf
import layman.makeconf  as makeconf

if sys.hexversion >= 0x30200f0:
    STR = str
else:
    STR = basestring

class RepoConfManager:

    def __init__(self, config, overlays):

        #TODO add custom_conf_type support
        self.config = config
        self.conf_types = config['conf_type']
        self.output = config['output']
        self.overlays = overlays

        self.modules = {
        'make.conf':  (makeconf,  'ConfigHandler'),
        'repos.conf': (reposconf, 'ConfigHandler')
        }

        if isinstance(self.conf_types, STR):
            self.conf_types = re.split(',\s+', self.conf_types)

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
                conf = getattr(self.modules[types][0],
                    self.modules[types][1])(self.config, self.overlays)
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
                conf = getattr(self.modules[types][0],
                    self.modules[types][1])(self.config, self.overlays)
                conf_ok = conf.delete(overlay)
                results.append(conf_ok)
            return results
        return [True]


    def update(self, overlay):
        '''
        Updates the source URL for the specified config type(s).
    
        @param overlay: layman.overlay.Overlay instance.
        @return boolean: represents success or failure.
        '''
        if self.config['require_repoconfig']:
            results = []
            for types in self.conf_types:
                conf = getattr(self.modules[types][0],
                    self.modules[types][1])(self.config, self.overlays)
                conf_ok = conf.update(overlay)
                results.append(conf_ok)
            return results
        return [True]
