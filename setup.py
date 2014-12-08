#!/usr/bin/env python

import os
import sys

from distutils.core import setup

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

SYNC_PLUGINS = {
    'sync-plugin-portage': 'layman.laymanator',
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

for plugin in sorted(SYNC_PLUGINS):
    if plugin in USE:
        modules.append(SYNC_PLUGIN)

setup(name          = 'layman',
      version       = VERSION,
      description   = 'Python script for retrieving gentoo overlays',
      author        = 'Brian Dolbec, Gunnar Wrobel (original author retired)',
      author_email  = 'dolsen@gentoo',
      url           = 'http://layman.sourceforge.net/, ' +\
        'http://git.overlays.gentoo.org/gitweb/?p=proj/layman.git;a=summary',
      packages      = ['layman', 'layman.config_modules',
        'layman.config_modules.makeconf', 'layman.config_modules.reposconf',
        'layman.overlays', 'layman.overlays.modules',
        ] + modules,
      scripts       = ['bin/layman', 'bin/layman-overlay-maker',
                       'bin/layman-mounter', 'bin/layman-updater'],
      license       = 'GPL',
      )
