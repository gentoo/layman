# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Stub plug-in module for layman.
'''

module_spec = {
    'name': 'stub',
    'description': __doc__,
    'provides':{
        'stub-module': {
            'name': 'stub',
            'class': 'StubOverlay',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync', 'update'],
            'func_desc': {
                'add': 'Stub add function',
                'supported': 'Stub supported function',
                'sync': 'Stub sync function',
                'update': 'Stub update function',
            },
        }
    }
}

