#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Copyright 2005 - 2008 Gunnar Wrobel
              2011 - Brian Dolbec
 Distributed under the terms of the GNU General Public License v2
"""


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


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
