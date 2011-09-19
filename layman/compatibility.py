#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Copyright 2005 - 2008 Gunnar Wrobel
              2011 - Brian Dolbec
 Distributed under the terms of the GNU General Public License v2
"""

import sys, types


def encode(text, enc="UTF-8"):
    """py2, py3 compatibility function"""
    if hasattr(text, 'decode'):
        try:
            return text.decode(enc)
        except UnicodeEncodeError:
            return unicode(text)
    return str(text)


def fileopen(path, mode='r', enc="UTF-8"):
    """py2, py3 compatibility function"""
    try:
        f = open(path, mode, encoding=enc)
    except TypeError:
        f = open(path, mode)
    return f

