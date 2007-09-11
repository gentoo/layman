#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN OVERLAY DB
#################################################################################
# File:       db.py
#
#             Access to the db of overlays
#
# Copyright:
#             (c) 2005 - 2006 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#
'''Handles different storage files.'''

__version__ = "$Id: db.py 309 2007-04-09 16:23:38Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os, os.path, urllib2, re, md5

from   layman.utils             import path
from   layman.overlay           import Overlays

from   layman.debug             import OUT

#===============================================================================
#
# Class DB
#
#-------------------------------------------------------------------------------

class DB(Overlays):
    ''' Handle the list of local overlays.'''

    def __init__(self, config):

        self.config = config

        self.path = config['local_list']

        if config['nocheck']:
            ignore = 2
        else:
            ignore = 1

        quiet = int(config['quietness']) < 3

        Overlays.__init__(self, 
                          [config['local_list'], ], 
                          ignore, 
                          quiet)

        OUT.debug('DB handler initiated', 6)

    def add(self, overlay):
        '''
        Add an overlay to the local list of overlays.

        >>> write = os.tmpnam()
        >>> write2 = os.tmpnam()
        >>> write3 = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'local_list' :
        ...           here + '/tests/testfiles/global-overlays.xml',
        ...           'make_conf' : write2,
        ...           'nocheck'    : True,
        ...           'storage'   : write3,
        ...           'quietness':3}

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> a = DB(config)
        >>> config['local_list'] = write
        >>> b = DB(config)
        >>> OUT.color_off()

        >>> m = MakeConf(config, b.overlays)
        >>> m.path = write2
        >>> m.write()

        Commented out since it needs network access:

        # >>> b.add(a.select('wrobel-stable')) #doctest: +ELLIPSIS
        # * Running command "/usr/bin/rsync -rlptDvz --progress --delete --delete-after --timeout=180 --exclude="distfiles/*" --exclude="local/*" --exclude="packages/*" "rsync://gunnarwrobel.de/wrobel-stable/*" "/tmp/file.../wrobel-stable""...
        # >>> c = Overlays([write, ])
        # >>> c.overlays.keys()
        # [u'wrobel-stable']

        # >>> m = MakeConf(config, b.overlays)
        # >>> [i.name for i in m.overlays] #doctest: +ELLIPSIS
        # [u'wrobel-stable']


        # >>> os.unlink(write)
        >>> os.unlink(write2)
        >>> import shutil

        # >>> shutil.rmtree(write3)
        '''

        if overlay.name not in self.overlays.keys():
            result = overlay.add(self.config['storage'])
            if result == 0:
                if 'priority' in self.config.keys():
                    overlay.priority = int(self.config['priority'])
                self.overlays[overlay.name] = overlay
                self.write(self.path)
                make_conf = MakeConf(self.config, self.overlays)
                make_conf.add(overlay)
            else:
                overlay.delete(self.config['storage'])
                raise Exception('Adding the overlay failed!')
        else:
            raise Exception('Overlay "' + overlay.name + '" already in the loca'
                            'l list!')

    def delete(self, overlay):
        '''
        Add an overlay to the local list of overlays.

        >>> write = os.tmpnam()
        >>> write2 = os.tmpnam()
        >>> write3 = os.tmpnam()
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> config = {'local_list' :
        ...           here + '/tests/testfiles/global-overlays.xml',
        ...           'make_conf' : write2,
        ...           'nocheck'    : True,
        ...           'storage'   : write3,
        ...           'quietness':3}

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> a = DB(config)
        >>> config['local_list'] = write
        >>> b = DB(config)
        >>> OUT.color_off()

        >>> m = MakeConf(config, b.overlays)
        >>> m.path = here + '/tests/testfiles/make.conf'
        >>> m.read()

        >>> m.path = write2
        >>> m.write()

        # >>> b.add(a.select('wrobel-stable')) #doctest: +ELLIPSIS
        # * Running command "/usr/bin/rsync -rlptDvz --progress --delete --delete-after --timeout=180 --exclude="distfiles/*" --exclude="local/*" --exclude="packages/*" "rsync://gunnarwrobel.de/wrobel-stable/*" "/tmp/file.../wrobel-stable""...
        # >>> b.add(a.select('wrobel')) #doctest: +ELLIPSIS
        # * Running command "/usr/bin/svn co "https://overlays.gentoo.org/svn/dev/wrobel/" "/tmp/file.../wrobel""...
        # >>> c = Overlays([write, ])
        # >>> c.overlays.keys()
        # [u'wrobel', u'wrobel-stable']

        # >>> b.delete(b.select('wrobel'))
        # >>> c = Overlays([write, ])
        # >>> c.overlays.keys()
        # [u'wrobel-stable']

        # >>> m = MakeConf(config, b.overlays)
        # >>> [i.name for i in m.overlays] #doctest: +ELLIPSIS
        # [u'wrobel-stable']

        # >>> os.unlink(write)
        >>> os.unlink(write2)
        >>> import shutil

        # >>> shutil.rmtree(write3)
        '''

        if overlay.name in self.overlays.keys():
            make_conf = MakeConf(self.config, self.overlays)
            overlay.delete(self.config['storage'])
            del self.overlays[overlay.name]
            self.write(self.path)
            make_conf.delete(overlay)
        else:
            raise Exception('No local overlay named "' + overlay.name + '"!')

    def sync(self, overlay_name):
        '''Synchronize the given overlay.'''

        overlay = self.select(overlay_name)

        if overlay:
            result = overlay.sync(self.config['storage'])
            if result:
                raise Exception('Syncing overlay "' + overlay_name + 
                                '" returned status ' + str(result) + '!')
        else:
            raise Exception('No such overlay ("' + overlay_name + '")!')

#===============================================================================
#
# Class RemoteDB
#
#-------------------------------------------------------------------------------

class RemoteDB(Overlays):
    '''Handles fetching the remote overlay list.'''

    def __init__(self, config):

        self.config = config

        self.proxies = {}

        if config['proxy']:
            self.proxies['http'] = config['proxy']
        elif os.getenv('http_proxy'):
            self.proxies['http'] = os.getenv('http_proxy')

        if self.proxies:
	    proxy_handler = urllib2.ProxyHandler(self.proxies)
	    opener = urllib2.build_opener(proxy_handler)
	    urllib2.install_opener(opener)

        self.urls  = [i.strip() for i in config['overlays'].split('\n') if i]

        paths = [self.path(i) for i in self.urls]

        if config['nocheck']:
            ignore = 2
        else:
            ignore = 0

        quiet = int(config['quietness']) < 3

        Overlays.__init__(self, paths, ignore, quiet)

    def cache(self):
        '''
        Copy the remote overlay list to the local cache.

        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> cache = os.tmpnam()
        >>> config = {'overlays' :
        ...           'file://' + here + '/tests/testfiles/global-overlays.xml',
        ...           'cache' : cache,
        ...           'nocheck'    : True,
        ...           'proxy' : None,
        ...           'quietness':3}
        >>> a = RemoteDB(config)
        >>> a.cache()
        >>> b = open(a.path(config['overlays']))
        >>> b.readlines()[24]
        '      A collection of ebuilds from Gunnar Wrobel [wrobel@gentoo.org].\\n'

        >>> b.close()
        >>> os.unlink(a.path(config['overlays']))

        >>> a.overlays.keys()
        [u'wrobel', u'wrobel-stable']
        '''
        for url in self.urls:

            mpath = self.path(url)

            try:

                # Fetch the remote list
                olist = urllib2.urlopen(url).read()

                # Create our storage directory if it is missing
                if not os.path.exists(os.path.dirname(mpath)):
                    try:
                        os.makedirs(os.path.dirname(mpath))
                    except OSError, error:
                        raise OSError('Failed to create layman storage direct'
                                      + 'ory ' + os.path.dirname(mpath) + '\n'
                                      + 'Error was:' + str(error))

                # Before we overwrite the old cache, check that the downloaded
                # file is intact and can be parsed
                try:
                    self.read(olist)
                except Exception, error:
                    raise IOError('Failed to parse the overlays list fetched fr'
                                  'om ' + url + '\nThis means that the download'
                                  'ed file is somehow corrupt or there was a pr'
                                  'oblem with the webserver. Check the content '
                                  'of the file. Error was:\n' + str(error))

                # Ok, now we can overwrite the old cache
                try:
                    out_file = open(mpath, 'w')
                    out_file.write(olist)
                    out_file.close()

                except Exception, error:
                    raise IOError('Failed to temporarily cache overlays list in'
                                  ' ' + mpath + '\nError was:\n' + str(error))


            except IOError, error:
                OUT.warn('Failed to update the overlay list from: '
                         + url + '\nError was:\n' + str(error))

            try:
                # Finally parse the contents of the cache
                self.read_file(mpath)
            except IOError, error:
                OUT.warn('Failed to read a cached version of the overlay list f'
                         'rom ' + url + '. You probably did not download the fi'
                         'le before. The corresponding entry in your layman.cfg'
                         ' file will be disregarded.\nError was:\n' + str(error)
                         )

    def path(self, url):
        '''Return a unique file name for the url.'''

        base = self.config['cache']

        OUT.debug('Generating cache path.', 6)

        return base + '_' + md5.md5(url).hexdigest() + '.xml'

#===============================================================================
#
# Helper class MakeConf
#
#-------------------------------------------------------------------------------

class MakeConf:
    '''
    Handles modifications to /etc/make.conf

    Check that an add/remove cycle does not modify the make.conf:

    >>> import md5
    >>> write = os.tmpnam()
    >>> here = os.path.dirname(os.path.realpath(__file__))
    >>> config = {'local_list' :
    ...           here + '/tests/testfiles/global-overlays.xml',
    ...           'make_conf' : here + '/tests/testfiles/make.conf',
    ...           'nocheck'    : True,
    ...           'storage'   : '/usr/portage/local/layman',
    ...           'quietness':3}
    >>> b = DB(config)
    >>> a = MakeConf(config, b.overlays)
    >>> o_md5 = str(md5.md5(open(here + '/tests/testfiles/make.conf').read()).hexdigest())
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
    >>> n_md5 = str(md5.md5(open(write).read()).hexdigest())
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
        ...           'storage'   : '/usr/portage/local/layman',
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
        ['/usr/portage/local/ebuilds/testing', '/usr/portage/local/ebuilds/stable', '/usr/portage/local/kolab2', '/usr/portage/local/gentoo-webapps-overlay/experimental', '/usr/portage/local/gentoo-webapps-overlay/production-ready']

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
        ...           'storage'   : '/usr/portage/local/layman',
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
        ['/usr/portage/local/ebuilds/testing', '/usr/portage/local/ebuilds/stable', '/usr/portage/local/kolab2', '/usr/portage/local/gentoo-webapps-overlay/experimental', '/usr/portage/local/gentoo-webapps-overlay/production-ready']

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
        ...           'storage'   : '/usr/portage/local/layman',
        ...           'quietness':3}
        >>> c = DB(config)
        >>> a = MakeConf(config, c.overlays)
        >>> [i.name for i in a.overlays]
        [u'wrobel-stable']
        >>> a.extra
        ['/usr/portage/local/ebuilds/testing', '/usr/portage/local/ebuilds/stable', '/usr/portage/local/kolab2', '/usr/portage/local/gentoo-webapps-overlay/experimental', '/usr/portage/local/gentoo-webapps-overlay/production-ready']
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
        ...           'storage'   : '/usr/portage/local/layman',
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
        ['/usr/portage/local/ebuilds/testing', '/usr/portage/local/ebuilds/stable', '/usr/portage/local/kolab2', '/usr/portage/local/gentoo-webapps-overlay/experimental', '/usr/portage/local/gentoo-webapps-overlay/production-ready']

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
            make_conf = open(self.path, 'w')

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
            make_conf = open(self.path)

            self.data = make_conf.read()

            make_conf.close()

        except Exception, error:
            raise Exception('Failed to read "' + self.path + '".\nError was:\n'
                            + str(error))

#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest, sys

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
