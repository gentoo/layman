#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# LAYMAN OVERLAY BASE CLASS
################################################################################
# File:       overlay.py
#
#             Base class for the different overlay types.
#
# Copyright:
#             (c) 2005 - 2009 Gunnar Wrobel
#             (c) 2009        Sebastian Pipping
#             (c) 2009        Christian Groschupp
#             (c) 2015        Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#             Sebastian Pipping <sebastian@pipping.org>
#             Christian Groschupp <christian@groschupp.org>
#             Devan Franchini <twitch153@gentoo.org>
#
'''Basic overlay class.'''

from __future__ import unicode_literals

__version__ = "0.2"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import codecs
import locale
import os
import os.path
import re
import sys
import xml.etree.ElementTree as ET # Python 2.5

from  layman.compatibility import encode
from  layman.module        import Modules, InvalidModuleName
from  layman.utils         import pad, terminal_width, get_encoding, encoder

#===============================================================================
#
# Constants
#
#-------------------------------------------------------------------------------
MOD_PATH = path = os.path.join(os.path.dirname(__file__), 'modules')

QUALITY_LEVELS = 'core|stable|testing|experimental|graveyard'.split('|')

WHITESPACE_REGEX = re.compile('\s+')


class Overlay(object):
    ''' Derive the real implementations from this.'''

    def __init__(self, config, json=None, ovl_dict=None, xml=None, ignore=0):
        self.config = config
        self.output = config['output']
        self.module_controller = Modules(path=MOD_PATH,
                                         namepath='layman.overlays.modules',
                                         output=self.output)
        self._encoding_ = get_encoding(self.output)

        if xml is not None:
            self.from_xml(xml, ignore)
        elif ovl_dict is not None:
            self.from_dict(ovl_dict, ignore)
        elif json is not None:
            self.from_json(json, ignore)


    def __eq__(self, other):
        for i in ('descriptions', 'homepage', 'name', 'owners', 'priority',
                  'status'):
            if getattr(self, i) != getattr(other, i):
                return False
        for i in self.sources + other.sources:
            if not i in self.sources:
                return False
            if not i in other.sources:
                return False
        return True


    def __ne__(self, other):
        return not self.__eq__(other)


    def add(self, base):
        res = 1
        first_s = True
        self.output.debug('Overlay.add()', 5)
        self.sources = self.filter_protocols(self.sources)
        self.output.debug('Overlay.add(), filtered protocols, sources:' + str(self.sources), 5)
        if not self.sources:
            msg = 'Overlay.add() error: overlay "%(name)s" does not support '\
                  ' the given\nprotocol(s) %(protocol)s and cannot be '\
                  'installed.'\
                  % {'name': self.name,
                     'protocol': str(self.config['protocol_filter'])}
            self.output.error(msg)
            return 1

        for s in self.sources:
            if not first_s:
                self.output.info('\nTrying next source of listed sources...', 4)
            try:
                self.output.debug('Overlay.add(), s.add(base)', 5)
                res = s.add(base)
                if res == 0:
                    # Worked, throw other sources away
                    self.sources = [s]
                    self.output.debug('Overlay.add(), back from s.add(base)', 5)
                    break
            except Exception as error:
                self.output.warn(str(error), 4)
            first_s = False
        return res


    def delete(self, base):
        assert len(self.sources) == 1
        return self.sources[0].delete(base)


    def filter_protocols(self, sources):
        '''
        Filters any protocols not specified in self.config['protocol_filter']
        from the overlay's sources.
        '''
        _sources = []
        self.output.debug('Overlay.filter_protocols()', 5)
        self.output.debug('Overlay.filter_protocols() filters:' + str(type(self.config['protocol_filter'])), 5)
        if not self.config['protocol_filter'] and not self.config['protocol_filter'] == []:
            self.output.debug('Overlay.filter_protocols() no protocol_filter, returning', 5)
            return sources
        self.output.debug('Overlay.filter_protocols() sources:' + str(sources), 5)
        for source in sources:
            self.output.debug('Overlay.filter_protocols() source:' + str(type(source)), 5)
            self.output.debug('Overlay.filter_protocols() filters:' + str(self.config['protocol_filter']), 5)
            for protocol in self.config['protocol_filter']:
                self.output.debug('Overlay.filter_protocols() protocol: ' + protocol + ' ' + str(type(protocol)), 5)
                protocol = protocol.lower()
                #re.search considers "\+" as the literal "+".
                if protocol == 'git+ssh':
                    protocol = 'git\+ssh'
                protocol += '://'
                if re.search('^' + protocol, source.src):
                    _sources.append(source)
        self.output.debug('Overlay.filter_protocols(), returning sources' + str(_sources), 5)
        return _sources


    def from_dict(self, overlay, ignore):
        '''
        Process an overlay dictionary definition
        '''
        msg = 'Overlay from_dict(); overlay %(ovl)s' % {'ovl': str(overlay)}
        self.output.debug(msg, 6)

        _name = overlay['name']
        if _name != None:
            self.name = encode(_name)
        else:
            msg = 'Overlay from_dict(), "name" entry missing from dictionary!'
            raise Exception(msg)

        if 'source' in overlay:
            _sources = overlay['source']
        else:
            _sources = None

        if _sources == None:
            msg = 'Overlay from_dict(), "%(name)s" is missing a "source" '\
                  'entry!' % {'name': self.name}
            raise Exception(msg)

        def create_dict_overlay_source(source_):
            _src, _type, _sub = source_
            self.ovl_type = _type
            try:
                _class = self.module_controller.get_class(_type)
            except InvalidModuleName:
                _class = self.module_controller.get_class('stub')

            _location = encode(_src)
            if _sub:
                self.branch = encode(_sub)
            else:
                self.branch = None

            return _class(parent=self, config=self.config,
                _location=_location, ignore=ignore)

        self.sources = [create_dict_overlay_source(e) for e in _sources]

        self.owners = []

        if 'owner' in overlay:
            for _owner in overlay['owner']:
                owner = {}
                if 'name' in _owner and _owner['name']:
                    owner['name'] = encode(_owner['name'])
                else:
                    owner['name'] = None

                if 'email' in _owner:
                    owner['email'] = encode(_owner['email'])
                else:
                    owner['email'] = None
                    msg = 'Overlay from_dict(), "%(name)s" is missing an '\
                          '"owner.email" entry!' % {'name': self.name}
                    if not ignore:
                        raise Exception(msg)
                    elif ignore == 1:
                        self.output.warn(msg, 4)

                self.owners.append(owner)

        if 'description' in overlay:
            self.descriptions = []
            _descs = overlay['description']
            for d in _descs:
                d = WHITESPACE_REGEX.sub(' ', d)
                self.descriptions.append(encode(d))
        else:
            self.descriptions = ['']
            if not ignore:
                raise Exception('Overlay from_dict(), "' + self.name +
                    '" is missing a "description" entry!')
            elif ignore == 1:
                self.output.warn('Overlay from_dict(), "' + self.name +
                    '" is missing a "description" entry!', 4)

        if 'status' in overlay:
            self.status = encode(overlay['status'])
        else:
            self.status = None

        self.quality = 'experimental'
        if 'quality' in overlay:
            if overlay['quality'] in set(QUALITY_LEVELS):
                self.quality = encode(overlay['quality'])

        if 'priority' in overlay:
            self.priority = int(overlay['priority'])
        else:
            self.priority = 50

        if 'license' in overlay:
            self.license = encode(overlay['license'])
        else:
            self.license = None

        if 'homepage' in overlay:
            self.homepage = encode(overlay['homepage'])
        else:
            self.homepage = None

        if 'feed' in overlay:
            self.feeds = [encode(e) \
                for e in overlay['feed']]
        else:
            self.feeds = None

        if 'irc' in overlay:
            self.irc = encode(overlay['irc'])
        else:
            self.irc = None

        # end of from_dict


    def from_json(self, json, ignore):
        '''
        Process a json overlay definition
        '''
        msg = 'Overlay from_json(); overlay %(ovl)s' % {'ovl': str(json)}
        self.output.debug(msg, 6)

        _name = json['name']
        if _name != None:
            self.name = encode(_name)
        else:
            msg = 'Overlay from_json(), "name" entry missing from json!'
            raise Exception(msg)

        if 'source' in json:
            _sources = json['source']
        else:
            _sources = None

        if _sources == None:
            msg = 'Overlay from_json(), "%(name)s" is missing a "source" '\
                  'entry!' % {'name': self.name}
            raise Exception(msg)

        def create_json_overlay_source(source_):
            _src = source_['#text']
            _type = source_['@type']
            if '@branch' in source_:
                _sub = source_['@branch']
            else:
                _sub = ''

            self.ovl_type = _type

            try:
                _class = self.module_controller.get_class(_type)
            except InvalidModuleName:
                _class = self.module_controller.get_class('stub')

            _location = encode(_src)
            if _sub:
                self.branch = encode(_sub)
            else:
                self.branch = None

            return _class(parent=self, config=self.config,
                _location=_location, ignore=ignore)

        self.sources = [create_json_overlay_source(e) for e in _sources]

        _owners = json['owner']
        self.owners = []

        for _owner in _owners:
            owner = {}
            if 'name' in _owner:
                owner['name'] = encode(_owner['name'])
            else:
                owner['name'] = None
            if 'email' in _owner:
                owner['email'] = encode(_owner['email'])
            else:
                owner['email'] = None
                msg = 'Overlay from_json(), "%(name)s" is missing an '\
                      '"owner.email" entry!' % {'name': self.name}
                if not ignore:
                    raise Exception(msg)
                elif ignore == 1:
                    self.output.warn(msg, 4)
            self.owners.append(owner)

        if 'description' in json:
            self.descriptions = []
            _descs = json['description']
            for d in _descs:
                d = WHITESPACE_REGEX.sub(' ', d)
                self.descriptions.append(encode(d))
        else:
            self.descriptions = ['']
            msg = 'Overlay from_json() "%(name)s" is missing description'\
                  'entry!' % {'name': self.name}
            if not ignore:
                raise Exception(msg)
            elif ignore == 1:
                self.output.warn(msg, 4)

        if '@status' in json:
            self.status = encode(json['@status'])
        else:
            self.status = None

        self.quality = 'experimental'
        if '@quality' in json:
            if json['@quality'] in set(QUALITY_LEVELS):
                self.quality = encode(json['@quality'])

        if '@priority' in json:
            self.priority = int(json['@priority'])
        else:
            self.priority = 50

        if '@license' in json:
            self.license = encode(json['@license'])
        else:
            self.license = None

        if 'homepage' in json:
            self.homepage = encode(json['homepage'])
        else:
            self.homepage = None

        if 'feed' in json:
            self.feeds = [encode(e) \
                for e in json['feed']]
        else:
            self.feeds = None

        if 'irc' in json:
            self.irc = encode(json['irc'])
        else:
            self.irc = None

        # end of from_json()


    def from_xml(self, xml, ignore):
        '''
        Process an xml overlay definition
        '''
        def strip_text(node):
            res = node.text
            if res is None:
                return ''
            return res.strip()

        _name = xml.find('name')

        if _name != None:
            self.name = encode(strip_text(_name))
        elif 'name' in xml.attrib:
            self.name = encode(xml.attrib['name'])
        else:
            msg = 'Overlay from_xml(), "name" entry missing from xml!'
            raise Exception(msg)

        _sources = xml.findall('source')

        # new xml format
        if _sources != []:
            _sources = [e for e in _sources if 'type' in e.attrib]
        #old xml format
        elif ('src' in xml.attrib) and ('type' in xml.attrib):
            s = ET.Element('source', type=xml.attrib['type'])
            s.text = xml.attrib['src']
            _sources = [s]
            del s

        def create_overlay_source(source_elem):
            _branch = ''
            _type = source_elem.attrib['type']
            self.ovl_type = _type

            if 'branch' in source_elem.attrib:
                _branch = source_elem.attrib['branch']

            try:
                _class = self.module_controller.get_class(_type)
            except InvalidModuleName:
                _class = self.module_controller.get_class('stub')

            _location = encode(strip_text(source_elem))
            self.branch = _branch

            return _class(parent=self, config=self.config,
                _location=_location, ignore=ignore)

        if not len(_sources):
            msg = 'Overlay from_xml(), "%(name)" is missing a "source" entry!'\
                  % {'name': self.name}
            raise Exception(msg)

        self.sources = [create_overlay_source(e) for e in _sources]

        _owners = xml.findall('owner')
        self.owners = []

        # For backwards compatibility with older Overlay XML formats
        # default to this.
        if 'contact' in xml.attrib:
            owner = {'email': encode(xml.attrib['contact']),
                     'name': None}
            self.owners.append(owner)
        else:
            for _owner in _owners:
                owner = {}

                _email = _owner.find('email')
                _name = _owner.find('name')

                if _name != None:
                    owner['name'] = encode(strip_text(_name))
                else:
                    owner['name'] = None
                if _email != None:
                    owner['email'] = encode(strip_text(_email))
                else:
                    owner['email'] = None
                    msg = 'Overlay from_xml(), "%(name)s" is missing an '\
                          '"owner.email" entry!' % {'name': self.name}
                    if not ignore:
                        raise Exception(msg)
                    elif ignore == 1:
                        self.output.warn(msg, 4)

                self.owners.append(owner)

        _desc = xml.findall('description')
        if _desc != None:
            self.descriptions = []
            for d in _desc:
                d = WHITESPACE_REGEX.sub(' ', strip_text(d))
                self.descriptions.append(encode(d))
        else:
            self.descriptions = ['']
            msg = 'Overlay from_xml(), "%(name)s is missing a '\
                  '"description" entry!' % {'name': self.name}
            if not ignore:
                raise Exception(msg)
            elif ignore == 1:
                self.output.warn(msg, 4)

        if 'status' in xml.attrib:
            self.status = encode(xml.attrib['status'])
        else:
            self.status = None

        self.quality = 'experimental'
        if 'quality' in xml.attrib:
            if xml.attrib['quality'] in set(QUALITY_LEVELS):
                self.quality = encode(xml.attrib['quality'])

        if 'priority' in xml.attrib:
            self.priority = int(xml.attrib['priority'])
        else:
            self.priority = 50

        if 'license' in xml.attrib:
            self.license = encode(xml.attrib['license'])
        else:
            self.license = None

        h = xml.find('homepage')
        l = xml.find('link')

        if h != None:
            self.homepage = encode(strip_text(h))
        elif l != None:
            self.homepage = encode(strip_text(l))
        else:
            self.homepage = None

        self.feeds = [encode(strip_text(e)) for e in xml.findall('feed')]

        _irc = xml.find('irc')
        if _irc != None:
            self.irc = encode(strip_text(_irc))
        else:
            self.irc = None


    def get_infostr(self):
        '''
        Gives more detailed string of overlay information.

        @rtype str: encoded overlay information.
        '''

        result = ''

        result += self.name + '\n' + (len(self.name) * '~')

        if len(self.sources) == 1:
            result += '\nSource  : ' + self.sources[0].src
        else:
            result += '\nSources : '
            for i, v in enumerate(self.sources):
                result += '\n  %d. %s' % (i + 1, v.src)
            result += '\n'

        if len(self.owners) == 1:
            if 'name' in self.owners[0] and self.owners[0]['name'] != None:
                result += '\nContact : %s <%s>' \
                    % (self.owners[0]['name'], self.owners[0]['email'])
            else:
                result += '\nContact : ' + self.owners[0]['email']
        else:
            result += '\nContacts: '
            for i, v in enumerate(self.owners):
                result += '\n %d. ' % (i + 1)
                if 'name' in v and v['name'] != None:
                    result += '%s <%s>' % (v['name'], v['email'])
                else:
                    result += v['email']
            result += '\n'

        if len(self.sources) == 1:
            result += '\nType    : ' + self.sources[0].type
        else:
            result += '\nType    : ' + '/'.join(
                sorted(set(e.type for e in self.sources)))
        result += '; Priority: ' + str(self.priority) + '\n'
        result += 'Quality : ' + self.quality + '\n'


        for description in self.descriptions:
            description = re.compile(' +').sub(' ', description)
            description = re.compile('\n ').sub('\n', description)
            result += '\nDescription:'
            result += '\n  '.join(('\n' + description).split('\n'))
            result += '\n'

        if self.homepage != None:
            link = self.homepage
            link = re.compile(' +').sub(' ', link)
            link = re.compile('\n ').sub('\n', link)
            result += '\nLink:'
            result += '\n  '.join(('\n' + link).split('\n'))
            result += '\n'

        if self.irc != None:
            result += '\nIRC : ' + self.irc + '\n'

        if len(self.feeds):
            result += '\n%s:' % ((len(self.feeds) == 1) and "Feed" or "Feeds")
            for i in self.feeds:
                result += '\n  %s' % i
            result += '\n'

        return encoder(result, self._encoding_)


    def is_supported(self):
        return any(e.is_supported() for e in self.sources)


    def set_priority(self, priority):
        '''
        Set the priority of this overlay.
        '''
        self.priority = int(priority)


    def short_list(self, width = 0):
        '''
        Return a shortened list of overlay information.

        @params width: int specifying terminal width.
        @rtype str: string of overlay information.
        '''
        if len(self.name) > 25:
            name = self.name + "   ###\n"
            name += pad(" ", 25)
        else:
            name   = pad(self.name, 25)

        if len(set(e.type for e in self.sources)) == 1:
            _type = self.sources[0].type
        else:
            _type = '%s/..' % self.sources[0].type

        mtype  = ' [' + pad(_type, 10) + ']'
        if not width:
            width = terminal_width()-1
        srclen = width - 43
        source = ', '.join(self.source_uris())
        if len(source) > srclen:
            source = source.replace("overlays.gentoo.org", "o.g.o")
        source = ' (' + pad(source, srclen) + ')'

        return encoder(name + mtype + source, self._encoding_)


    def source_types(self):
        for i in self.sources:
            yield i.type


    def is_official(self):
        '''
        Is the overlay official?
        '''
        return self.status == 'official'


    def get_masters(self, base):
        assert len(self.sources) == 1
        return self.sources[0].get_masters(base)


    def source_uris(self):
        for i in self.sources:
            yield i.src


    def sync(self, base):
        msg = 'Overlay.sync(); name = %(name)s' % {'name': self.name}
        self.output.debug(msg, 4)

        assert len(self.sources) == 1
        return self.sources[0].sync(base)


    def to_json(self):
        '''
        Convert to json.
        '''
        repo = {}

        repo['@priority'] = str(self.priority)
        repo['@quality'] = self.quality
        if self.status != None:
            repo['@status'] = self.status
        if self.license != None:
            repo['@license'] = self.license
        repo['name'] = self.name
        repo['description'] = [i for i in self.descriptions]
        if self.homepage != None:
            repo['homepage'] = self.homepage
        if self.irc != None:
            repo['irc'] = self.irc
        repo['owner'] = [i for i in self.owners]
        repo['source'] = []
        for i in self.sources:
            source = {'@type': i.__class__.type_key}
            if i.branch:
                source['@branch'] = i.branch
            source['#text'] = i.src
            repo['source'].append(source)
        if self.feeds != None:
            repo['feed'] = []
            for feed in self.feeds:
                repo['feed'].append(feed)

        return repo


    def to_xml(self):
        '''
        Convert to xml.
        '''
        repo = ET.Element('repo')
        if self.status != None:
            repo.attrib['status'] = self.status
        repo.attrib['quality'] = self.quality
        repo.attrib['priority'] = str(self.priority)
        if self.license != None:
            repo.attrib['license'] = self.license
        name = ET.Element('name')
        name.text = self.name
        repo.append(name)
        for i in self.descriptions:
            desc = ET.Element('description')
            desc.text = i
            repo.append(desc)
            del desc
        if self.homepage != None:
            homepage = ET.Element('homepage')
            homepage.text = self.homepage
            repo.append(homepage)
        if self.irc != None:
            irc = ET.Element('irc')
            irc.text = self.irc
            repo.append(irc)
        for _owner in self.owners:
            owner = ET.Element('owner')
            owner_email = ET.Element('email')
            owner_email.text = _owner['email']
            owner.append(owner_email)
            if 'name' in _owner and _owner['name']:
                owner_name = ET.Element('name')
                owner_name.text = _owner['name']
                owner.append(owner_name)
            repo.append(owner)
        for i in self.sources:
            if not i.branch:
                source = ET.Element('source', type=i.__class__.type_key)
            else:
                source = ET.Element('source', type=i.__class__.type_key, branch=i.branch)
            source.text = i.src
            repo.append(source)
            del source
        for i in self.sources:
            # NOTE: Two loops on purpose so the
            # hooks are called with all sources in
            i.to_xml_hook(repo)
        if self.feeds != None:
            for i in self.feeds:
                feed = ET.Element('feed')
                feed.text = i
                repo.append(feed)
                del feed
        return repo


    def update(self, base, available_srcs):
        res = 1
        first_src = True
        result = False

        self.sources = self.filter_protocols(self.sources)
        available_srcs = self.filter_protocols(available_srcs)
        if not self.sources or not available_srcs:
            msg = 'Overlay.update() error: overlay "%(name)s" does not support'\
                  ' the given protocol(s) %(protocol)s and cannot be updated.'\
                  % {'name': self.name,
                     'protocol': str(self.config['protocol_filter'])}
            self.output.error(msg)
            return 1

        if isinstance(available_srcs, str):
            available_srcs = [available_srcs]

        if self.sources[0].type in self.config.get_option('support_url_updates'):
            for src in available_srcs:
                if not first_src:
                    self.output.info('\nTrying next source of listed sources...', 4)
                try:
                    res = self.sources[0].update(base, src)
                    if res == 0:
                        # Updating it worked, no need to bother
                        # checking other sources.
                        self.sources[0].src = src
                        result = True
                        break
                except Exception as error:
                    self.output.warn(str(error), 4)
                first_s = False
        else:
            # Update the overlay source with the remote
            # source, assuming that it's telling the truth
            # so it can be written to the installed.xml.
            msg = 'Overlay.update(); type: "%(src_type)s does not support '\
                  'source URL updating' % {'src_type': self.sources[0].type}
            self.output.debug(msg, 4)

            self.sources[0].src = available_srcs.pop()
            result = True
        return (self.sources, result)
