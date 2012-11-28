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

from __future__ import with_statement

__version__ = "$Id: db.py 309 2007-04-09 16:23:38Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os, os.path
import sys
import urllib2
import hashlib


GPG_ENABLED = False
try:
    from pygpg.config import GPGConfig
    from pygpg.gpg import GPG
    GPG_ENABLED = True
except ImportError:
    pass


from   layman.utils             import encoder
from   layman.dbbase            import DbBase
from   layman.version           import VERSION
from layman.compatibility       import fileopen


class RemoteDB(DbBase):
    '''Handles fetching the remote overlay list.'''

    def __init__(self, config, ignore_init_read_errors=False):

        self.config = config
        self.output = config['output']
        self.detached_urls = []
        self.signed_urls = []

        self.proxies = {}

        if config['proxy']:
            self.proxies['http'] = config['proxy']
        elif os.getenv('http_proxy'):
            self.proxies['http'] = os.getenv('http_proxy')

        if self.proxies:
            proxy_handler = urllib2.ProxyHandler(self.proxies)
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        self.urls  = [i.strip()
            for i in config['overlays'].split('\n') if len(i)]

        if GPG_ENABLED:
            self.get_gpg_urls()
        else:
            self.output.debug('RemoteDB.__init__(), NOT GPG_ENABLED, bypassing...', 2)

        # add up the lists to load for display, etc.
        # unsigned overlay lists
        paths = [self.filepath(i) + '.xml' for i in self.urls]
        # detach-signed lists
        paths.extend([self.filepath(i[0]) + '.xml' for i in self.detached_urls])
        # single file signed, compressed, clearsigned
        paths.extend([self.filepath(i) + '.xml' for i in self.signed_urls])

        self.output.debug('RemoteDB.__init__(), url lists= \nself.urls: %s\nself.detached_urls: %s\nself.signed_urls: %s' % (str(self.urls), str(self.detached_urls), str(self.signed_urls)), 2)

        self.output.debug('RemoteDB.__init__(), paths to load = %s' %str(paths), 2)

        if config['nocheck']:
            ignore = 2
        else:
            ignore = 0

        #quiet = int(config['quietness']) < 3

        DbBase.__init__(self, config, paths=paths, ignore=ignore,
            ignore_init_read_errors=ignore_init_read_errors)

        self.gpg = None
        self.gpg_config = None


    # overrider
    def _broken_catalog_hint(self):
        return 'Try running "sudo layman -f" to re-fetch that file'


    def cache(self):
        '''
        Copy the remote overlay list to the local cache.

        >>> import tempfile
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> tmpdir = tempfile.mkdtemp(prefix="laymantmp_")
        >>> cache = os.path.join(tmpdir, 'cache')
        >>> myoptions = {'overlays' :
        ...           ['file://' + here + '/tests/testfiles/global-overlays.xml'],
        ...           'cache' : cache,
        ...           'nocheck'    : 'yes',
        ...           'proxy' : None}
        >>> from layman.config import OptionConfig
        >>> config = OptionConfig(myoptions)
        >>> config.set_option('quietness', 3)
        >>> a = RemoteDB(config)
        >>> a.cache()
        (True, True)
        >>> b = fileopen(a.filepath(config['overlays'])+'.xml')
        >>> b.readlines()[24]
        '      A collection of ebuilds from Gunnar Wrobel [wrobel@gentoo.org].\\n'

        >>> b.close()
        >>> os.unlink(a.filepath(config['overlays'])+'.xml')

        >>> a.overlays.keys()
        [u'wrobel', u'wrobel-stable']

        >>> import shutil
        >>> shutil.rmtree(tmpdir)
        '''
        has_updates = False
        self._create_storage(self.config['storage'])
        # succeeded reset when a failure is detected
        succeeded = True
        url_lists = [self.urls, self.detached_urls, self.signed_urls]
        need_gpg = [False, True, True]
        for index in range(0, 3):
            self.output.debug("RemoteDB.cache() index = %s" %str(index),2)
            urls = url_lists[index]
            if need_gpg[index] and len(urls) and self.gpg is None:
                #initialize our gpg instance
                self.init_gpg()
            # main working loop
            for url in urls:
                sig = ''
                self.output.debug("RemoteDB.cache() url = %s is a tuple=%s"
                    %(str(url), str(isinstance(url, tuple))),2)
                filepath, mpath, tpath, sig = self._paths(url)

                if sig:
                    success, olist, timestamp = self._fetch_url(
                        url[0], mpath, tpath)
                else:
                    success, olist, timestamp = self._fetch_url(
                        url, mpath, tpath)
                if not success:
                    #succeeded = False
                    continue

                self.output.debug("RemoteDB.cache() len(olist) = %s" %str(len(olist)),2)
                # GPG handling
                if need_gpg[index]:
                    olist, verified = self.verify_gpg(url, sig, olist)
                    if not verified:
                        self.output.debug("RemoteDB.cache() gpg returned "
                            "verified = %s" %str(verified),2)
                        succeeded = False
                        filename = os.path.join(self.config['storage'], "Failed-to-verify-sig")
                        self.write_cache(olist, filename)
                        continue

                # Before we overwrite the old cache, check that the downloaded
                # file is intact and can be parsed
                if isinstance(url, tuple):
                    olist = self._check_download(olist, url[0])
                else:
                    olist = self._check_download(olist, url)

                # Ok, now we can overwrite the old cache
                has_updates = max(has_updates,
                    self.write_cache(olist, mpath, tpath, timestamp))

            self.output.debug("RemoteDB.cache() self.urls:  has_updates, succeeded"
                " %s, %s" % (str(has_updates), str(succeeded)), 4)
        return has_updates, succeeded


    def _paths(self, url):
        self.output.debug("RemoteDB._paths(), url is tuple %s" % str(url),2)
        if isinstance(url, tuple):
            filepath = self.filepath(url[0])
            sig = filepath + '.sig'
        else:
            filepath = self.filepath(url)
            sig = ''
        mpath = filepath + '.xml'
        tpath = filepath + '.timestamp'
        return filepath, mpath, tpath, sig


    @staticmethod
    def _create_storage(mpath):
            # Create our storage directory if it is missing
            if not os.path.exists(os.path.dirname(mpath)):
                try:
                    os.makedirs(os.path.dirname(mpath))
                except OSError, error:
                    raise OSError('Failed to create layman storage direct'
                                  + 'ory ' + os.path.dirname(mpath) + '\n'
                                  + 'Error was:' + str(error))
            return


    def filepath(self, url):
        '''Return a unique file name for the url.'''

        base = self.config['cache']

        self.output.debug('Generating cache path.', 6)
        url_encoded = encoder(url, "UTF-8")

        return base + '_' + hashlib.md5(url_encoded).hexdigest()


    def _fetch_url(self, url, mpath, tpath=None):
        self.output.debug('RemoteDB._fetch_url() url = %s' % url, 2)
        # check when the cache was last updated
        # and don't re-fetch it unless it has changed
        request = urllib2.Request(url)
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept-Charset', 'utf-8'),
            ('User-Agent', 'Layman-' + VERSION)]
        #opener.addheaders[('User-Agent', 'Layman-' + VERSION)]

        if tpath and os.path.exists(tpath):
            with fileopen(tpath,'r') as previous:
                timestamp = previous.read()
            request.add_header('If-Modified-Since', timestamp)

        if not self.check_path([mpath]):
            return (False, '', '')

        try:
            self.output.debug('RemoteDB._fetch_url() connecting to opener', 2)
            connection = opener.open(request)
            # py2, py3 compatibility, since only py2 returns keys as lower()
            headers = dict((x.lower(), x) for x in connection.headers.keys())
            if 'last-modified' in headers:
                timestamp = connection.headers[headers['last-modified']]
            elif 'date' in headers:
                timestamp = connection.headers[headers['date']]
            else:
                timestamp = None
        except urllib2.HTTPError, e:
            if e.code == 304:
                self.output.info('Remote list already up to date: %s'
                    % url, 4)
                self.output.info('Last-modified: %s' % timestamp, 4)
            else:
                self.output.error('RemoteDB.cache(); HTTPError was:\n'
                    'url: %s\n%s'
                    % (url, str(e)))
                return (False, '', '')
            return (False, '', '')
        except IOError, error:
            self.output.error('RemoteDB.cache(); Failed to update the '
                'overlay list from: %s\nIOError was:%s\n'
                % (url, str(error)))
            return (False, '', '')
        else:
            if url.startswith('file://'):
                quieter = 1
            else:
                quieter = 0
            self.output.info('Fetching new list... %s' % url, 4 + quieter)
            if timestamp is not None:
                self.output.info('Last-modified: %s' % timestamp, 4 + quieter)
            # Fetch the remote list
            olist = connection.read()
            self.output.debug('RemoteDB._fetch_url(), olist type = %s' %str(type(olist)),2)

            return (True, olist, timestamp)


    def check_path(self, paths, hint=True):
        '''Check for sufficient privileges'''
        self.output.debug('RemoteDB.check_path; paths = ' + str(paths), 8)
        is_ok = True
        for path in paths:
            if os.path.exists(path) and not os.access(path, os.W_OK):
                if hint:
                    self.output.warn(
                        'You do not have permission to update the cache (%s).'
                        % path)
                    import getpass
                    if getpass.getuser() != 'root':
                        self.output.warn('Hint: You are not root.\n')
                is_ok = False
        return is_ok


    def _check_download(self, olist, url):

        try:
            self.read(olist, origin=url)
        except Exception, error:
            self.output.debug("RemoteDB._check_download(), url=%s \nolist:\n" % url,2)
            self.output.debug(olist,2)
            raise IOError('Failed to parse the overlays list fetched fr'
                          'om ' + url + '\nThis means that the download'
                          'ed file is somehow corrupt or there was a pr'
                          'oblem with the webserver. Check the content '
                          'of the file. Error was:\n' + str(error))

        # the folowing is neded for py3 only
        if sys.hexversion >= 0x3000000 and hasattr(olist, 'decode'):
            olist = olist.decode("UTF-8")
        return olist


    @staticmethod
    def write_cache(olist, mpath, tpath=None, timestamp=None):
        has_updates = False
        try:
            out_file = fileopen(mpath, 'w')
            out_file.write(olist)
            out_file.close()

            if timestamp is not None and tpath is not None:
                out_file = fileopen(tpath, 'w')
                out_file.write(str(timestamp))
                out_file.close()

            has_updates = True

        except Exception, error:
            raise IOError('Failed to temporarily cache overlays list in'
                          ' ' + mpath + '\nError was:\n' + str(error))
        return has_updates

    def verify_gpg(self, url, sig, olist):
        '''Verify and decode it.'''
        self.output.debug("RemoteDB: verify_gpg(), verify & decrypt olist: "
            " %s, type(olist)=%s" % (str(url),str(type(olist))), 2)
        #self.output.debug(olist, 2)

        # detached sig
        if sig:
            self.output.debug("RemoteDB.verify_gpg(), detached sig", 2)
            self.dl_sig(url[1], sig)
            gpg_result = self.gpg.verify(
                inputtxt=olist,
                inputfile=sig)
        # armoured signed file, compressed or clearsigned
        else:
            self.output.debug("RemoteDB.verify_gpg(), single signed file", 2)
            gpg_result = self.gpg.decrypt(
                inputtxt=olist)
            olist = gpg_result.output
        # verify and report
        self.output.debug("gpg_result, verified=%s, len(olist)=%s"
            % (gpg_result.verified[0], str(len(olist))),1)
        if gpg_result.verified[0]:
            self.output.info("GPG verification succeeded for gpg-signed url.", 4)
            self.output.info('\tSignature result:' + str(gpg_result.verified), 4)
        else:
            self.output.error("GPG verification failed for gpg-signed url.")
            self.output.error('\tSignature result:' + str(gpg_result.verified))
            olist = ''
        return olist, gpg_result.verified[0]


    def dl_sig(self, url, sig):
        self.output.debug("RemoteDB.dl_sig() url=%s, sig=%s" % (url, sig),2)
        success, newsig, timestamp = self._fetch_url(url, sig)
        if success:
            success = self.write_cache(newsig, sig)
        return success


    def init_gpg(self):
        self.output.debug("RemoteDB.init_gpg(), initializing",2)
        if not self.gpg_config:
            self.gpg_config = GPGConfig()

        if not self.gpg:
            self.gpg = GPG(self.gpg_config)
        self.output.debug("RemoteDB.init_gpg(), initialized :D",2)

    def get_gpg_urls(self):
        '''Extend paths with gpg signed url listings from the config

        @param paths: list or urls to fetch
        '''
        #pair up the list url and detached sig url
        d_urls = [i.strip()
            for i in self.config['gpg_detached_lists'].split('\n') if len(i)]

        #for index in range(0, len(d_urls), 2):
        #    self.detached_urls.append((d_urls[index], d_urls[index+1]))
        for i in d_urls:
            u = i.split()
            self.detached_urls.append((u[0], u[1]))

        self.signed_urls = [i.strip()
            for i in self.config['gpg_signed_lists'].split('\n') if len(i)]


if __name__ == '__main__':
    import doctest

    # Ignore warnings here. We are just testing
    from warnings     import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
