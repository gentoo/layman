#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import stderr
import os
import argparse

from layman.config import OptionConfig
from layman.api import LaymanAPI
from layman.version import VERSION


def rename_db(config, newname, output):
    """small upgrade function to handle the name change
    for the installed xml file"""
    if os.access(config['local_list'], os.F_OK):
        output.info("Automatic db rename, old name was..: %s"
            % config['local_list'],2)
        try:
            os.rename(config['local_list'], newname)
            output.info("Automatic db rename, new "
                "name is...: %s" %newname, 2)
            output.notice('')
            return
        except OSError, err:
            output.error("Automatic db rename failed:\n%s" %str(err))
    else:
        output.info("Automatic db rename, failed access to: %s"
            % config['local_list'],2)
    output.die("Please check that /etc/layman.cfg is up"
            " to date\nThen try running layman again.\n"
            "You may need to rename the old 'local_list' config setting"
            " to\nthe new 'installed' config setting's filename.\n")


class Main(object):

    def __init__(self):
        self.parser = None
        self.output = None
        self.config = None
        self.args = None

    def args_parser(self):
        self.parser = argparse.ArgumentParser(prog='layman-updater',
            description="Layman's DB update script")
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

        self.config = OptionConfig(options=options)
        self.config.read_config(self.config.get_defaults())

        layman_inst = LaymanAPI(config=self.config)

        self.output = layman_inst.output

        self.rename_check()


    def rename_check(self):
        '''Checks for and renames the installed db if needed
        '''
        newname = self.config['installed']

        # check and handle the name change
        if not os.access(newname, os.F_OK):
            if os.access(self.config['local_list'], os.F_OK):
                self.output.info("Layman automatic db rename utility, "
                    "performing update", 2)
                rename_db(self.config, newname, self.output)
        elif os.access(newname, os.F_OK) and \
            os.access(self.config['local_list'], os.F_OK):
            self.output.error("Automatic db rename failed: "
                "Both old and new files exist")
            self.output.error("Old file: %s still exists"
                % self.config['local_list'])
            self.output.error("New file: %s already exists" % newname)
        else:
            self.output.info("Automatic db rename "
                "already updated: %s" % newname)
        return
