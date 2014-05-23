#!/usr/bin/python

import re

import layman.reposconf as reposconf
import layman.makeconf  as makeconf

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

        if isinstance(self.conf_types, str):
            self.conf_types = re.split(',\s+', self.conf_types)

        if not self.conf_types and self.config['require_repoconfig']:
            self.output.error('No Repo configuration type found, but'
                + '\nis required in order to continue...')


    def add(self, overlay):
        if self.config['require_repoconfig']:
            for types in self.conf_types:
                conf = getattr(self.modules[types][0],
                    self.modules[types][1])(self.config, self.overlays)
                conf_ok = conf.add(overlay)
            return conf_ok
        return True

    def delete(self, overlay):
        if self.config['require_repoconfig']:
            for types in self.conf_types:
                conf = getattr(self.modules[types][0],
                    self.modules[types][1])(self.config, self.overlays)
                conf_ok = conf.delete(overlay)
            return conf_ok
        return True


    def update(self, overlay):
        if self.config['require_repoconfig']:
            for types in self.conf_types:
                conf = getattr(self.modules[types][0],
                    self.modules[types][1])(self.config, self.overlays)
                conf_ok = conf.update(overlay)
            return conf_ok
        return True
