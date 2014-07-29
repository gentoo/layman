# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Subversion plug-in module for layman.
'''

module_spec = {
    'name': 'svn',
    'description': __doc__,
    'provides':{
        'svn-module': {
            'name': 'svn',
            'class': 'SvnOverlay',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync', 'update'],
            'func_desc': {
                'add': 'Performs a svn checkout on a repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a svn up on the repository',
                'update': 'Updates a svn overlay\'s source URL',
            },
        }
    }
}

