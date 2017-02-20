"""
Read configuration file and return it
"""

import json

def load_config(config_path='config.json'):
    """
    Read configuration and return it
    """
    with open(config_path) as config_file:
        data = json.load(config_file)
    return data
