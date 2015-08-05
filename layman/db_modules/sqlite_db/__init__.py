# Copyright 2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
SQLite database plug-in module for layman.
'''

module_spec = {
    'name': 'sqlite_db',
    'description': __doc__,
    'provides':{
        'sqlite-module': {
            'name': 'sqlite_db',
            'class': 'DBHandler',
            'description': __doc__,
            'functions': ['add_new', 'read_db', 'remove', 'write'],
            'func_desc': {
                'add_new': 'Adds overlay(s) from provided database file',
                'read_db': 'Reads the list of overlays from database file',
                'remove' : 'Removes overlay from provided database file',
                'write'  : 'Writes the list of overlays to database file',
            },
        }
    }
}
