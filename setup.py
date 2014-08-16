#!/usr/bin/env python

import os
import sys

from distutils.core import setup

# this affects the names of all the directories we do stuff with
sys.path.insert(0, './')
from layman.version import VERSION

SELECTABLE = "bzr cvs darcs git g_sorcery mercurial rsync squashfs svn tar"
# get the USE from the environment, default to all selectable modules
# split them so we don't get substring matches
USE = os.environ.get("USE", SELECTABLE).split()

modules = ['layman.overlays.modules.stub']

for mod in SELECTABLE.split():
    if mod in USE:
        modules.append('layman.overlays.modules.%s' %mod)


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
