#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# POLYMERAZE XML UTILITIES
#################################################################################
# File:       xml.py
#
#             Utilities to deal with xml nodes.
#
# Copyright:
#             (c) 2005 - 2008 Gunnar Wrobel
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Gunnar Wrobel <wrobel@gentoo.org>
#

'''Utility functions to deal with xml nodes. '''

__version__ = '$Id: utils.py 236 2006-09-05 20:39:37Z wrobel $'

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import types, re

#===============================================================================
#
# Helper functions
#
#-------------------------------------------------------------------------------

def node_to_text(node):
    '''
    Reduces an xml node to its text elements. The function does not
    collect the text nodes recursively.

    >>> import xml.dom.minidom
    >>> imp = xml.dom.minidom.getDOMImplementation()
    >>> doc = imp.createDocument('test', 'root', None)
    >>> root =  doc.childNodes[0]
    >>> node = doc.createTextNode('text')
    >>> a = root.appendChild(node)
    >>> node = doc.createElement('text')
    >>> node2 = doc.createTextNode('text')
    >>> a = node.appendChild(node2)
    >>> a = root.appendChild(node)
    >>> node = doc.createTextNode('text')
    >>> a = root.appendChild(node)
    >>> doc.toprettyxml('', '') #doctest: +ELLIPSIS
    '<?xml version="1.0" ?>...<root>text<text>text</text>text</root>'

    >>> node_to_text(root)
    'texttext'

    '''
    text = ''

    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            text = text + child.data

    return text

def node_to_dict(node):
    ''' Converts a xml node to a dictionary. The function collects the
    nodes recursively. Attributes will be prepended with '&', child
    nodes will be surrounded with tags. An index will be appended
    since several child nodes with the same tag may exist. Text
    elements will be collapsed and stored in a n entry prepended with
    '@'. Comments will be ignored.

    >>> import xml.dom.minidom
    >>> imp = xml.dom.minidom.getDOMImplementation()
    >>> doc = imp.createDocument('test', 'root', None)
    >>> root =  doc.childNodes[0]
    >>> node = doc.createTextNode('text')
    >>> a = root.appendChild(node)
    >>> node = doc.createElement('text')
    >>> node2 = doc.createTextNode('text')
    >>> comm = doc.createComment('comment')
    >>> attr = doc.createAttribute('&attr')
    >>> a = node.appendChild(node2)
    >>> a = root.appendChild(comm)
    >>> node.setAttributeNode(attr)
    >>> node.setAttribute('&attr','test')
    >>> a = root.appendChild(node)
    >>> node3 = doc.createElement('text')
    >>> a = root.appendChild(node3)
    >>> node = doc.createTextNode('text')
    >>> a = root.appendChild(node)
    >>> doc.toprettyxml('', '') #doctest: +ELLIPSIS
    '<?xml version="1.0" ?>...<root>text<!--comment--><text &attr="test">text</text><text/>text</root>'

    >>> node_to_dict(root)
    {'<text>1': {'@': 'text', '&&attr': 'test'}, '<text>2': {'@': ''}, '@': 'texttext'}

    '''
    result = {}

    # Map the attributes
    for index in range(0, node.attributes.length):
        attr = node.attributes.item(index)
        result['&' +  attr.name] = attr.nodeValue

    text = ''

    # Map the nodes
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            text = text + child.data
        if child.nodeType == child.ELEMENT_NODE:
            index = 1
            while ('<' + child.tagName + '>' + str(index)) in result.keys():
                index += 1
            result['<' + child.tagName + '>' + str(index)] = node_to_dict(child)

    result['@'] = text

    return result

def dict_to_node(data, document, root_name):
    ''' Reverts the node_to_dict operation.

    >>> import xml.dom.minidom
    >>> imp = xml.dom.minidom.getDOMImplementation()
    >>> doc = imp.createDocument('test', 'root', None)
    >>> a = {'<text>1': {'@': 'text', '&&attr': 'test'}, '<text>2': {'@': ''}, '@': 'texttext'}
    >>> doc.childNodes[0] = dict_to_node(a, doc, 'root')
    >>> doc.toprettyxml('', '') #doctest: +ELLIPSIS
    '<?xml version="1.0" ?>...<root><text &attr="test">text</text><text></text>texttext</root>'

    '''
    node = document.createElement(root_name)

    for i, j in data.items():

        if i[0] == '&':
            attr = document.createAttribute(i[1:])
            node.setAttributeNode(attr)
            node.setAttribute(i[1:], j)
        if i[0] == '<':
            k = i[1:]
            while k[-1] in '0123456789':
                k = k[:-1]
            child = dict_to_node(data[i],
                                 document,
                                 k[:-1])
            node.appendChild(child)
        if i[0] == '@':
            child = document.createTextNode(j)
            node.appendChild(child)

    return node

def path(path_elements):
    '''
    Concatenate a path from several elements.

    >>> path([])
    ''
    >>> path(['a'])
    'a'
    >>> path(['a','b'])
    'a/b'
    >>> path(['a/','b'])
    'a/b'
    >>> path(['/a/','b'])
    '/a/b'
    >>> path(['/a/','b/'])
    '/a/b'
    >>> path(['/a/','b/'])
    '/a/b'
    >>> path(['/a/','/b/'])
    '/a/b'
    >>> path(['/a/','/b','c/'])
    '/a/b/c'
    '''
    pathname = ''

    if type(path_elements) in types.StringTypes:
        path_elements = [path_elements]

    # Concatenate elements and seperate with /
    for i in path_elements:
        pathname += i + '/'

    # Replace multiple consecutive slashes
    pathname = re.compile('/+').sub('/', pathname)

    # Remove the final / if there is one
    if pathname and pathname[-1] == '/':
        pathname = pathname[:-1]

    return pathname

#===============================================================================
#
# Testing
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
