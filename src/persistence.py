"""
Persistence for fetching and saving speedtests
"""

import sqlite3
import os
from datetime import datetime, timedelta

class LogPersistence(object):
    """Fetches and saves data from/to the sqlite database"""

    def __init__(self, database):
        """
        Constructor
        :param database the database to read/write from/to
        """
        # Expand path to allow ~ character
        self.database = os.path.expanduser(database)
        self.conn = None

    def __enter__(self):
        """Establish a connection and create the table if not existing"""
        self.connect()
        self.create()
        return self

    def connect(self):
        """Establish a connection"""
        self.conn = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the connection"""
        self.conn.close()

    def create(self):
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
        sql = 'SELECT {}, measure_dt FROM speedlogs ORDER BY measure_dt DESC LIMIT 1'.format(type)
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_stats(self, speed_type, daterange=(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), datetime.now())):
        """
        Fetches the Max, Min, Avg and Count of the given type in a specified period
        :param daterange default period is today (00:00 am until now)
        """
        cursor = self.conn.cursor()
        sql = 'Select max({0}), min({0}), avg({0}), count({0}) from speedlogs WHERE measure_dt BETWEEN ? AND ?'.format(speed_type)
        cursor.execute(sql, (daterange[0], daterange[1]))
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
