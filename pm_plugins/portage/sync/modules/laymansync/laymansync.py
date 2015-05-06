# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
'''Layman module for portage'''



try:
    from portage.sync.modules.laymansync.pylayman import PyLayman
    CONFIG_CLASS = PyLayman
except ImportError:
    from portage.sync.modules.laymansync.subproc import Layman
    CONFIG_CLASS = Layman

