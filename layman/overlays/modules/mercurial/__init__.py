# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
Mercurial plug-in module for layman.
'''

module_spec = {
    'name': 'mercurial',
    'description': __doc__,
    'provides':{
        'mercurial-module': {
            'name': 'mercurial',
            'class': 'MercurialOverlay',
            'sourcefile': 'mercurial',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync', 'update'],
            'func_desc': {
                'add': 'Performs a hg clone on a repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a hg pull on the repository',
                'update': 'Updates a mercurial overlay\'s source URL',
            },
        }
    }
}

