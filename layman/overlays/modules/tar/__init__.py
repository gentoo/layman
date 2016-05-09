# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Tar plug-in module for layman.
'''

module_spec = {
    'name': 'tar',
    'description': __doc__,
    'provides':{
        'tar-module': {
            'name': 'tar',
            'class': 'TarOverlay',
            'sourcefile': 'tar',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync'],
            'func_desc': {
                'add': 'Creates the base dir and extracts the tar repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a sync on the repository',
            },
        }
    }
}

