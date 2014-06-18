#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN CONSTANTS
#################################################################################
# File:       constants.py
#
#             Handles layman actions via the command line interface.
#
# Copyright:
#             (c) 2010 - 2011
#                   Gunnar Wrobel
#                   Brian Dolbec
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Brian Dolbec <brian.dolbec@gmail.com
#
''' Provides the command line actions that can be performed by layman.'''

from __future__ import unicode_literals

__version__ = "$Id: constants.py 2011-01-16 23:52 PST Brian Dolbec$"




#################################################################################
##
## Color codes (taken from portage)
##
#################################################################################

esc_seq = '\x1b['

codes = {}
codes['reset']     = esc_seq + '39;49;00m'
codes['red']       = esc_seq + '31;01m'
codes['green']     = esc_seq + '32;01m'
codes['yellow']    = esc_seq + '33;01m'
codes['turquoise'] = esc_seq + '36;01m'


NOT_OFFICIAL_MSG = '*** This is not an official gentoo overlay ***\n'
NOT_SUPPORTED_MSG = '*** You are lacking the necessary tools' +\
    ' to install this overlay ***\n'


OFF = 0
WARN_LEVEL = 4
INFO_LEVEL = 4
NOTE_LEVEL = 4
DEBUG_LEVEL = 4
DEBUG_VERBOSITY = 2

FAILURE = 1
SUCCEED = 0

#################################################################################
##
## Overlay components
##
#################################################################################

COMPONENT_DEFAULTS  = ['name', 'description', 'owner', 'type', 'sources']
POSSIBLE_COMPONENTS = ['name', 'description', 'homepage', 'owner', 'quality',
                       'priority', 'sources', 'branch', 'irc', 'feeds']
