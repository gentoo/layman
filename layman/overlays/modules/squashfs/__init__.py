# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Squashfs plug-in module for layman.
'''

module_spec = {
    'name': 'squashfs',
    'description': __doc__,
    'provides':{
        'squashfs-module': {
            'name': 'squashfs',
            'class': 'SquashfsOverlay',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync'],
            'func_desc': {
                'add': 'Fetches overlay package and mounts it locally',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Refetches overlay package and mounts it locally',
            },
        }
    }
}

