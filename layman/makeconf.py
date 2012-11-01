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

import os
import codecs
import re

from layman.utils import path

#===============================================================================
#
# Helper class MakeConf
#
#-------------------------------------------------------------------------------

class MakeConf:
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
    >>> a = MakeConf(config, b.overlays)
    >>> o_md5 = str(hashlib.md5(open(here + '/tests/testfiles/make.conf').read()).hexdigest())
    >>> a.path = write
    >>> a.add(b.overlays['wrobel-stable'])
    >>> [i.name for i in a.overlays]
    [u'wrobel-stable', u'wrobel-stable']
    >>> a.add(b.overlays['wrobel'])
    >>> [i.name for i in a.overlays]
    [u'wrobel', u'wrobel-stable', u'wrobel-stable']
    >>> a.delete(b.overlays['wrobel-stable'])
    >>> [i.name for i in a.overlays]
    [u'wrobel']
    >>> a.add(b.overlays['wrobel-stable'])
    >>> [i.name for i in a.overlays]
    [u'wrobel', u'wrobel-stable']
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
        >>> a = MakeConf(config, c.overlays)
        >>> a.path = write
        >>> a.add(c.select('wrobel'))
        >>> config['make_conf'] = write
        >>> b = MakeConf(config, c.overlays)
        >>> [i.name for i in b.overlays]
        [u'wrobel', u'wrobel-stable']
        >>> b.extra
        [u'/usr/local/portage/ebuilds/testing', u'/usr/local/portage/ebuilds/stable', u'/usr/local/portage/kolab2', u'/usr/local/portage/gentoo-webapps-overlay/experimental', u'/usr/local/portage/gentoo-webapps-overlay/production-ready']

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
        >>> a = MakeConf(config, c.overlays)
        >>> a.path = write
        >>> a.delete(c.select('wrobel-stable'))
        >>> config['make_conf'] = write
        >>> b = MakeConf(config, c.overlays)
        >>> [i.name for i in b.overlays]
        []
        >>> b.extra
        [u'/usr/local/portage/ebuilds/testing', u'/usr/local/portage/ebuilds/stable', u'/usr/local/portage/kolab2', u'/usr/local/portage/gentoo-webapps-overlay/experimental', u'/usr/local/portage/gentoo-webapps-overlay/production-ready']

        >>> os.unlink(write)
        >>> import shutil
        >>> shutil.rmtree(tmpdir)
        '''
        self.overlays = [i
                         for i in self.overlays
                         if i.name != overlay.name]
        return self.write()

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
        >>> a = MakeConf(config, c.overlays)
        >>> [i.name for i in a.overlays]
        [u'wrobel-stable']
        >>> a.extra
        [u'/usr/local/portage/ebuilds/testing', u'/usr/local/portage/ebuilds/stable', u'/usr/local/portage/kolab2', u'/usr/local/portage/gentoo-webapps-overlay/experimental', u'/usr/local/portage/gentoo-webapps-overlay/production-ready']
        '''
        if os.path.isfile(self.path):
            self.content()

            overlays = self.my_re.search(self.data)

            if not overlays:
                msg = 'MakeConf: read(); Did not find a ' + \
                    'PORTDIR_OVERLAY entry in file ' + \
                    self.path +'! Did you specify the correct file?'
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
        >>> a = MakeConf(config, c.overlays)
        >>> a.path = write
        >>> a.write()
        >>> config['make_conf'] = write
        >>> b = MakeConf(config, c.overlays)
        >>> [i.name for i in b.overlays]
        [u'wrobel-stable']
        >>> b.extra
        [u'/usr/local/portage/ebuilds/testing', u'/usr/local/portage/ebuilds/stable', u'/usr/local/portage/kolab2', u'/usr/local/portage/gentoo-webapps-overlay/experimental', u'/usr/local/portage/gentoo-webapps-overlay/production-ready']

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

        self.overlays.sort(prio_sort)

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
            self.output.error('MakeConf: write(); Oops, failed to set a '
                'proper PORTDIR_OVERLAY entry in file '
                 + self.path +'! Did not overwrite the file.')
            return False

        try:
            make_conf = codecs.open(self.path, 'w', 'utf-8')

            make_conf.write(content)

            make_conf.close()

        except Exception, error:
            self.output.error('MakeConf: write(); Failed to write "'
                + self.path + '".\nError was:\n' + str(error))
            return False
        return True

    def content(self):
        '''
        Returns the content of the /var/lib/layman/make.conf file.
        '''
        try:
            make_conf = codecs.open(self.path, 'r', 'utf-8')

            self.data = make_conf.read()

            make_conf.close()

        except Exception, error:
            self.output.error('MakeConf: content(); Failed to read "' +
                self.path + '".\nError was:\n' + str(error))
            raise error
