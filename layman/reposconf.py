#!/usr/bin/python

import os

try:
    # Import for Python3
    import configparser as ConfigParser
except:
    # Import for Python2
    import ConfigParser

from layman.utils import path 

class ConfigHandler:

    def __init__(self, config, overlays):
        
        self.config = config
        self.output = config['output']
        self.overlay = {}
        self.path = config['repos_conf']
        self.storage = config['storage']

        self.read()

        def _read_config(self, config=None):
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
                self._read_file(self.repo_conf)
            else:
                self.output.error('ReposConf: ConfigHandler.read(); Failed to read "'\
                    '%(path)s".\nFile not found.' % ({'path': self.path}))


        def add(self, overlay):
            '''
            Adds an overlay to layman.conf.

            @param overlay: layman.overlay.Overlay object.
            '''
            self.repo_conf.add_section(overlay.name)
            self.repo_conf.set(overlay.name, 'location', path((self.storage, overlay.name)))
            self.repo_conf.set(overlay.name, 'sync-uri', overlay.sources[0].src)
            self.repo_conf.set(overlay.name, 'auto-sync', self.config['auto_sync'])

            return self.write()


        def delete(self, overlay):
            '''
            Deletes an overlay from layman.conf.

            @param overlay: layman.overlay.Overlay object.
            '''
            self.repo_conf.remove_section(overlay.name)

            return self.write()


        def update(self, overlay):
            '''
            Updates an overlay's sync-uri.

            @param overlay: layman.overlay.Overlay object.
            '''
            self.repo_conf.set(overlay.name, 'sync-uri', overlay.sources[0].src)

            return self.write()


        def write(self):
            '''
            Writes changes from ConfigParser to /etc/portage/repos.conf/layman.conf
            '''
            try:
                with open(self.path, 'w') as laymanconf:
                    self.repo_conf.write(laymanconf)
                return True
            except IOError as error:
                self.output.error('ReposConf: ConfigHandler.write(); Failed to write "'\
                    '%(path)s".\nError was:\n%(error)s'\
                    % ({'path': self.path, 'error': str(error)}))
