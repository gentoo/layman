#!/usr/bin/python
from __future__ import unicode_literals

import os
import sys
import shutil
import tempfile

import xml.etree.ElementTree as ET # Python 2.5

from  layman.constants         import MOUNT_TYPES
from  layman.compatibility     import fileopen
from  layman.overlays.source   import OverlaySource, require_supported
from  layman.utils             import path
from  layman.version           import VERSION
from  sslfetch.connections     import Connector

USERAGENT = "Layman-" + VERSION

class ArchiveOverlay(OverlaySource):

    type = 'Archive'
    type_key = 'archive'

    def __init__(self, parent, config, _location, ignore = 0):
        
        super(ArchiveOverlay, self).__init__(parent,
            config, _location, ignore)

        self.clean_archive = config['clean_archive']
        self.output = config['output']
        self.proxies = config.proxies
        self.branch = self.parent.branch
        self.mount_me = bool(self.type in MOUNT_TYPES)


    def _fetch(self, base, archive_url, dest_dir):
        '''
        Fetches overlay source archive.

        @params base: string of directory base for installed overlays.
        @params archive_url: string of URL where archive is located.
        @params dest_dir: string of destination of extracted archive.
        @rtype tuple (str of package location, bool to clean_archive)
        '''
        ext = self.get_extension()
 
        if 'file://' not in archive_url:
            # set up ssl-fetch output map
            connector_output = {
                'info': self.output.debug,
                'error': self.output.error,
                'kwargs-info': {'level': 2},
                'kwargs-error': {'level': None},
            }

            fetcher = Connector(connector_output, self.proxies, USERAGENT)

            success, archive, timestamp = fetcher.fetch_content(archive_url)

            pkg = path([base, self.parent.name + ext])

            try:
                with fileopen(pkg, 'w+b') as out_file:
                    out_file.write(archive)

            except Exception as error:
                raise Exception('Failed to store archive package in '\
                                '%(pkg)s\nError was: %(error)s'\
                                % ({'pkg': pkg, 'error': error}))
        
        else:
            self.clean_archive = False
            pkg = archive_url.replace('file://', '')

        return pkg


    def _add_unchecked(self, base):
        def try_to_wipe(folder):
            if not os.path.exists(folder):
                return

            try:
                self.output.info('Deleting directory %(dir)s'\
                    % ({'dir': folder}), 2)
                shutil.rmtree(folder)
            except Exception as error:
                raise Exception('Failed to remove unneccessary archive '\
                    'structure %(dir)s\nError was: %(err)s'\
                    % ({'dir': folder, 'err': error}))

        final_path = path([base, self.parent.name])
        try:
            if not self.mount_me:
                temp_path = tempfile.mkdtemp(dir=base)
            else:
                temp_path = final_path
                if not os.path.exists(temp_path):
                    os.mkdir(temp_path)
                else:
                    if os.path.ismount(temp_path):
                      self.config['mounts'].umount([self.parent.name],
                                                   dest=temp_path,
                                                   sync=True)
            pkg = self._fetch(base=base, archive_url=self.src,
                dest_dir=temp_path)
            result = self.post_fetch(pkg, temp_path)
            if self.clean_archive:
                os.unlink(pkg)
        except Exception as error:
            try_to_wipe(temp_path)
            raise error

        if result == 0 and not self.mount_me:
            if self.branch:
                source = temp_path + os.path.sep + self.branch
            else:
                source = temp_path

            if os.path.exists(source):
                if os.path.exists(final_path):
                    self.delete(base)

                try:
                    os.rename(source, final_path)
                except Exception as error:
                    raise Exception('Failed to rename archive subdirectory '\
                        '%(src)s to %(path)s\nError was: %(err)s'\
                        % ({'src': source, 'path': final_path, 'err': error}))
                os.chmod(final_path, 0o755)
            else:
                raise Exception('The given path (branch setting in the xml)\n'\
                    ' %(src)s does not exist in this archive package!'\
                    % ({'src': source}))

        if not self.mount_me:
            try_to_wipe(temp_path)

        return result


    def add(self, base):
        '''
        Add overlay.

        @params base: string location where overlays are installed.
        @rtype bool
        '''
        
        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        if os.path.exists(target):
            raise Exception('Directory %(dir)s already exists. Will not '\
                'overwrite its contents!' % ({'dir': target}))

        return self.postsync(
            self._add_unchecked(base),
            cwd=target)


    def sync(self, base):
        '''
        Sync overlay.

        @params base: string location where overlays are installed.
        @rtype bool
        '''

        if not self.supported():
            return 1

        target = path([base, self.parent.name])

        return self.postsync(
            self._add_unchecked(base),
            cwd=target)


    def supported(self):
        '''
        Determines if overlay type is supported.

        @rtype bool
        '''

        return self.is_supported()


if __name__ == '__main__':
    import doctest

    # Ignore warnings here. We are just testing.
    from warnings    import filterwarnings, resetwarnings
    filterwarnings('ignore')

    doctest.testmod(sys.modules[__name__])

    resetwarnings()
