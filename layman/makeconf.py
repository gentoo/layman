#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# MAKE-DOT-CONF HANDLING
#################################################################################
# File:       makeconf.py
#
#             Handles modifications to /var/layman/make.conf
#
# Copyright:
#             (c) 2005 - 2009 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#

from __future__ import unicode_literals

import os
import codecs
import re

from layman.utils import path
from layman.compatibility import cmp_to_key, fileopen

#===============================================================================
#
# Helper class ConfigHandler
#
#-------------------------------------------------------------------------------

class ConfigHandler:
    '''
    Handles modifications to /var/layman/make.conf

    Check that an add/remove cycle does not modify the make.conf:

    >>> import hashlib
    >>> import tempfile
    >>> tmpdir = tempfile.mkdtemp(prefix="laymantmp_")
    >>> write = os.path.join(tmpdir, 'make.conf')
    >>> here = os.path.dirname(os.path.realpath(__file__))
    >>> config = {'installed' :
    ...           here + '/tests/testfiles/global-overlays.xml',
    ...           'make_conf' : here + '/tests/testfiles/make.conf',
    ...           'nocheck'    : True,
    ...           'storage'   : '/var/lib/layman',
    ...           'quietness':3}
    >>> b = DB(config)
    >>> a = ConfigHandler(config, b.overlays)
    >>> o_md5 = str(hashlib.md5(open(here + '/tests/testfiles/make.conf').read()).hexdigest())
    >>> a.path = write
    >>> a.add(b.overlays['wrobel-stable'])
    >>> [i.name for i in a.overlays]
    ['wrobel-stable', 'wrobel-stable']
    >>> a.add(b.overlays['wrobel'])
    >>> [i.name for i in a.overlays]
    ['wrobel', 'wrobel-stable', 'wrobel-stable']
    >>> a.delete(b.overlays['wrobel-stable'])
    >>> [i.name for i in a.overlays]
    ['wrobel']
    >>> a.add(b.overlays['wrobel-stable'])
    >>> [i.name for i in a.overlays]
    ['wrobel', 'wrobel-stable']
    >>> a.delete(b.overlays['wrobel'])
    >>> n_md5 = str(hashlib.md5(open(write).read()).hexdigest())
    >>> o_md5 == n_md5
    True
    >>> os.unlink(write)
    >>> import shutil
    >>> shutil.rmtree(tmpdir)
    '''

    my_re = re.compile('PORTDIR_OVERLAY\s*=\s*"([^"]*)"')

    def __init__(self, config, overlays):

        self.config = config
        self.path = config['make_conf']
        self.storage = config['storage']
        self.data = ''
        self.db = overlays
        self.overlays = []
        self.extra = []
        self.output = config['output']

        self.read(True)

    def add(self, overlay):
        '''
        Add an overlay to make.conf.

        >>> import tempfile
        >>> tmpdir = tempfile.mkdtemp(prefix="laymantmp_")
        >>> write = os.path.join(tmpdir, 'make.conf')
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'installed' :
        ...           here + '/tests/testfiles/global-overlays.xml',
        ...           'make_conf' : here + '/tests/testfiles/make.conf',
        ...           'nocheck'    : True,
        ...           'storage'   : '/var/lib/layman',
        ...           'quietness':3}
        >>> c = DB(config)
        >>> a = ConfigHandler(config, c.overlays)
        >>> a.path = write
        >>> a.add(c.select('wrobel'))
        >>> config['make_conf'] = write
        >>> b = ConfigHandler(config, c.overlays)
        >>> [i.name for i in b.overlays]
        ['wrobel', 'wrobel-stable']
        >>> b.extra
        ['/usr/local/portage/ebuilds/testing', '/usr/local/portage/ebuilds/stable', '/usr/local/portage/kolab2', '/usr/local/portage/gentoo-webapps-overlay/experimental', '/usr/local/portage/gentoo-webapps-overlay/production-ready']

        >>> os.unlink(write)
        >>> import shutil
        >>> shutil.rmtree(tmpdir)
        '''
        self.overlays.append(overlay)
        return self.write()

    def delete(self, overlay):
        '''
        Delete an overlay from make.conf.

        >>> import tempfile
        >>> tmpdir = tempfile.mkdtemp(prefix="laymantmp_")
        >>> write = os.path.join(tmpdir, 'make.conf')
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'installed' :
        ...           here + '/tests/testfiles/global-overlays.xml',
        ...           'make_conf' : here + '/tests/testfiles/make.conf',
        ...           'nocheck'    : True,
        ...           'storage'   : '/var/lib/layman',
        ...           'quietness':3}
        >>> c = DB(config)
        >>> a = ConfigHandler(config, c.overlays)
        >>> a.path = write
        >>> a.delete(c.select('wrobel-stable'))
        >>> config['make_conf'] = write
        >>> b = ConfigHandler(config, c.overlays)
        >>> [i.name for i in b.overlays]
        []
        >>> b.extra
        ['/usr/local/portage/ebuilds/testing', '/usr/local/portage/ebuilds/stable', '/usr/local/portage/kolab2', '/usr/local/portage/gentoo-webapps-overlay/experimental', '/usr/local/portage/gentoo-webapps-overlay/production-ready']

        >>> os.unlink(write)
        >>> import shutil
        >>> shutil.rmtree(tmpdir)
        '''
        self.overlays = [i
                         for i in self.overlays
                         if i.name != overlay.name]
        return self.write()

    def update(self, overlay):
        '''
        Stub function necessary for RepoConfManager class.
        '''
        pass

    def read(self, raise_error=False):
        '''
        Read the list of registered overlays from /var/layman/make.conf.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'installed' :
        ...           here + '/tests/testfiles/global-overlays.xml',
        ...           'make_conf' : here + '/tests/testfiles/make.conf',
        ...           'nocheck'    : True,
        ...           'storage'   : '/var/lib/layman',
        ...           'quietness':3}
        >>> c = DB(config)
        >>> a = ConfigHandler(config, c.overlays)
        >>> [i.name for i in a.overlays]
        ['wrobel-stable']
        >>> a.extra
        ['/usr/local/portage/ebuilds/testing', '/usr/local/portage/ebuilds/stable', '/usr/local/portage/kolab2', '/usr/local/portage/gentoo-webapps-overlay/experimental', '/usr/local/portage/gentoo-webapps-overlay/production-ready']
        '''
        if os.path.isfile(self.path):
            self.content()

            overlays = self.my_re.search(self.data)

            if not overlays:
                msg = 'MakeConf: ConfigHandler.read(); Did not find a '\
                    'PORTDIR_OVERLAY entry in file '\
                    '%(path)s! Did you specify the correct file?' % ({'path': self.path})
                if raise_error:
                    raise Exception(msg)
                self.output.error(msg)
                return False

            overlays = [i.strip()
                        for i in overlays.group(1).split('\n')
                        if i.strip()]

            for i in overlays:
                if i[:len(self.storage)] == self.storage:
                    oname = os.path.basename(i)
                    if  oname in self.db.keys():
                        self.overlays.append(self.db[oname])
                    else:
                        # These are additional overlays that we dont know
                        # anything about. The user probably added them manually
                        self.extra.append(i)
                else:
                    # These are additional overlays that we dont know anything
                    # about. The user probably added them manually
                    self.extra.append(i)

        else:
            self.overlays = []
            self.data     = 'PORTDIR_OVERLAY="\n"\n'

        self.extra = [i for i in self.extra
                         if (i != '$PORTDIR_OVERLAY'
                             and i != '${PORTDIR_OVERLAY}')]
        return True

    def write(self):
        '''
        Write the list of registered overlays to /var/layman/make.conf.

        >>> import tempfile
        >>> tmpdir = tempfile.mkdtemp(prefix="laymantmp_")
        >>> os.path.join(tmpdir, 'make.conf')
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'installed' :
        ...           here + '/tests/testfiles/global-overlays.xml',
        ...           'make_conf' : here + '/tests/testfiles/make.conf',
        ...           'nocheck'    : True,
        ...           'storage'   : '/var/lib/layman',
        ...           'quietness':3}
        >>> c = DB(config)
        >>> a = ConfigHandler(config, c.overlays)
        >>> a.path = write
        >>> a.write()
        >>> config['make_conf'] = write
        >>> b = ConfigHandler(config, c.overlays)
        >>> [i.name for i in b.overlays]
        ['wrobel-stable']
        >>> b.extra
        ['/usr/local/portage/ebuilds/testing', '/usr/local/portage/ebuilds/stable', '/usr/local/portage/kolab2', '/usr/local/portage/gentoo-webapps-overlay/experimental', '/usr/local/portage/gentoo-webapps-overlay/production-ready']

        >>> os.unlink(write)
        >>> import shutil
        >>> shutil.rmtree(tmpdir)
        '''
        def prio_sort(a, b):
            '''Sort by priority.'''
            if a.priority < b.priority:
                return -1
            elif a.priority > b.priority:
                return 1
            return 0

        self.overlays.sort(key=cmp_to_key(prio_sort))

        paths = []
        for i in self.overlays:
            paths.append(path((self.storage, i.name, )))

        overlays = 'PORTDIR_OVERLAY="\n'
        overlays += '\n'.join(paths) + '\n'
        overlays += '$PORTDIR_OVERLAY\n'
        overlays += '\n'.join(self.extra)
        overlays += '"'

        content = self.my_re.sub(overlays, self.data)

        if not self.my_re.search(content):
            self.output.error('MakeConf: ConfigHandler.write(); Oops, failed to set a '\
                'proper PORTDIR_OVERLAY entry in file '\
                '%(path)s! Did not overwrite the file.' % ({'path': self.path}))
            return False

        try:
             with fileopen(self.path, 'w') as make_conf:
                make_conf.write(content)

        except Exception as error:
            self.output.error('MakeConf: ConfigHandler.write(); Failed to write "'\
                '%(path)s".\nError was:\n%(error)s' % ({'path': self.path, 'error': str(error)}))
            return False
        return True

    def content(self):
        '''
        Returns the content of the /var/lib/layman/make.conf file.
        '''
        try:
            with fileopen(self.path, 'r') as make_conf:
                self.data = make_conf.read()

        except Exception as error:
            self.output.error('ConfigHandler: content(); Failed to read "'\
                '%(path)s".\nError was:\n%(error)s' % ({'path': self.path, 'error': str(error)}))
            raise error
