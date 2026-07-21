#!/usr/bin/env python3

import sqlite3
import json
from .scanner import Data
import subprocess

class Registry:
    
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.conn = None
        scanner = Data()
        self.apps = scanner.app_data()
        self.cursor = None

    def initialize(self):
        self.conn = sqlite3.connect(self.dbfile)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                categories TEXT,
                command TEXT,
                TERMINAL INTEGER
                )
                """)

    def add(self):

        self.cursor.execute("""SELECT 1 FROM applications LIMIT 1""")
        row = self.cursor.fetchone()
        
        if row is None:
            for app in self.apps:
                str_command = json.dumps(app["command"])
                self.cursor.execute("""
                INSERT INTO applications(name, categories, command, terminal)
                VALUES(?, ?, ?, ?)
                """,
                                    (
                                    app["name"],
                                    app["categories"],
                                    str_command,
                                    app["terminal"]
                                    )
                                    )
        else:
            return

    def search_name(self, argument):
        
        self.cursor.execute("""
        SELECT *
        FROM applications
        WHERE name LIKE ?
        LIMIT 1
        """, (f"%{argument}%",)
                       )

        row = self.cursor.fetchone()

        return row

    def search_category(self, argument):

        CATEGORY_MAP = {
            "browser": "WebBrowser",
            "terminal": "TerminalEmulator",
            "editor": "TextEditor",
            "ide": "Development",
            "music": "Player",
            "video": "AudioVideo",
            "file manager": "FileManager",
            "settings": "Settings",
        }

        self.cursor.execute("""
        SELECT *
        FROM applications
        WHERE categories LIKE ?
        """, (f"%{CATEGORY_MAP.get(argument)}%",)
                            )

        row = self.cursor.fetchall()

        return row

    def sync(self):
        
        self.cursor.execute("""SELECT * FROM applications""")
        stored_apps = self.cursor.fetchall()

        database_apps = []
        for stored_app in stored_apps:
            command = json.loads(stored_app[3])
            terminal = bool(stored_app[4])
            database_app = {
                    "name": stored_app[1],
                    "categories": stored_app[2],
                    "command": command,
                    "terminal": terminal
                    }
            database_apps.append(database_app)

        # From scanner's data POV.

        for scanned_app in self.apps:
            str_command = json.dumps(scanned_app["command"])
            
            db_found = False
            
            for db_app in database_apps:
                if db_app["name"] == scanned_app["name"]:
                    db_found = True
                    if ( db_app["categories"] != scanned_app["categories"] or db_app["command"] != scanned_app["command"] or db_app["terminal"] != scanned_app["terminal"] ):
                        self.cursor.execute("""
                        UPDATE applications
                        SET categories = ?, command = ?, terminal = ?
                        WHERE name = ?
                        """,
                                            (
                                                scanned_app["categories"],
                                                str_command,
                                                scanned_app["terminal"],
                                                db_app["name"]
                                                ))

            if db_found == False:
                self.cursor.execute("""
                INSERT INTO applications(name, categories, command, terminal)
                VALUES (?, ?, ?, ?)
                """,
                                    (
                                        scanned_app["name"],
                                        scanned_app["categories"],
                                        str_command,
                                        scanned_app["terminal"]
                                        )
                                    )

        # From Database' data POV.

        for db_app in database_apps:
            scan_found = False
            for scanned_app in self.apps:
                if scanned_app["name"] == db_app["name"]:
                    scan_found = True
                    break
            if scan_found == False:
                self.cursor.execute("""
                                    DELETE FROM applications
                                    WHERE name = ?
                                    """,
                                    (
                                        db_app["name"],
                                        )
                                    )

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    
    registry = Registry("applications.db")

    registry.initialize()
    registry.add()

    registry.sync()
    registry.commit()
    print("Search: ", end='')
    app_search = input("")
    result = registry.search_name(app_search)
    print(result)

    print("Search by Category: ", end='')
    category_search = input("")
    result = registry.search_category(category_search)
    print(result)

    registry.close()
