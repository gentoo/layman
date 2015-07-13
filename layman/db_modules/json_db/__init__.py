# Copyright 2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
JSON database plug-in module for layman.
'''

module_spec = {
    'name': 'json_db',
    'description': __doc__,
    'provides':{
        'json-module': {
            'name': 'json_db',
            'class': 'DBHandler',
            'description': __doc__,
            'functions': ['add_new', 'read_db', 'write'],
            'func_desc': {
                'add_new': 'Adds overlay(s) from provided database text',
                'read_db': 'Reads the list of overlays from database file',
                'write'  : 'Writes the list of overlays to database file',
            },
        }
    }
}
