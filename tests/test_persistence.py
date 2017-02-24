"""
Test the persistence module
"""

import unittest
import os
from unittest_data_provider import data_provider
import fixtures
import context
from persistence import LogPersistence

class TestPersistence(unittest.TestCase):

    creation_provider = lambda: (
        ('test_database.db',),
        ('~/test_database.db',)
    )

    @data_provider(creation_provider)
    def test_connect(self, path):
        expanded = os.path.expanduser(path)
        # Before continue, make sure file does not exist already, otherwise we would overwrite it
        self.assertFalse(os.path.isfile(expanded), 'File does already exist. Aborting.')

        instance = LogPersistence(path)
        self.assertIsNotNone(instance)

        instance.connect()
        self.assertIsNotNone(instance.conn)

        # Remove the file now
        os.remove(expanded)


if __name__ == '__main__':
    unittest.main()