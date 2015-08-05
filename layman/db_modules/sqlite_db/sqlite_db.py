#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN SQLite DB
#################################################################################
# File:       sqlite_db.py
#
#             Access SQLite overlay database(s).
#
# Copyright:
#             (c) 2015        Devan Franchini
#             Distributed under the terms of the GNU General Public License v2
#
# Author(s):
#             Devan Franchini <twitch153@gentoo.org>
#
'''Handler for sqlite overlay databases.'''

from __future__ import unicode_literals

__version__ = "$Id: sqlite_db.py 273 2015-08-03 20:17:30Z twitch153 $"

#===============================================================================
#
# Dependencies
#
#-------------------------------------------------------------------------------

import os
import sys
import sqlite3

from   layman.overlays.overlay   import Overlay

#py3.2+
if sys.hexversion >= 0x30200f0:
    _UNICODE = 'unicode'
else:
    _UNICODE = 'UTF-8'


#===============================================================================
#
# Class DBHandler
#
#-------------------------------------------------------------------------------

class DBHandler(object):
    '''
    Handle a SQLite overlay database.
    '''

    def __init__(self, config, overlays, paths=None, ignore=0,
                 ignore_init_read_errors=False):

        self.config = config
        self.ignore = ignore
        self.overlays = overlays
        self.paths = paths
        self.output = config['output']
        self.ignore_init_read_errors = ignore_init_read_errors

        self.output.debug('Initializing SQLite overlay list handler', 8)


    def __connect__(self, path):
        '''
        Establish connection with the SQLite database.
        '''
        if not os.path.exists(path):
            if not self.ignore_init_read_errors:
                msg = 'SQLite DBHandler warning; database previously '\
                      'non-existent.\nCreating database now...'
                self.output.warn(msg, 2)

            if not os.access(os.path.dirname(path), os.W_OK):
                msg = 'SQLite DBHandler error; cannot create database.\n'
                errmsg = 'Write permissions are not given in dir: "%(dir)s"'\
                      % {'dir': os.path.dirname(path)}
                self.output.error(msg + errmsg)
                
                raise Exception(errmsg)

        if os.path.exists(path) and not os.access(path, os.R_OK):
            msg = 'SQLite DBHandler error; database lacks read permissions'\
                  ' cannot continue.'
            self.output.error(msg)

            raise Exception(msg)

        self.__create_database__(path)

        return sqlite3.connect(path)


    def __create_database__(self, path):
        '''
        Create the LaymanOverlays database if it doesn't exist.
        '''
        with sqlite3.connect(path) as connection:
            cursor = connection.cursor()
            try:
                cursor.execute('''CREATE TABLE IF NOT EXISTS Overlay
                ( Overlay_ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, 
                Priority TEXT, Status TEXT, Quality TEXT, Homepage 
                TEXT, IRC TEXT, License TEXT, UNIQUE (Name) ON CONFLICT IGNORE )
                ''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS Owner ( Owner_ID
                INTEGER PRIMARY KEY AUTOINCREMENT, Owner_Name TEXT, 
                Owner_Email TEXT, UNIQUE (Owner_Name, Owner_Email) ON 
                CONFLICT IGNORE )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS Source ( Source_ID
                INTEGER PRIMARY KEY AUTOINCREMENT, Type TEXT, Branch TEXT, 
                URL TEXT, UNIQUE (Type, URL) ON CONFLICT IGNORE )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS Description 
                ( Description_ID INTEGER PRIMARY KEY AUTOINCREMENT, 
                Overlay_ID INTEGER, Description TEXT, FOREIGN 
                KEY(Overlay_ID) REFERENCES Overlay(Overlay_ID), 
                UNIQUE (Overlay_ID, Description) ON CONFLICT IGNORE )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS Feed ( Feed_ID 
                INTEGER PRIMARY KEY AUTOINCREMENT, Overlay_ID INTEGER, 
                Feed TEXT, FOREIGN KEY(Overlay_ID) REFERENCES 
                Overlay(Overlay_ID), UNIQUE (Overlay_ID, Feed) ON CONFLICT 
                IGNORE )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS Overlay_Source
                ( Overlay_Source_ID INTEGER PRIMARY KEY AUTOINCREMENT, 
                Overlay_ID INTEGER, Source_ID INTEGER, FOREIGN KEY(Overlay_ID) 
                REFERENCES Overlay(Overlay_ID), FOREIGN KEY(Source_ID) 
                REFERENCES Source(SourceID), UNIQUE (Overlay_ID, Source_ID) ON 
                CONFLICT IGNORE )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS Overlay_Owner
                ( Overlay_Owner_ID INTEGER PRIMARY KEY AUTOINCREMENT, 
                Overlay_ID INTEGER, Owner_ID INTEGER, FOREIGN KEY(Overlay_ID) 
                REFERENCES Overlay(Overlay_ID), FOREIGN KEY(Owner_ID) 
                REFERENCES Owner(Owner_ID), UNIQUE (Overlay_ID, Owner_ID) ON 
                CONFLICT IGNORE )''')

                connection.commit()
            except Exception as err:
                msg = 'SQLite DBHandler error; failed to create database.\n'\
                      'Error was: %(msg)s' % {'msg': err}
                self.output.error(msg)

                raise err


    def read_db(self, path, text=None):
        '''
        Read the overlay definitions from the database and generate overlays.
        '''
        cursor = None
        overlay_id = None
        overlay = {}

        with self.__connect__(path) as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT Overlay_ID, Name, Priority, Status, 
            Quality, Homepage, IRC, License FROM Overlay''')
            overlays_info = cursor.fetchall()
            connection.commit()

            for overlay_info in overlays_info:
                overlay = {}
                overlay_id = overlay_info[0]
                overlay['name'] = overlay_info[1]

                cursor.execute('''SELECT URL, Type, Branch FROM Overlay_Source 
                JOIN Overlay USING (Overlay_ID) JOIN Source USING (Source_ID) 
                WHERE Overlay_ID = ?''', (overlay_id,))
                overlay['source'] = cursor.fetchall()

                cursor.execute('''SELECT Owner_Name, Owner_Email FROM 
                Overlay_Owner JOIN Overlay USING (Overlay_ID) JOIN Owner USING 
                (Owner_ID) WHERE Overlay_ID = ?''', (overlay_id,))
                owner_info = cursor.fetchall()

                if len(owner_info):
                    owner_info = owner_info[0]
                    overlay['owner_name'] = owner_info[0]
                    overlay['owner_email'] = owner_info[1]

                cursor.execute('''SELECT Description FROM Description JOIN 
                Overlay USING (Overlay_ID) WHERE Overlay_ID = ?''',
                (overlay_id,))
                overlay['description'] = cursor.fetchall()[0]

                overlay['status'] = overlay_info[3]
                overlay['quality'] = overlay_info[4]
                overlay['priority'] = overlay_info[2]

                if overlay_info[7]:
                    overlay['license'] = overlay_info[7]
                else:
                    overlay['license'] = None

                overlay['homepage'] = overlay_info[5]
                overlay['IRC'] = overlay_info[6]

                cursor.execute('''SELECT Feed FROM Feed JOIN Overlay USING 
                (Overlay_ID) WHERE Overlay_ID = ?''', (overlay_id,))
                overlay['feed'] = cursor.fetchall()

                if len(overlay['feed']):
                    overlay['feed'] = overlay['feed'][0]

                self.overlays[overlay_info[1]] = Overlay(self.config,
                                                         ovl_dict=overlay,
                                                         ignore=self.ignore)


    def add_new(self, document=None, origin=None):
        '''
        Reads in provided sqlite text and generates overlays to populate
        database.
        '''
        if not document:
            msg = 'SQLite DBHandler - add_new() failed: can\'t add '\
                  'non-existent overlay(s).\nOrigin: %(path)s'\
                  % {'path': origin}
            self.output.warn(msg)

            return False

        return True


    def add_ovl(self, overlay, connection):
        '''
        Adds an overlay to the database.
        '''
        overlay_id = None
        owner_id = None
        source_ids = []
        cursor = None

        cursor = connection.cursor()
        cursor.execute('''INSERT INTO Overlay ( Name, Priority, Status, 
        Quality, Homepage, IRC, License ) VALUES ( ?, ?, ?, ?, ?, ?, ? )''',
        (overlay.name, overlay.priority, overlay.status, overlay.quality,
        overlay.homepage, overlay.irc, overlay.license,))
        connection.commit()

        cursor.execute('''SELECT Overlay_ID FROM Overlay WHERE Name = ?''',
        (overlay.name,))
        overlay_id = cursor.fetchone()[0]

        cursor.execute('''INSERT INTO Owner ( Owner_Name, Owner_Email ) 
        VALUES ( ?, ? )''', (overlay.owner_name, overlay.owner_email,))
        connection.commit()

        cursor.execute('''SELECT Owner_ID from Owner WHERE Owner_Name = ?;''',
        (overlay.owner_name,))
        owner_id = cursor.fetchone()[0]

        for source in overlay.sources:
            cursor.execute('''INSERT INTO Source ( Type, Branch, URL )
            VALUES ( ?, ?, ? )''', (source.type_key, source.branch,
            source.src,))
            connection.commit()
            cursor.execute('''SELECT Source_ID FROM Source WHERE URL = ?;''',
            (source.src,))
            source_ids.append(cursor.fetchone()[0])

        for description in overlay.descriptions:
            cursor.execute('''INSERT INTO Description ( Overlay_ID, 
            Description ) VALUES ( ?, ? )''', (overlay_id, description,))

        for feed in overlay.feeds:
            cursor.execute('''INSERT INTO Feed ( Overlay_ID, Feed ) VALUES ( ?,
             ? )''', (overlay_id, feed,))

        cursor.execute('''INSERT INTO Overlay_Owner ( Overlay_ID, Owner_ID ) 
        VALUES ( ?, ? )''', (overlay_id, owner_id,))

        for source_id in source_ids:
            cursor.execute('''INSERT INTO Overlay_Source ( Overlay_ID, 
            Source_ID ) VALUES ( ?, ? )''', (overlay_id, source_id,))

        connection.commit()


    def remove(self, overlay, path):
        '''
        Remove an overlay from the database.
        '''
        cursor = None
        overlay_id = 0
        owner_id = 0
        source_ids = []

        with self.__connect__(path) as connection:
            cursor = connection.cursor()
            
            cursor.execute('''SELECT Overlay_ID FROM Overlay WHERE Name = 
            ?''', (overlay.name,))
            overlay_id = cursor.fetchone()[0]

            cursor.execute('''SELECT Owner_ID FROM Overlay_Owner WHERE 
            Overlay_ID = ?''', (overlay_id,))
            owner_id = cursor.fetchone()[0]

            cursor.execute('''SELECT Source_ID FROM Overlay_Source WHERE 
            Overlay_ID = ?''', (overlay_id,))
            source_ids = cursor.fetchall()[0]

            cursor.execute('''DELETE FROM Feed WHERE Overlay_ID = ?''',
            (overlay_id,))
            cursor.execute('''DELETE FROM Description WHERE Overlay_ID = ?''',
            (overlay_id,))
            cursor.execute('''DELETE FROM Overlay_Source WHERE Overlay_ID = 
            ?''', (overlay_id,))
            cursor.execute('''DELETE FROM Overlay_Owner WHERE Overlay_ID = 
            ?''', (overlay_id,))

            for source_id in source_ids:
               cursor.execute('''DELETE FROM Source WHERE Source_ID = ?''', 
               (source_id,))

            cursor.execute('''DELETE FROM Owner WHERE Owner_ID = ?''',
            (owner_id,))
            cursor.execute('''DELETE FROM Overlay WHERE Overlay_ID = ?''',
            (overlay_id,))

            connection.commit()

        if overlay.name in self.overlays:
            del self.overlays[overlay.name]


    def write(self, path):
        '''
        Write the list of overlays to the database.
        '''
        try:
            with self.__connect__(path) as connection:
                for overlay in self.overlays:
                    self.add_ovl(self.overlays[overlay], connection)
        except Exception as err:
            msg = 'Failed to write to overlays database: %(path)s\nError was'\
                  ': %(err)s' % {'path': path, 'err': err}
            self.output.error(msg)
            raise err
