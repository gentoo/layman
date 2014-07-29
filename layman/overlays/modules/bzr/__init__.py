# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Bazaar plug-in module for layman.
'''

module_spec = {
    'name': 'bzr',
    'description': __doc__,
    'provides':{
        'bzr-module': {
            'name': 'bzr',
            'class': 'BzrOverlay',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync', 'update'],
            'func_desc': {
                'add': 'Performs a bzr get on a repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a bzr pull on the repository',
                'update': 'Updates a bzr overlay\'s source URL via bzr bind',
            },
        }
    }
}

