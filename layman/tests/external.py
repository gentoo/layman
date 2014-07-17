# -*- coding: utf-8 -*-
#################################################################################
# EXTENRAL LAYMAN TESTS
#################################################################################
# File:       external.py
#
#             Runs external (non-doctest) test cases.
#
# Copyright:
#             (c) 2009        Sebastian Pipping
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Sebastian Pipping <sebastian@pipping.org>
#
'''Runs external (non-doctest) test cases.'''

import os
import shutil
import tempfile
import unittest
#Py3
try:
    import urllib.request as urllib
except ImportError:
    import urllib

from  layman.db               import DB
from  layman.dbbase           import DbBase
from  layman.compatibility    import fileopen
from  layman.config           import BareConfig, OptionConfig
from  layman.output           import Message
from  layman.overlays.overlay import Overlay
from  layman.repoconfmanager  import RepoConfManager
from  warnings import filterwarnings, resetwarnings

HERE = os.path.dirname(os.path.realpath(__file__))

class AddDeleteEnableDisableFromDB(unittest.TestCase):

    def test(self):
        tmpdir = tempfile.mkdtemp(prefix='laymantmp_')
        makeconf = os.path.join(tmpdir, 'make.conf')
        reposconf = os.path.join(tmpdir, 'repos.conf')

        make_txt =\
        'PORTDIR_OVERLAY="\n'\
        '$PORTDIR_OVERLAY"'

        # Create the .conf files so layman doesn't
        # complain.
        with fileopen(makeconf, 'w') as f:
            f.write(make_txt)

        with fileopen(reposconf, 'w') as f:
            f.write('')

        my_opts = {
                   'installed' :
                   HERE + '/testfiles/global-overlays.xml',
                   'make_conf' : makeconf,
                   'nocheck'    : 'yes',
                   'storage'   : tmpdir,
                   'repos_conf' : reposconf,
                   'conf_type' : ['make.conf', 'repos.conf'],
                   }

        config = OptionConfig(my_opts)
        config.set_option('quietness', 3)

        a = DB(config)
        config['output'].set_colorize(False)

        conf = RepoConfManager(config, a.overlays)

        # Set up our success tracker.
        success = []

        # Add all the overlays in global_overlays.xml.
        for overlay in a.overlays.keys():
            conf_success = conf.add(a.overlays[overlay])
            if False in conf_success:
                success.append(False)
            else:
                success.append(True)

        # Disable one overlay.
        conf_success = conf.disable(a.overlays['wrobel'])
        if False in conf_success:
            success.append(False)
        else:
            success.append(True)

        # Enable disabled overlay.
        conf_success = conf.enable(a.overlays['wrobel'])
        if False in conf_success:
            success.append(False)
        else:
            success.append(True)
        # Delete all the overlays in global_overlays.xml.
        for overlay in a.overlays.keys():
            conf_success = conf.delete(a.overlays[overlay])
            if False in conf_success:
                success.append(False)
            else:
                success.append(True)

        # Clean up.
        os.unlink(makeconf)
        os.unlink(reposconf)

        shutil.rmtree(tmpdir)

        if False in success:
            success = False
        else:
            success = True

        self.assertTrue(success)


class Unicode(unittest.TestCase):
    def _overlays_bug(self, number):
        config = BareConfig()
        filename = os.path.join(HERE, 'testfiles', 'overlays_bug_%d.xml' % number)
        o = DbBase(config, [filename])
        for verbose in (True, False):
            for t in o.list(verbose=verbose):
                print(t[0].decode('utf-8'))
                print()

    def test_184449(self):
        self._overlays_bug(184449)

    def test_286290(self):
        self._overlays_bug(286290)


class FormatBranchCategory(unittest.TestCase):
    def _run(self, number):
        #config = {'output': Message()}
        config = BareConfig()
        # Discuss renaming files to "branch-%d.xml"
        filename1 = os.path.join(HERE, 'testfiles',
                'subpath-%d.xml' % number)

        # Read, write, re-read, compare
        os1 = DbBase(config, [filename1])
        filename2 = tempfile.mkstemp()[1]
        os1.write(filename2)
        os2 = DbBase(config, [filename2])
        os.unlink(filename2)
        self.assertTrue(os1 == os2)

        # Pass original overlays
        return os1

    def test(self):
        os1 = self._run(1)
        os2 = self._run(2)

        # Same content from old/layman-global.txt
        #   and new/repositories.xml format?
        self.assertTrue(os1 == os2)


# http://bugs.gentoo.org/show_bug.cgi?id=304547
class TarAddRemoveSync(unittest.TestCase):
    def test(self):
        repo_name = 'tar-test-overlay'
        tar_source_path = os.path.join(HERE, 'testfiles', 'layman-test.tar.bz2')

        # Duplicate test tarball (so we have it deletable for later)
        (_, temp_tarball_path) = tempfile.mkstemp()
        shutil.copyfile(tar_source_path, temp_tarball_path)

        # Write overlay collection XML
        xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<repositories xmlns="" version="1.0">
  <repo quality="experimental" status="unofficial">
    <name>%(repo_name)s</name>
    <description>XXXXXXXXXXX</description>
    <owner>
      <email>foo@exmaple.org</email>
    </owner>
    <source type="tar">file://%(temp_tarball_url)s</source>
  </repo>
</repositories>
""" % {     'temp_tarball_url':urllib.pathname2url(temp_tarball_path),
            'repo_name':repo_name}
        (fd, temp_collection_path) = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as f:
            f.write(xml_text)

        # Make playground directory
        temp_dir_path = tempfile.mkdtemp()

        # Make DB from it
        #config = {'output': Message(), 'tar_command':'/bin/tar'}
        config = BareConfig()
        db = DbBase(config, [temp_collection_path])

        specific_overlay_path = os.path.join(temp_dir_path, repo_name)
        o = db.select('tar-test-overlay')

        # Actual testcase
        o.add(temp_dir_path)
        self.assertTrue(os.path.exists(specific_overlay_path))
        # (1/2) Sync with source available
        o.sync(temp_dir_path)
        self.assertTrue(os.path.exists(specific_overlay_path))
        os.unlink(temp_tarball_path)
        try:
            # (2/2) Sync with source _not_ available
            o.sync(temp_dir_path)
        except:
            pass
        self.assertTrue(os.path.exists(specific_overlay_path))
        o.delete(temp_dir_path)
        self.assertFalse(os.path.exists(specific_overlay_path))

        # Cleanup
        os.unlink(temp_collection_path)
        os.rmdir(temp_dir_path)


if __name__ == '__main__':
    filterwarnings('ignore')
    unittest.main()
    resetwarnings()
