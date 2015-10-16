#!/usr/bin/env python

import os
import sys

from distutils.core import setup, Command
from distutils.dir_util import copy_tree


# this affects the names of all the directories we do stuff with
sys.path.insert(0, './')
from layman.version import VERSION

# leave rsync and tar commented out since they are part of system set
# make them installed by default
SELECTABLE = {
    'bazaar': 'bzr',
    'cvs': 'cvs',
    'darcs': 'darcs',
    'git': 'git',
    'g-sorcery': 'g_sorcery',
    'mercurial': 'mercurial',
    #'rsync': 'rsync',
    'squashfs': 'squashfs',
    'subversion': 'svn',
    #'tar': 'tar',
    }

use_defaults = ' '.join(list(SELECTABLE))

DB_PLUGINS = {
    'sqlite': 'layman.db_modules.sqlite_db'
}

SYNC_PLUGINS = {
    'sync-plugin-portage': 'portage.sync.modules.laymansync',
}

# get the USE from the environment, default to all selectable modules
# split them so we don't get substring matches
USE = os.environ.get("USE", use_defaults).split()

modules = [
    'layman.overlays.modules.rsync',
    'layman.overlays.modules.stub',
    'layman.overlays.modules.tar',
    ]

for mod in sorted(SELECTABLE):
    if mod in USE:
        modules.append('layman.overlays.modules.%s' % SELECTABLE[mod])

for plugin in sorted(DB_PLUGINS):
    if plugin in USE:
        modules.append(DB_PLUGINS[plugin])

for plugin in sorted(SYNC_PLUGINS):
    if plugin in USE:
        modules.append(SYNC_PLUGINS[plugin])

class setup_plugins(Command):
    """ Perform moves for the plugins into base namespace
    so they can be installed. """

    user_options = [
    ]

    def initialize_options(self):
        self.build_base = None

    def finalize_options(self):
        self.set_undefined_options('build',
            ('build_base', 'build_base'))

    def run(self):
        for plugin in sorted(SYNC_PLUGINS):
            if plugin in USE:
                source = os.path.join('pm_plugins',
                    SYNC_PLUGINS[plugin].split('.')[0])
                target = SYNC_PLUGINS[plugin].split('.')[0]
                copy_tree(source, target)


setup(
    name          = 'layman',
    version       = VERSION,
    description   = 'Python script for retrieving gentoo overlays',
    author        = 'Brian Dolbec, Gunnar Wrobel (original author retired)',
    author_email  = 'dolsen@gentoo',
    url           = 'http://layman.sourceforge.net/, ' +\
        'http://git.overlays.gentoo.org/gitweb/?p=proj/layman.git;a=summary',
    packages      = ['layman', 'layman.config_modules',
        'layman.config_modules.makeconf', 'layman.config_modules.reposconf',
        'layman.db_modules', 'layman.db_modules.json_db',
        'layman.db_modules.xml_db', 'layman.overlays',
        'layman.overlays.modules',
        ] + modules,
    scripts       = ['bin/layman', 'bin/layman-overlay-maker',
                       'bin/layman-mounter', 'bin/layman-updater'],
    cmdclass = {
        'setup_plugins': setup_plugins,
        },
    license       = 'GPL',
    )
