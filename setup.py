#!/usr/bin/env python

import sys

from distutils.core import setup

# this affects the names of all the directories we do stuff with
sys.path.insert(0, './')
from layman.version import VERSION


setup(name          = 'layman',
      version       = VERSION,
      description   = 'Python script for retrieving gentoo overlays',
      author        = 'Gunnar Wrobel',
      author_email  = 'wrobel@gentoo.org',
      url           = 'http://projects.gunnarwrobel.de/scripts',
      packages      = ['layman', 'layman.overlays'],
      scripts       = ['bin/layman'],
      license       = 'GPL',
      )
