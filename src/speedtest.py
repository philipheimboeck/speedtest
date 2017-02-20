#!/usr/bin/env python

"""
Executable that does a speedtest and saves it to the database
"""

from datetime import datetime
from persistence import LogPersistence
import pyspeedtest
import config

CONFIG = config.load_config()

def test_speed():
    """
    Do a speedtest
    """
    speedtest = pyspeedtest.SpeedTest()
    return {
        'ping': speedtest.ping(),
        'download': speedtest.download(),
        'upload': speedtest.upload(),
        'measure_dt': datetime.now()
        }

with LogPersistence(CONFIG['database']) as persistence:

    # Speedtest
    SPEED = test_speed()
    print SPEED

    persistence.save(SPEED)
