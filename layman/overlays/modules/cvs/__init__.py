# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''
CVS plug-in module for layman.
'''

module_spec = {
    'name': 'cvs',
    'description': __doc__,
    'provides':{
        'cvs-module': {
            'name': 'cvs',
            'class': 'CvsOverlay',
            'sourcefile': 'cvs',
            'description': __doc__,
            'functions': ['add', 'supported', 'sync', 'update'],
            'func_desc': {
                'add': 'Performs a cvs checkout on a repository',
                'supported': 'Confirms if overlay type is supported',
                'sync': 'Performs a cvs update on the repository',
                'update': 'Updates a cvs overlay\'s source URL',
            },
        }
    }
}

