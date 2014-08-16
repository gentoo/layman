#!/usr/bin/env python

import sys

from distutils.core import setup

# this affects the names of all the directories we do stuff with
sys.path.insert(0, './')
from layman.version import VERSION


modules = [
    'layman.overlays.moudules.bzr',
    'layman.overlays.moudules.cvs',
    'layman.overlays.moudules.darcs',
    'layman.overlays.moudules.git',
    'layman.overlays.moudules.g_sourcery',
    'layman.overlays.moudules.mercurial',
    'layman.overlays.moudules.rsync',
    'layman.overlays.moudules.squashfs',
    'layman.overlays.moudules.stub',
    'layman.overlays.moudules.svn',
    'layman.overlays.moudules.tar',
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
