# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Reposconf plug-in module for layman.
'''

module_spec = {
    'name': 'reposconf',
    'description': __doc__,
    'provides':{
        'reposconf-module': {
            'name': 'reposconf',
            'class': 'ConfigHandler',
            'sourcefile': 'reposconf',
            'description': __doc__,
            'functions': ['add', 'delete', 'disable', 'enable', 'read',
                          'update', 'write'],
            'func_desc': {
                'add': 'Adds overlay information to config',
                'delete': 'Removes overlay information from config',
                'disable': 'Comments out specific overlay config entry',
                'enable': 'Uncomments specific overlay config entry',
                'read': 'Reads the config file',
                'update': 'Updates the source URL for the specified overlay',
                'write': 'Writes the overlay information to the config',
            },
        }
    }
}
