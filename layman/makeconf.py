#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# MAKE-DOT-CONF HANDLING
#################################################################################
# File:       makeconf.py
#
#             Handles modifications to /etc/make.conf
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
    Handles modifications to /etc/make.conf

    Check that an add/remove cycle does not modify the make.conf:

    >>> import hashlib
    >>> write = os.tmpnam()
    >>> here = os.path.dirname(os.path.realpath(__file__))
    >>> config = {'local_list' :
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
    '''

    my_re = re.compile('PORTDIR_OVERLAY\s*=\s*"([^"]*)"')

    def __init__(self, config, overlays):

        self.path = config['make_conf']
        self.storage = config['storage']
        self.data = ''
        self.db = overlays
        self.overlays = []
        self.extra = []

        self.read()

    def add(self, overlay):
        '''
        Add an overlay to make.conf.

        >>> write = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'local_list' :
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
        '''
        self.overlays.append(overlay)
        self.write()

    def delete(self, overlay):
        '''
        Delete an overlay from make.conf.

        >>> write = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'local_list' :
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
        '''
        self.overlays = [i
                         for i in self.overlays
                         if i.name != overlay.name]
        self.write()

    def read(self):
        '''
        Read the list of registered overlays from /etc/make.conf.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'local_list' :
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
                raise Exception('Did not find a PORTDIR_OVERLAY entry in file ' +
                                self.path +'! Did you specify the correct file?')

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

    def write(self):
        '''
        Write the list of registered overlays to /etc/make.conf.

        >>> write = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'local_list' :
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
            raise Exception('Ups, failed to set a proper PORTDIR_OVERLAY entry '
                            'in file ' + self.path +'! Did not overwrite the fi'
                            'le.')

        try:
            make_conf = codecs.open(self.path, 'w', 'utf-8')

            make_conf.write(content)

            make_conf.close()

        except Exception, error:
            raise Exception('Failed to read "' + self.path + '".\nError was:\n'
                            + str(error))

    def content(self):
        '''
        Returns the content of the /etc/make.conf file.
        '''
        try:
            make_conf = codecs.open(self.path, 'r', 'utf-8')

            self.data = make_conf.read()

            make_conf.close()

        except Exception, error:
            raise Exception('Failed to read "' + self.path + '".\nError was:\n'
                            + str(error))
