# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Darcs plug-in module for layman.
'''

module_spec = {
    'name': 'darcs',
    'description': __doc__,
    'provides':{
        'darcs-module': {
            'name': 'darcs',
            'class': 'DarcsOverlay',
            'sourcefile': 'darcs',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync'],
            'func_desc': {
                'add': 'Performs a darcs get on a repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a darcs pull on the repository',
            },
        }
    }
}

