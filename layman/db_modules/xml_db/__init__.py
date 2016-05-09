# Copyright 2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
XML database plug-in module for layman.
'''

module_spec = {
    'name': 'xml_db',
    'description': __doc__,
    'provides':{
        'xml-module': {
            'name': 'xml_db',
            'class': 'DBHandler',
            'sourcefile': 'xml_db',
            'description': __doc__,
            'functions': ['add_new', 'read_db', 'remove', 'write'],
            'func_desc': {
                'add_new': 'Adds overlay(s) from provided database text',
                'read_db': 'Reads the list of overlays from database file',
                'remove' : 'Removes overlay from installed overlays list',
                'write'  : 'Writes the list of overlays to database file',
            },
        }
    }
}
