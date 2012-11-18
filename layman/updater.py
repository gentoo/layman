#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import stderr
import os
import argparse

from layman.config import OptionConfig
from layman.api import LaymanAPI
from layman.version import VERSION
from layman.compatibility import fileopen


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
        except OSError, err:
            output.error("  Automatic db rename failed:\n%s" %str(err))
    else:
        output.info("  Automatic db rename, failed access to: %s"
            % config['local_list'],2)
    output.die("  Please check that /etc/layman.cfg is up"
            " to date\nThen try running layman again.\n"
            "You may need to rename the old 'local_list' config setting"
            " to\nthe new 'installed' config setting's filename.\n")


class Main(object):

    def __init__(self, root=None):
        self.parser = None
        self.output = None
        self.config = None
        self.args = None
        self.root = root

    def args_parser(self):
        self.parser = argparse.ArgumentParser(prog='layman-updater',
            description="Layman's update script")
        self.parser.add_argument("-c", "--config",
            help='the path to config file')
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

        if not self.check_is_new():
            self.rename_check()


    def check_is_new(self):
        if not os.access(self.config['make_conf'], os.F_OK):
            self.create_make_conf()
            self.print_instructions()
            return True
        return False


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
        make_conf = '/etc/portage/make.conf'
        if not os.access(make_conf, os.F_OK):
            make_conf = '/etc/make.conf'
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
            "",
            "If this is the very first overlay you add with layman,",
            "you need to append the following statement to your",
            "%s file:" %make_conf,
            "",
            "  source /var/lib/layman/make.conf",
            "",
            "If you modify the 'storage' parameter in the layman",
            "configuration file (/etc/layman/layman.cfg) you will",
            "need to adapt the path given above to the new storage",
            "directory.",
            "",
        ]

        for message in messages:
            self.output.info("  " + message)


    def create_make_conf(self):
        self.output.info("  Creating layman's make.conf file")
        # create layman's %(storage)s/make.conf
        # so portage won't error
        from layman.makeconf import MakeConf
        maker = MakeConf(self.config, None)
        maker.write()



