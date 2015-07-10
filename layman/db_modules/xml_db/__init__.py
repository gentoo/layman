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
            'description': __doc__,
            'functions': ['add_new', 'read_db', 'write'],
            'func_desc': {
                'add_new': 'Adds new overlay(s) to database',
                'read_db': 'Reads the list of registered overlays from config',
                'write'  : 'Writes the list of registered overlay to config',
            },
        }
    }
}
