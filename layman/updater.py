#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import argparse
import os
import shutil
import sys
import re

from layman.api           import LaymanAPI
from layman.compatibility import fileopen
from layman.config        import OptionConfig
from layman.constants     import DB_TYPES
from layman.db            import DB
from layman.version       import VERSION

if sys.hexversion >= 0x30200f0:
    STR = str
else:
    STR = basestring

def rename_db(config, newname, output):
    """small upgrade function to handle the name change
    for the installed xml file"""
    if os.access(config['local_list'], os.F_OK):
        output.info("  Automatic db rename, old name was..: %s"
            % config['local_list'],2)
        try:
            os.rename(config['local_list'], newname)
            output.info("  Automatic db rename, new "
                "name is...: %s" %newname, 2)
            output.notice('')
            return
        except OSError as err:
            output.error("  Automatic db rename failed:\n%s" %str(err))
    else:
        output.info("  Automatic db rename, failed access to: %s"
            % config['local_list'],2)
    output.die("  Please check that /etc/layman.cfg is up"
            " to date\nThen try running layman again.\n"
            "You may need to rename the old 'local_list' config setting"
            " to\nthe new 'installed' config setting's filename.\n")


class Main(object):

    def __init__(self, root=None, config=None, output=None):
        self.parser = None
        self.output = output
        self.config = config
        self.args = None
        self.root = root

    def args_parser(self):
        self.parser = argparse.ArgumentParser(prog='layman-updater',
            description="Layman's update script")
        self.parser.add_argument("-H", '--setup_help', action='store_true',
            help = 'Print the NEW INSTALL help messages.')
        self.parser.add_argument("-c", "--config",
            help='the path to config file')
        self.parser.add_argument("-m", "--migrate_db",
            help="the database you'd like to migrate to")
        self.parser.add_argument("-R", "--rebuild", action='store_true',
            help='rebuild the Package Manager config file')
        self.parser.add_argument('--version', action='version',
            version='%(prog)s ' + VERSION)

        self.args = self.parser.parse_args()

    def __call__(self):
        self.args_parser()
        options = None
        if self.args.config:
            options = {
                'config': self.args.config,
            }

        self.config = OptionConfig(options=options, root=self.root)
        # fix the config path
        defaults = self.config.get_defaults()
        defaults['config'] = defaults['config'] \
            % {'configdir': defaults['configdir']}
        self.config.update_defaults({'config': defaults['config']})

        self.config.read_config(defaults)

        layman_inst = LaymanAPI(config=self.config)

        self.output = layman_inst.output

        if self.args.setup_help:
            self.print_instructions()
        elif not self.check_is_new(self.args.rebuild):
            self.rename_check()
        if self.args.migrate_db:
            self.migrate_database(self.args.migrate_db)

    def check_is_new(self, rebuild=False):
        print_instructions = False
        if isinstance(self.config['conf_type'], STR):
            self.config.set_option('conf_type',
                                   self.config['conf_type'].split(','))
        for i in self.config['conf_type']:
            conf = i.replace('.', '_').strip()
            if conf and (rebuild or not os.access(self.config[conf], os.F_OK)):
                getattr(self, 'create_%(conf)s' % {'conf': conf})()
                print_instructions = True
        if print_instructions:
            self.print_instructions()
            return True
        return False



    def migrate_database(self, migrate_type):
        if migrate_type not in DB_TYPES:
            msg = 'migrate_database() error; invalid migration type: '\
                  '"%(db_type)s"' % {'db_type': migrate_type}
            self.output.die(msg)

        db = DB(self.config)
        installed = self.config['installed']
        old_ext = os.path.splitext(installed)[1]
        backup_name = installed + '.' + self.config['db_type']
        if old_ext == "." + self.config['db_type']:
            backup_name = installed + '.bak'
        new_name = installed.replace(old_ext, '.db')

        if not os.path.isfile(installed):
            msg = 'migrate_database() error; database file "%(loc)s" does not '\
                  'exist!' % {'loc': backup_name}
            self.output.error('  ' + msg)
            raise Exception(msg)

        msg = '  Creating backup of "%(db)s" at:\n "%(loc)s"\n'\
              % {'db': installed, 'loc': backup_name}
        self.output.info(msg)

        try:
            if migrate_type in ('json', 'xml'):
                shutil.copy(installed, backup_name)
            else:
                shutil.move(installed, backup_name)
        except IOError as err:
            msg = '  migrate_database() error; failed to back up old database '\
                  'file.\n  Error was: %(err)s' % {'err': err}
            self.output.error(msg)
            raise err

        db.write(installed, migrate_type=migrate_type)

        try:
            os.rename(installed, new_name)
        except OSError as err:
            msg = '  migrate_database() error: failed to rename old database '\
                  ' to "%(name)s".\n  Error was: %(err)s' % {'err': err}
            self.output.error(msg)
            raise err

        msg = '  Successfully migrated database from "%(from_type)s" to '\
              ' "%(to_type)s"\n' % {'from_type': self.config['db_type'],
                                   'to_type': migrate_type}
        self.output.info(msg)

        self.set_db_type(migrate_type, os.path.basename(new_name))

        msg = '  Warning: Please be sure to update your config file via '\
              'the\n  `dispatch-conf` command or you *will* lose database '\
              'functionality!\n'
        self.output.warn(msg)


    def rename_check(self):
        '''Checks for and renames the installed db if needed
        '''
        newname = self.config['installed']

        # check and handle the name change
        if not os.access(newname, os.F_OK):
            if os.access(self.config['local_list'], os.F_OK):
                self.output.info("  Layman automatic db rename utility, "
                    "performing update", 2)
                rename_db(self.config, newname, self.output)
        elif os.access(newname, os.F_OK) and \
            os.access(self.config['local_list'], os.F_OK):
            self.output.error("  Automatic db rename failed: "
                "Both old and new files exist")
            self.output.error(" Old file: %s still exists"
                % self.config['local_list'])
            self.output.error("  New file: %s already exists" % newname)
        elif os.access(newname, os.F_OK):
            self.output.info("  Automatic db rename: "
                "db already updated: %s" % newname)
        else:
            self.output.info("  Automatic db rename: "
                "nothing to update")
        return


    def print_instructions(self):
        messages = [
            "You are now ready to add overlays into your system.",
            "",
            "  layman -L",
            "",
            "will display a list of available overlays.",
            "",
            "Select an overlay and add it using",
            "",
            "  layman -a overlay-name",
            "",]
        if 'make.conf' in self.config['conf_type']:
            make_conf = '/etc/portage/make.conf'
            if not os.access(make_conf, os.F_OK):
                make_conf = '/etc/make.conf'
            messages += [
                "If this is the very first overlay you add with layman,",
                "you need to append the following statement to your",
                "%s file:" % make_conf,
                "",
                "  source /var/lib/layman/make.conf",
                "",
                "If you modify the 'storage' parameter in the layman",
                "configuration file (/etc/layman/layman.cfg) you will",
                "need to adapt the path given above to the new storage",
                "directory.",
                "",]

        for message in messages:
            self.output.info("  " + message)


    def create_make_conf(self):
        self.output.info("  Creating layman's make.conf file")
        layman_inst = LaymanAPI(config=self.config)
        overlays = {}
        for ovl in layman_inst.get_installed():
            overlays[ovl] = layman_inst._get_installed_db().select(ovl)
        # create layman's %(storage)s/make.conf
        # so portage won't error
        from layman.config_modules.makeconf.makeconf import ConfigHandler
        maker = ConfigHandler(self.config, overlays)
        maker.write()


    def create_repos_conf(self):
        self.output.info("  Creating layman's repos.conf file")

        if os.path.isdir(self.config['repos_conf']):
            msg = '  create_repos_conf() error: %s is a directory and will\n'\
                  '  not be written to.' % self.config['repos_conf']
            self.output.error(msg)
            return None

        conf_dir = os.path.dirname(self.config['repos_conf'])

        if not os.path.isdir(conf_dir):
            try:
                os.mkdir(conf_dir)
            except OSError as e:
                self.output.error('  create_repos_conf() error creating %s: '\
                                  % conf_dir)
                self.output.error('  "%s"' % e)
                return None

        layman_inst = LaymanAPI(config=self.config)
        overlays = {}
        for ovl in layman_inst.get_installed():
            overlays[ovl] = layman_inst._get_installed_db().select(ovl)
        # create layman's %(repos_conf) so layman
        # can write the overlays to it.
        open(self.config['repos_conf'], 'w').close()
        from layman.config_modules.reposconf.reposconf import ConfigHandler
        repos_conf = ConfigHandler(self.config, overlays)
        repos_conf.write()


    def set_db_type(self, migrate_type, installed):
        config_path = self.config['config']\
                      % {'configdir': self.config['configdir']}
        db_type_found = False
        installed_found = False
        new_conf = os.path.dirname(config_path) + '/' + '._cfg0000_' +\
                   os.path.basename(config_path)
        new_lines = []

        try:
            shutil.copy(config_path, new_conf)
        except IOError as err:
            msg = '  set_db_type() error; failed to copy "%(old)s" to '\
                  '"%(new)s\n  Error was: %(err)s"' % {'old': config_path,
                                                       'new': new_conf,
                                                       'err': err}
            self.output.error(msg)
            raise err

        if not os.path.isfile(new_conf):
            msg = 'set_db_type() error; failed to read config at "%(path)s".'\
                  % {'path': new_conf}
            self.output.error('  ' + msg)
            raise Exception(msg)

        try:
            with fileopen(new_conf, 'r') as laymanconf:
                lines = laymanconf.readlines()
        except Exception as err:
            msg = '  set_db_type() error; failed to read config at "%(path)s".'\
                  '\n  Error was: "%(err)s"' % {'path': new_conf, 'err': err}
            self.output.error(msg)
            raise err

        for line in lines:
            if re.search('^#*\s*db_type\s*:', line):
                db_type_found = True
                line = 'db_type : ' + migrate_type + '\n'
            if re.search('^#*\s*installed\s*:', line):
                installed_found = True
                line = 'installed : %(storage)s/' + installed + '\n'
            new_lines.append(line)

        if not db_type_found:
            new_lines.append('db_type : ' + migrate_type + '\n')
        if not installed_found:
            new_lines.append('installed : %(storage)s/' + installed + '\n')

        with fileopen(new_conf, 'w') as laymanconf:
            for line in new_lines:
                laymanconf.write(line)
