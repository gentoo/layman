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

import copy
import os
import re
import sys

from   layman.api            import LaymanAPI
from   layman.compatibility  import fileopen
from   layman.constants      import COMPONENT_DEFAULTS, POSSIBLE_COMPONENTS
from   layman.config         import OptionConfig
from   layman.utils          import indent, reload_config

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

    def __init__(self):
        self.config = OptionConfig()
        reload_config(self.config)
        self.layman_inst = LaymanAPI(config=self.config)
        self.overlay = {}
        self.overlays = []
        self.overlays_available = self.layman_inst.get_available()
        self.supported_types = self.layman_inst.supported_types().keys()

    def __call__(self, overlay_package=None, path=None):

        if not overlay_package:
            for x in range(1, int(self.get_input("How many overlays would you like to create?: "))+1):
                self.info_available = False
                print('')
                print('Overlay #%(x)s: ' % ({'x': str(x)}))
                print('~~~~~~~~~~~~~')

                self.info_available = self.get_ans('Is the mirror for this '\
                    'overlay either github.com,\ngit.overlays.gentoo.org, or'\
                    'bitbucket.org? [y/n]: ')
                print('')
                self.update_required()
                print('')
                self.get_overlay_components()
                ovl = Overlay.Overlay(config=self.config, ovl_dict=self.overlay, ignore=1)
                self.overlays.append((self.overlay['name'], ovl))
        else:
            ovl_name, ovl = overlay_package
            self.overlays.append((ovl_name, ovl))

        result = self.write(path)
        return result


    def get_input(self, msg):
        '''
        py2 py3 compatibility function
        to obtain user input.

        @params msg: message prompt for user
        @rtype str: input from user
        '''
        try:
            value = raw_input(msg)
        except NameError:
            value = input(msg)
        
        return value


    def get_ans(self, msg):
        '''
        Handles yes/no input

        @params msg: message prompt for user
        @rtype boolean: reflects whether the user answered yes or no.
        '''
        ans = self.get_input(msg).lower()

        while ans not in ('y', 'yes', 'n', 'no'):
            ans = self.get_input('Please respond with [y/n]: ').lower()

        return ans in ('y', 'yes')


    def check_overlay_type(self, ovl_type):
        '''
        Validates overlay type.

        @params ovl_type: str of overlay type
        @rtype None or str (if overlay type is valid).
        '''
        if ovl_type.lower() in self.supported_types:
            return ovl_type.lower()
        print('Specified type "%(type)s" not valid.' % ({'type': ovl_type}))
        print('Supported types include: %(types)s.'\
            % ({'types': ', '.join(self.supported_types)}))
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
        # Don't assume they want the same
        # info for the next overlay.
        self.required = copy.deepcopy(COMPONENT_DEFAULTS)

        for possible in POSSIBLE_COMPONENTS:
            if possible not in self.required:
                msg = 'Include %(comp)s for this overlay? [y/n]: '\
                        % ({'comp': possible})
                if ((possible in 'homepage' or possible in 'feeds') and
                   self.info_available):
                    available = False
                else:
                    available = self.get_ans(msg)
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

        desc = self.get_input('Define overlay\'s description: ')
        descriptions.append(desc)

        self.overlay['descriptions'] = descriptions


    def get_feeds(self):
        '''
        Prompts user for any overlay RSS feeds
        and updates overlay dict with values.
        '''
        feed_amount = int(self.get_input('How many RSS feeds exist for this overlay?: '))
        feeds = []

        for i in range(1, feed_amount + 1):
            if feed_amount > 1:
                feeds.append(self.get_input('Define overlay feed[%(i)s]: '\
                    % ({'i': str(i)})))
            else:
                feeds.append(self.get_input('Define overlay feed: '))

        self.overlay['feeds'] = feeds
        print('')


    def get_name(self):
        '''
        Prompts user for the overlay name
        and updates the overlay dict.
        '''
        name = self.get_input('Define overlay name: ')

        while name in self.overlays_available:
            print('!!! Overlay name already defined in list of installed overlays.')
            name = self.get_input('Please specify a different overlay name: ')

        self.overlay['name'] = name


    def get_sources(self):
        '''
        Prompts user for possible overlay source
        information such as type, url, and branch
        and then appends the values to the overlay
        being created.
        '''
        ovl_type = None

        if self.info_available:
            source_amount = 1
        else:
            source_amount = int(self.get_input('How many different sources,'\
                    ' protocols, or mirrors exist for this overlay?: '))

        self.overlay['sources'] = []

        for i in range(1, source_amount + 1):
            sources = []
            if source_amount > 1:
                sources.append(self.get_input('Define source[%(i)s] URL: '\
                    % ({'i': str(i)})))

                ovl_type = self.guess_overlay_type(sources[0])
                correct = self.get_ans('Is %(type)s the correct overlay'\
                                ' type?: ' % ({'type': ovl_type}))
                while not ovl_type or not correct:
                    ovl_type = self.check_overlay_type(\
                                self.get_input('Please provide overlay'\
                                ' type: '))
                    correct = True

                sources.append(ovl_type)
                if 'branch' in self.required:
                    sources.append(self.get_input('Define source[%(i)s]\'s '\
                        'branch (if applicable): ' % ({'i': str(i)})))
                else:
                    sources.append('')
            else:
                sources.append(self.get_input('Define source URL: '))

                ovl_type = self.guess_overlay_type(sources[0])
                correct = self.get_ans('Is %(type)s the correct overlay'\
                                ' type?: ' % ({'type': ovl_type}))
                while not ovl_type or not correct:
                    ovl_type = self.check_overlay_type(\
                                   self.get_input('Please provide overlay'\
                                   ' type: '))
                    correct = True

                sources.append(ovl_type)
                if 'branch' in self.required:
                    sources.append(self.get_input('Define source branch (if applicable): '))
                else:
                    sources.append('')
            if self.info_available:
                sources = self._set_additional_info(sources)
                for source in sources:
                    self.overlay['sources'].append(source)
            else:
                self.overlay['sources'].append(sources)
        print('')


    def get_owner(self):
        '''
        Prompts user for overlay owner info and
        then appends the values to the overlay
        being created.
        '''
        print('')
        self.overlay['owner_name'] = self.get_input('Define owner name: ')
        self.overlay['owner_email'] = self.get_input('Define owner email: ')
        print('')


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
                self.overlay[component] = getattr(self, 'get_input')(msg)


    def get_overlay_components(self):
        '''
        Acquires overlay components via user interface.
        '''
        self.overlay = {}

        for component in self.required:
            self.get_component(component, 'Define %(comp)s: '\
                                % ({'comp': component}))


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
            print(msg)

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

        for i in AUTOCOMPLETE_TEMPLATE.keys():
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
        print('Interactive._split_source_url(); error: Unable to split URL.')


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
            filename = self.get_input('Desired overlay file name: ')
            filepath = self.config.get_option('overlay_defs')

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
            print('Successfully wrote to: %(path)s' % ({'path': destination}))
            return True

        except IOError as e:
            print("Writing XML failed: %(error)s" % ({'error': e}))

        return False
