# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Makeconf plug-in module for layman.
'''

module_spec = {
    'name': 'makeconf',
    'description': __doc__,
    'provides':{
        'makeconf-module': {
            'name': 'makeconf',
            'class': 'ConfigHandler',
            'sourcefile': 'makeconf',
            'description': __doc__,
            'functions': ['add', 'delete', 'disable', 'enable', 'read',
                          'update', 'write'],
            'func_desc': {
                'add': 'Adds overlay dir string to config',
                'delete': 'Removes overlay dir string from config',
                'disable': 'Moves overlay dir string to DISBALED var',
                'enable': 'Moves overlay dir string to ENABLED var',
                'read': 'Reads the list of registered overlays from config',
                'update': 'Nothing, stub function',
                'write': 'Writes the list of registered overlay to config',
            },
        }
    }
}
