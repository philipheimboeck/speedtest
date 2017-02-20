"""
Persistence for fetching and saving speedtests
"""

import sqlite3
from datetime import datetime, timedelta

class LogPersistence(object):
    """Fetches and saves data from/to the sqlite database"""

    def __init__(self, database):
        """
        Constructor
        :param database the database to read/write from/to
        """
        self.database = database
        self.conn = None

    def __enter__(self):
        """Establish a connection"""
        self.conn = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)
        self.__create()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the connection"""
        self.conn.close()

    def __create(self):
        """
        Create the table if not already existing
        """
        cursor = self.conn.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS speedlogs ' + \
            '(id INTEGER primary key, measure_dt TIMESTAMP, ping REAL, download REAL, upload REAL)'
        cursor.execute(sql)
        self.conn.commit()

    def fetch(self, daterange=(datetime.now() - timedelta(1), datetime.now())):
        """
        Fetches data in a specified period
        :param daterange default period is today until tomorrow
        """
        cursor = self.conn.cursor()
        sql = 'SELECT measure_dt, ping, download, upload FROM speedlogs ' + \
            ' WHERE measure_dt BETWEEN ? AND ?'
        cursor.execute(sql, daterange)
        return cursor.fetchall()

    def fetch_last(self, type):
        """
        Fetches the last entry
        """
        cursor = self.conn.cursor()
        sql = 'SELECT {} FROM speedlogs ORDER BY measure_dt DESC LIMIT 1'.format(type)
        cursor.execute(sql)
        return cursor.fetchone()


    def save(self, values):
        """
        Persist values
        """
        cursor = self.conn.cursor()
        params = (values['measure_dt'], values['ping'], values['download'], values['upload'])
        sql = 'INSERT INTO speedlogs (measure_dt, ping, download, upload) VALUES (?, ?, ?, ?)'
        cursor.execute(sql, params)
        self.conn.commit()
