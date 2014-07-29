# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Rsync plug-in module for layman.
'''

module_spec = {
    'name': 'rsync',
    'description': __doc__,
    'provides':{
        'rsync-module': {
            'name': 'rsync',
            'class': 'RsyncOverlay',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync'],
            'func_desc': {
                'add': 'Creates the base dir and syncs a rsync repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a rsync sync',
            },
        }
    }
}

