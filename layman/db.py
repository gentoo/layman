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

from __future__ import unicode_literals
from __future__ import with_statement

__version__ = "$Id: db.py 309 2007-04-09 16:23:38Z wrobel $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os, os.path

from   layman.utils             import path, delete_empty_directory, get_ans
from   layman.dbbase            import DbBase
from   layman.repoconfmanager   import RepoConfManager

#===============================================================================
#
# Class DB
#
#-------------------------------------------------------------------------------

class DB(DbBase):
    ''' Handle the list of installed overlays.'''

    def __init__(self, config):

        self.config = config
        self.output = config['output']

        self.path = config['installed']
        self.output.debug("DB.__init__(): config['installed'] = %s" % self.path, 3)

        if config['nocheck']:
            ignore = 2
        else:
            ignore = 1


        DbBase.__init__(self,
                          config,
                          paths=[config['installed'], ],
                          ignore=ignore,
                          allow_missing=True,
                          )

        self.repo_conf = RepoConfManager(self.config, self.overlays)

        self.output.debug('DB handler initiated', 6)

        # check and handle the name change
        if not os.access(self.config['installed'], os.F_OK) and \
            os.access(self.config['local_list'], os.F_OK):
                self.output.die("Please run layman-updater, "
                    "then run layman again")


    # overrider
    def _broken_catalog_hint(self):
        return ''


    def _check_official(self, overlay):
        '''
        Prompt user to see if they want to install unofficial overlays.

        @params overlay: layman.overlays.Overlay object.
        @rtype bool: reflect the user's decision to install overlay.
        '''
        if self.config['check_official'] and not overlay.status == 'official':
            msg = 'Overlay "%(repo)s" is not official. Continue installing?'\
                  ' [y/n]: ' % {'repo': overlay.name}
            if not get_ans(msg, color='green'):
                msg = 'layman will not add "%(repo)s", due to user\'s'\
                      ' decision\nto not install unofficial overlays.'\
                      % {'repo': overlay.name}
                hint = 'Hint: To remove this check, set "check_official"'\
                       ' to "No"\nin your layman.cfg.'
                self.output.warn(msg)
                self.output.notice('')
                self.output.warn(hint)
                return False
            else:
                return True
        return True


    def add(self, overlay):
        '''
        Add an overlay to the local list of overlays.
        '''
        if overlay.name not in self.overlays.keys():
            if not self._check_official(overlay):
                return False
            result = overlay.add(self.config['storage'])
            if result == 0:
                if 'priority' in self.config.keys():
                    overlay.set_priority(self.config['priority'])
                self.overlays[overlay.name] = overlay
                self.write(self.path)
                repo_ok = self.repo_conf.add(overlay)
                if False in repo_ok:
                    return False
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
        Delete an overlay from the local list of overlays.
        '''
        if overlay.name in self.overlays.keys():
            overlay.delete(self.config['storage'])
            repo_ok = self.repo_conf.delete(overlay)
            self.remove(overlay, self.path)
            self.write(self.path, remove=True)
        else:
            self.output.error('No local overlay named "' + overlay.name + '"!')
            return False
        if False in repo_ok:
            return False
        return True


    def disable(self, overlay):
        if overlay.name in self.overlays.keys():
            result = self.repo_conf.disable(overlay)
        else:
            self.output.error('No local overlay named "%(repo)s"!'\
                % ({'repo': overlay.name}))
            return False
        msg = 'Overlay %(repo)s has been disabled.\n'\
              'All ebuilds in this overlay will not be recognized by portage.'\
              % ({'repo': overlay.name})
        if result:
            self.output.warn(msg)
        return result


    def enable(self, overlay):
        if overlay.name in self.overlays.keys():
            result = self.repo_conf.enable(overlay)
        else:
            self.output.error('No local overlay named "%(repo)s"!'\
                % ({'repo': overlay.name}))
            return False
        msg = 'Overlay %(repo)s has been enabled.\n'\
              'All ebuilds in this overlay will now be recognized by portage.'\
              % ({'repo': overlay.name})
        if result:
            self.output.info(msg)
        return result


    def update(self, overlay, available_srcs):
        '''
        Updates the overlay source via the available source(s).

        @params overlay: layman.overlay.Overlay object.
        @params available_srcs: set of available source URLs.
        '''

        source, result = self.overlays[overlay.name].update(self.config['storage'],
                                                    available_srcs)
        result = [result]
        self.overlays[overlay.name].sources = source
        result.extend(self.repo_conf.update(self.overlays[overlay.name]))
        self.write(self.path)

        if False in result:
            return False
        return True



    def sync(self, overlay_name):
        '''Synchronize the given overlay.'''

        overlay = self.select(overlay_name)
        result = overlay.sync(self.config['storage'])
        if result:
            raise Exception('Syncing overlay "' + overlay_name +
                            '" returned status ' + str(result) + '!' +
                            '\ndb.sync()')
