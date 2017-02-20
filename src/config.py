"""
Read configuration file and return it
"""

import json

def load_config():
    """
    Read configuration and return it
    """
    with open('config.json') as config_file:
        data = json.load(config_file)
    return data
