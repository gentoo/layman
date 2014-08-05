#!/usr/bin/python
# -*- coding: utf-8 -*-
# File:       maker.py
#
#             Creates overlay definitions and writes them to an XML file
#
# Copyright:
#             (c) 2014 Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Devan Franchini <twitch153@gentoo.org>
#

#===============================================================================              
#
# Dependencies
#                                                   
#-------------------------------------------------------------------------------
from __future__ import unicode_literals

import layman.overlays.overlay as Overlay
import xml.etree.ElementTree   as ET

import argparse
import copy
import os
import re
import sys

from   layman.api            import LaymanAPI
from   layman.compatibility  import fileopen
from   layman.constants      import COMPONENT_DEFAULTS, POSSIBLE_COMPONENTS
from   layman.config         import OptionConfig
from   layman.utils          import get_ans, get_input, indent, reload_config
from   layman.version        import VERSION

#py3
if sys.hexversion >= 0x30200f0:
    _UNICODE = 'unicode'
else:
    _UNICODE = 'UTF-8'

AUTOCOMPLETE_TEMPLATE = {
    'bitbucket': {'feeds': (
                            'http://bitbucket.org/%(tail)s/atom',
                            'http://bitbucket.org/%(tail)s/rss'
                           ),
                  'homepage': 'https://bitbucket.org/%(tail)s',
                  'sources': (
                 ('https://bitbucket.org/%(tail)s', 'mercurial', '%(branch)s'),
                 ('ssh://hg@bitbucket.org/%(tail)s', 'mercurial', '%(branch)s')
                 )
                 },
    'gentoo': {'feeds': (
                         'https://git.overlays.gentoo.org/gitweb/'\
                         '?p=%(tail)s;a=atom',
                         'https://git.overlays.gentoo.org/gitweb/'\
                         '?p=%(tail)s;a=rss'
                        ),
               'homepage': 'https://git.overlays.gentoo.org/gitweb/'\
                           '?p=%(tail)s;a=summary',
               'sources': (
              ('https://git.overlays.gentoo.org/gitroot/%(tail)s', 'git', ''),
              ('git://git.overlays.gentoo.org/%(tail)s', 'git', ''),
              ('git+ssh://git@git.overlays.gentoo.org/%(tail)s', 'git', '')
              )
              },
    'gentoo-branch': {'feeds': (
                                'https://git.overlays.gentoo.org/gitweb/?p='\
                                '%(tail)s;a=atom;h=refs/heads/%(branch)s',
                                'https://git.overlays.gentoo.org/gitweb/?p='\
                                '%(tail)s;a=rss;h=refs/heads/%(branch)s'
                               ),
                      'homepage': 'https://git.overlays.gentoo.org/gitweb/?p='\
                                  '%(tail)s;a=shortlog;h=refs/heads/'\
                                  '%(branch)s',
                      'sources': (
                     ('https://git.overlays.gentoo.org/gitroot/%(tail)s', 'git', 
                      '%(branch)s'),
                     ('git://git.overlays.gentoo.org/%(tail)s', 'git', 
                      '%(branch)s'),
                     ('git+ssh://git@git.overlays.gentoo.org/%(tail)s', 'git',
                      '%(branch)s')
                     )
                     },
    'github': {'feeds': ('https://github.com/%(info)s/commits/master.atom',),
               'homepage': 'https://github.com/%(info)s',
               'sources': (
              ('https://github.com/%(tail)s', 'git', ''),
              ('git://github.com/%(tail)s', 'git', ''),
              ('git@github.com:%(tail)s', 'git', ''),
              ('https://github.com/%(tail)s', 'svn', '')
              )
              },
    'github-branch': {'feeds': ('https://github.com/%(info)s/commits/'\
                               '%(branch)s.atom'),
                     'homepage': 'https://github.com/%(info)s/tree/%(branch)s',
                     'sources': (
                     ('https://github.com/%(tail)s', 'git', '%(branch)s'),
                     ('git://github.com/%(tail)s', 'git', '%(branch)s'),
                     ('git@github.com:%(tail)s', 'git', '%(branch)s'),
                     ('https://github.com/%(tail)s', 'svn', '%(branch)s')
                     )
                     }
    }

class Interactive(object):

    def __init__(self, config=None):
        self.config = config
        if self.config:
           reload_config(self.config)
        self.layman_inst = LaymanAPI(config=self.config)
        self.output = self.config.get_option('output')
        self.overlay = {}
        self.overlays = []
        self.overlays_available = self.layman_inst.get_available()
        self.supported_types = self.layman_inst.supported_types().keys()


    def args_parser(self):
        self.parser = argparse.ArgumentParser(prog='layman-overlay-maker',
            description='Layman\'s utility script to create overlay'\
                        'definitions.')
        self.parser.add_argument('-l',
                                 '--list-autocomplete',
                                 action='store_true',
                                 help='Lists all available mirrors supported'\
                                 ' for information auto-completion'
                                )
        self.parser.add_argument('-n',
                                 '--no-extra',
                                 action='store_true',
                                 help='Don\'t add any extra overlay info,'\
                                 ' just the bare minimum requirements')
        self.parser.add_argument('-s',
                                 '--set-autocomplete',
                                 nargs='+',
                                 help='Enables auto-completion support for'\
                                 ' the selected mirror. Specify "ALL" to'\
                                 ' enable support for all available mirrors')
        self.parser.add_argument('-S',
                                 '--sudo',
                                 action='store_true',
                                 help='Bypass checks to see if an overlay'\
                                 ' name being inputted is already being used'\
                                 ' and choose the installation dir for the'\
                                 ' XML')
        self.parser.add_argument('-V',
                                 '--version',
                                 action='version',
                                 version='%(prog)s ' + VERSION)

        self.args = self.parser.parse_args()


    def __call__(self, overlay_package=None, path=None):

        if not overlay_package:
            self.args_parser()
            options = {}
            for key in vars(self.args):
                options[key] = vars(self.args)[key]
            self.config = OptionConfig(options=options)
            reload_config(self.config)

            self.auto_complete = False
            self.list_info     = self.config.get_option('list_autocomplete')
            self.no_extra      = self.config.get_option('no_extra')
            self.sudo          = self.config.get_option('sudo')

            if self.list_info:
                self.list_templates()

            if self.args.set_autocomplete:
                if 'ALL' in self.args.set_autocomplete:
                    self.templates = AUTOCOMPLETE_TEMPLATE.keys()
                    self.auto_complete = True
                else:
                    self.templates = self.args.set_autocomplete
                    self.auto_complete = True

            msg = 'How many overlays would you like to create?: '
            for x in range(1, int(get_input(msg))+1):
                self.output.notice('')
                self.output.info('Overlay #%(x)s: ' % ({'x': str(x)}))
                self.output.info('~~~~~~~~~~~~~')

                self.required = copy.deepcopy(COMPONENT_DEFAULTS)

                if not self.no_extra:
                    self.output.notice('')
                    self.update_required()
                    self.output.notice('')
                    
                self.get_overlay_components()
                ovl = Overlay.Overlay(config=self.config, ovl_dict=self.overlay, ignore=1)
                self.overlays.append((self.overlay['name'], ovl))
        else:
            ovl_name, ovl = overlay_package
            self.overlays.append((ovl_name, ovl))

        result = self.write(path)
        return result


    def check_overlay_type(self, ovl_type):
        '''
        Validates overlay type.

        @params ovl_type: str of overlay type
        @rtype None or str (if overlay type is valid).
        '''
        if ovl_type.lower() in self.supported_types:
            return ovl_type.lower()

        msg = '!!! Specified type "%(type)s" not valid.' % ({'type': ovl_type})
        self.output.warn(msg)
        msg = 'Supported types include: %(types)s.'\
              % ({'types': ', '.join(self.supported_types)})
        self.output.warn(msg)
        return None


    def guess_overlay_type(self, source_uri):
        '''
        Guesses the overlay type based on the source given.

        @params source-uri: str of source.
        @rtype None or str (if overlay type was guessed correctly).
        '''

        type_checks = copy.deepcopy(self.supported_types)

        #Modify the type checks for special overlay types.
        if 'tar' in type_checks:
            type_checks.remove(type_checks[type_checks.index('tar')])
            type_checks.insert(len(type_checks), '.tar')
                
        if 'bzr' in type_checks:
            type_checks.remove(self.supported_types[type_checks.index('bzr')])
            type_checks.insert(len(type_checks), 'bazaar')

        for guess in type_checks:
            if guess in source_uri:
                return guess

        if 'bitbucket.org' in source_uri:
            return 'mercurial'

        return None


    def update_required(self):
        '''
        Prompts user for optional components and updates
        the required components accordingly.
        '''
        for possible in POSSIBLE_COMPONENTS:
            if possible not in self.required:
                msg = 'Include %(comp)s for this overlay? [y/n]: '\
                        % ({'comp': possible})
                if ((possible in 'homepage' or possible in 'feeds') and
                    self.auto_complete):
                    available = False
                else:
                    available = get_ans(msg)
                if available:
                    self.required.append(possible)


    def get_descriptions(self):
        '''
        Prompts user for an overlay's description(s)
        and updates overlay dict with value(s).
        '''
        #TODO: Currently a "stub" function. Add multiple description
        # field support later down the road.
        descriptions = []

        desc = get_input('Define overlay\'s description: ')
        descriptions.append(desc)

        self.overlay['descriptions'] = descriptions


    def get_feeds(self):
        '''
        Prompts user for any overlay RSS feeds
        and updates overlay dict with values.
        '''
        msg = 'How many RSS feeds exist for this overlay?: '
        feed_amount = int(get_input(msg))
        feeds = []

        for i in range(1, feed_amount + 1):
            if feed_amount > 1:
                msg = 'Define overlay feed[%(i)s]: ' % ({'i': str(i)})
                feeds.append(get_input(msg))
            else:
                feeds.append(get_input('Define overlay feed: '))

        self.overlay['feeds'] = feeds
        self.output.notice('')


    def get_name(self):
        '''
        Prompts user for the overlay name
        and updates the overlay dict.
        '''
        name = get_input('Define overlay name: ')

        if not self.sudo:
            while name in self.overlays_available:
                msg = '!!! Overlay name already defined in list of installed'\
                      ' overlays.'
                self.output.warn(msg)
                msg = 'Please specify a different overlay name: '
                name = get_input(msg, color='yellow')

        self.overlay['name'] = name


    def get_sources(self):
        '''
        Prompts user for possible overlay source
        information such as type, url, and branch
        and then appends the values to the overlay
        being created.
        '''
        ovl_type = None

        if self.auto_complete:
            source_amount = 1
        else:
            msg = 'How many different sources, protocols, or mirrors exist '\
                  'for this overlay?: '
            source_amount = int(get_input(msg))

        self.overlay['sources'] = []

        for i in range(1, source_amount + 1):
            sources = []
            if source_amount > 1:
                msg = 'Define source[%(i)s]\'s URL: ' % ({'i': str(i)})
                sources.append(get_input(msg))

                ovl_type = self.guess_overlay_type(sources[0])
                msg = 'Is %(type)s the correct overlay type?: '\
                    % ({'type': ovl_type})
                correct = get_ans(msg)
                while not ovl_type or not correct:
                    msg = 'Please provide overlay type: '
                    ovl_type = self.check_overlay_type(\
                                get_input(msg, color='yellow'))
                    correct = True

                sources.append(ovl_type)
                if 'branch' in self.required:
                    msg = 'Define source[%(i)s]\'s branch (if applicable): '\
                          % ({'i': str(i)})
                    sources.append(get_input(msg))
                else:
                    sources.append('')
            else:
                sources.append(get_input('Define source URL: '))

                ovl_type = self.guess_overlay_type(sources[0])
                msg = 'Is %(type)s the correct overlay type?: '\
                       % ({'type': ovl_type})                                                      
                correct = get_ans(msg)
                while not ovl_type or not correct:
                    msg = 'Please provide overlay type: '
                    ovl_type = self.check_overlay_type(\
                                   get_input(msg, color='yellow'))
                    correct = True

                sources.append(ovl_type)
                if 'branch' in self.required:
                    msg = 'Define source branch (if applicable): '
                    sources.append(get_input(msg))
                else:
                    sources.append('')
            if self.auto_complete:
                sources = self._set_additional_info(sources)
                for source in sources:
                    self.overlay['sources'].append(source)
            else:
                self.overlay['sources'].append(sources)
        self.output.notice('')


    def get_owner(self):
        '''
        Prompts user for overlay owner info and
        then appends the values to the overlay
        being created.
        '''
        self.output.notice('')
        self.overlay['owner_name'] = get_input('Define owner name: ')
        self.overlay['owner_email'] = get_input('Define owner email: ')
        self.output.notice('')


    def get_component(self, component, msg):
        '''
        Sets overlay component value.

        @params component: (str) component to be set
        @params msg: (str) prompt message for component
        '''
        if component not in ('branch', 'type'):
            if component in ('descriptions', 'feeds', 'name', 'owner', 'sources'):
                getattr(self, 'get_%(comp)s' % ({'comp': component}))()
            else:
                self.overlay[component] = getattr('get_input')(msg)


    def get_overlay_components(self):
        '''
        Acquires overlay components via user interface.
        '''
        self.overlay = {}

        for component in self.required:
            self.get_component(component, 'Define %(comp)s: '\
                                % ({'comp': component}))


    def list_templates(self):
        '''
        Lists all available mirrors that support information auto-completion
        and exits.
        '''
        self.output.info('Mirrors supported for information auto-completion: ')
        self.output.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        for i in sorted(AUTOCOMPLETE_TEMPLATE):
            self.output.info(i)
        sys.exit()


    def read(self, path):
        '''
        Reads overlay.xml files and appends the contents
        to be sorted when writing to the file.

        @params path: path to file to be read
        '''
        try:
            document = ET.parse(path)
        except xml.etree.ElementTree.ParseError as error:
            msg = 'Interactive.read(); encountered error: %(error)s'\
                % ({'error': error})
            raise Exception(msg)

        overlays = document.findall('overlay') + document.findall('repo')

        for overlay in overlays:
            ovl_name = overlay.find('name')
            ovl = Overlay.Overlay(config=self.config, xml=overlay, ignore=1)
            self.overlays.append((ovl_name.text, ovl))


    def _set_additional_info(self, source):
        '''
        Sets additional possible overlay information.

        @params source: list of the source URL, type, and branch.
        '''
        feeds = []
        sources = []
        url = self._split_source_url(source[0])
        attrs = {'branch': source[2], 'tail': '/'.join(url[3:])}
        mirror = url[2].split('.')

        for i in self.templates:
            if i in mirror:
                if i not in ('gentoo'):
                    attrs['info'] = attrs['tail'].replace('.git', '')

                if attrs['branch']:
                    try:
                        TEMPLATE = AUTOCOMPLETE_TEMPLATE[i+'-branch']
                    except KeyError:
                        TEMPLATE = AUTOCOMPLETE_TEMPLATE[i]
                else:
                    TEMPLATE = AUTOCOMPLETE_TEMPLATE[i]
 
                self.overlay['homepage'] = TEMPLATE['homepage'] % attrs

                if i in ('bitbucket') and 'git' in (source[1]):
                    return [source]

                for s in TEMPLATE['sources']:
                    source = (s[0] % attrs, s[1], s[2] % attrs)
                    sources.append(source)
                for f in TEMPLATE['feeds']:
                    feed = (f % attrs)
                    feeds.append(feed)
                self.overlay['feeds'] = feeds

        if sources:
            return sources

        return [source]


    def _split_source_url(self, source_url):
        '''
        Splits the given source URL based on
        the source URL type.

        @params source_url: str, represents the URL for the repo.
        @rtype str: The newly split url components.
        '''
        url = None
        if re.search("^(git://)|(http://)|(https://)|(ssh://)", source_url):
            url = source_url.split('/')
        if re.search('^git\+ssh://', source_url):
            url = source_url.replace('+ssh', '')
            url = url.replace('git@', '').split('/')
        if re.search('^git@', source_url):
            url = source_url.replace('@', '//')
            url = url.replace(':', '/')
            url = url.replace('//', '://').split('/')
        if url:
            return url
        raise Exception('Interactive._split_source_url(); error: Unable '\
                        'to split URL.')


    def _sort_to_tree(self):
        '''
        Sorts all Overlay objects by overlay name
        and converts the sorted overlay objects to
        XML that is then appended to the tree.
        '''
        self.overlays = sorted(self.overlays)
        for overlay in self.overlays:
            self.tree.append(overlay[1].to_xml())


    def write(self, destination):
        '''
        Writes overlay file to desired location.
        
        @params destination: path & file to write xml to.
        @rtype bool: reflects success or failure to write xml.
        '''
        if not destination:
            filepath = self.config.get_option('overlay_defs')
            if self.sudo:
                filepath = get_input('Desired file destination dir: ')
            filename = get_input('Desired overlay file name: ')

            if not filename.endswith('.xml'):
                filename += ".xml"

            if not filepath.endswith(os.path.sep):
                filepath += os.path.sep

            destination = filepath + filename

        self.tree = ET.Element('repositories', version='1.1', encoding=_UNICODE)

        if os.path.isfile(destination):
            self.read(destination)

        self._sort_to_tree()
        indent(self.tree)
        self.tree = ET.ElementTree(self.tree)

        try:
            with fileopen(destination, 'w') as xml:
                self.tree.write(xml, encoding=_UNICODE)
            msg = 'Successfully wrote repo(s) to: %(path)s'\
                  % ({'path': destination})
            self.output.info(msg)
            return True

        except IOError as e:
            raise Exception("Writing XML failed: %(error)s" % ({'error': e}))
