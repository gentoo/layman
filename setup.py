#!/usr/bin/env python

import sys

from distutils.core import setup

# this affects the names of all the directories we do stuff with
sys.path.insert(0, './')
from layman.version import VERSION


modules = [
    'layman.overlays.modules.bzr',
    'layman.overlays.modules.cvs',
    'layman.overlays.modules.darcs',
    'layman.overlays.modules.git',
    'layman.overlays.modules.g_sourcery',
    'layman.overlays.modules.mercurial',
    'layman.overlays.modules.rsync',
    'layman.overlays.modules.squashfs',
    'layman.overlays.modules.stub',
    'layman.overlays.modules.svn',
    'layman.overlays.modules.tar',
    ]


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
      scripts       = ['bin/layman', 'bin/layman-updater'],
      license       = 'GPL',
      )
