# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Git plug-in module for layman.
'''

module_spec = {
    'name': 'git',
    'description': __doc__,
    'provides':{
        'git-module': {
            'name': 'git',
            'class': 'GitOverlay',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync', 'update'],
            'func_desc': {
                'add': 'Performs a git clone on a repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a git pull on the repository',
                'update': 'Updates a git overlay\'s source URL',
            },
        }
    }
}

