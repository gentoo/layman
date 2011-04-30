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
#             (c) 2005 - 2008 Gunnar Wrobel
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

import os, os.path, urllib2, hashlib

from   layman.utils             import path, delete_empty_directory
from   layman.dbbase            import DbBase
from   layman.makeconf          import MakeConf

#from   layman.debug             import OUT

#===============================================================================
#
# Class DB
#
#-------------------------------------------------------------------------------

class DB(DbBase):
    ''' Handle the list of local overlays.'''

    def __init__(self, config):

        self.config = config
        self.output = config['output']

        self.path = config['local_list']

        if config['nocheck']:
            ignore = 2
        else:
            ignore = 1

        quiet = int(config['quietness']) < 3

        DbBase.__init__(self,
                          config,
                          paths=[config['local_list'], ],
                          ignore=ignore,
                          quiet=quiet)

        self.output.debug('DB handler initiated', 6)

    # overrider
    def _broken_catalog_hint(self):
        return ''

    def add(self, overlay, quiet = False):
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
        # >>> c = DbBase([write, ], dict())
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
            result = overlay.add(self.config['storage'], quiet)
            if result == 0:
                if 'priority' in self.config.keys():
                    overlay.set_priority(self.config['priority'])
                self.overlays[overlay.name] = overlay
                self.write(self.path)
                if self.config['make_config']:
                    make_conf = MakeConf(self.config, self.overlays)
                    make_ok = make_conf.add(overlay)
                    return make_ok
                return True
            else:
                mdir = path([self.config['storage'], overlay.name])
                delete_empty_directory(mdir, self.output)
                if os.path.exists(mdir):
                    self.output.error('Adding repository "%s" failed!'
                                ' Possible remains of the operation have NOT'
                                ' been removed and may be left at "%s".'
                                ' Please remove them manually if required.' \
                                % (overlay.name, mdir))
                    return False
                else:
                    self.output.error(
                        'Adding repository "%s" failed!' % overlay.name)
                    return False
        else:
            self.output.error('Repository "' + overlay.name +
                '" already in the local (installed) list!')
            return False


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
        >>> .color_off()

        >>> m = MakeConf(config, b.overlays)
        >>> m.path = here + '/tests/testfiles/make.conf'
        >>> m.read()

        >>> m.path = write2
        >>> m.write()

        # >>> b.add(a.select('wrobel-stable')) #doctest: +ELLIPSIS
        # * Running command "/usr/bin/rsync -rlptDvz --progress --delete --delete-after --timeout=180 --exclude="distfiles/*" --exclude="local/*" --exclude="packages/*" "rsync://gunnarwrobel.de/wrobel-stable/*" "/tmp/file.../wrobel-stable""...
        # >>> b.add(a.select('wrobel')) #doctest: +ELLIPSIS
        # * Running command "/usr/bin/svn co "https://overlays.gentoo.org/svn/dev/wrobel/" "/tmp/file.../wrobel""...
        # >>> c = DbBase([write, ], dict())
        # >>> c.overlays.keys()
        # [u'wrobel', u'wrobel-stable']

        # >>> b.delete(b.select('wrobel'))
        # >>> c = DbBase([write, ], dict())
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

    def sync(self, overlay_name, quiet = False):
        '''Synchronize the given overlay.'''

        overlay = self.select(overlay_name)
        result = overlay.sync(self.config['storage'], quiet)
        if result:
            raise Exception('Syncing overlay "' + overlay_name +
                            '" returned status ' + str(result) + '!' +
                            '\ndb.sync()')

#===============================================================================
#
# Class RemoteDB
#
#-------------------------------------------------------------------------------

class RemoteDB(DbBase):
    '''Handles fetching the remote overlay list.'''

    def __init__(self, config, ignore_init_read_errors=False):

        self.config = config
        self.output = config['output']

        self.proxies = {}

        if config['proxy']:
            self.proxies['http'] = config['proxy']
        elif os.getenv('http_proxy'):
            self.proxies['http'] = os.getenv('http_proxy')

        if self.proxies:
            proxy_handler = urllib2.ProxyHandler(self.proxies)
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        self.urls  = [i.strip() for i in config['overlays'].split('\n') if len(i)]

        paths = [self.path(i) for i in self.urls]

        if config['nocheck']:
            ignore = 2
        else:
            ignore = 0

        quiet = int(config['quietness']) < 3

        DbBase.__init__(self, config, paths=paths, ignore=ignore,
            quiet=quiet, ignore_init_read_errors=ignore_init_read_errors)

    # overrider
    def _broken_catalog_hint(self):
        return 'Try running "sudo layman -f" to re-fetch that file'

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

            # Check for sufficient privileges
            if os.path.exists(mpath) and not os.access(mpath, os.W_OK):
                self.output.warn('You do not have permission to update the cache (%s).' % mpath)
                import getpass
                if getpass.getuser() != 'root':
                    self.output.warn('Hint: You are not root.\n')
                continue

            try:

                # Fetch the remote list
                olist = urllib2.urlopen(url).read()

                # Create our storage directory if it is missing
                if not os.path.exists(os.path.dirname(mpath)):
                    try:
                        os.makedirs(os.path.dirname(mpath))
                    except OSError as error:
                        raise OSError('Failed to create layman storage direct'
                                      + 'ory ' + os.path.dirname(mpath) + '\n'
                                      + 'Error was:' + str(error))

                # Before we overwrite the old cache, check that the downloaded
                # file is intact and can be parsed
                try:
                    self.read(olist, origin=url)
                except Exception as error:
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

                except Exception as error:
                    raise IOError('Failed to temporarily cache overlays list in'
                                  ' ' + mpath + '\nError was:\n' + str(error))


            except IOError as error:
                self.output.warn('Failed to update the overlay list from: '
                         + url + '\nError was:\n' + str(error))

    def path(self, url):
        '''Return a unique file name for the url.'''

        base = self.config['cache']

        self.output.debug('Generating cache path.', 6)

        return base + '_' + hashlib.md5(url).hexdigest() + '.xml'


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
