#!/usr/bin/env python

import sys

from distutils.core import setup

# this affects the names of all the directories we do stuff with
sys.path.insert(0, './')
from layman.version import VERSION


setup(name          = 'layman',
      version       = VERSION,
      description   = 'Python script for retrieving gentoo overlays',
      author        = 'Gunnar Wrobel, Brian Dolbec',
      author_email  = 'wrobel@gentoo.org, brian.dolbec@gmail.com',
      url           = 'http://layman.sourceforge.net/, ' +\
        'http://git.overlays.gentoo.org/gitweb/?p=proj/layman.git;a=summary',
      packages      = ['layman', 'layman.overlays'],
      scripts       = ['bin/layman'],
      license       = 'GPL',
      )
