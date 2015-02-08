# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

'''Layman plug-in module for portage.
Performs layman sync actions for layman overlays.
'''

import os

from portage.sync.config_checks import CheckSyncConfig


try:
    import layman
    config_class = 'PyLayman'
    del layman
except ImportError:
    config_class = 'Layman'


module_spec = {
    'name': 'laymansync',
    'description': __doc__,
    'provides':{
        'layman-module': {
            'name': 'laymansync',
            'class': config_class,
            'description': __doc__,
            'functions': ['sync', 'new', 'exists'],
            'func_desc': {
                'sync': 'Performs a layman sync of the specified overlay',
                'new': 'Performs a layman add of the specified overlay',
                'exists': 'Returns a boolean of whether the specified dir ' +
                    'exists and is a valid repository',
            },
            'validate_config': CheckSyncConfig,
        },
    }
}
