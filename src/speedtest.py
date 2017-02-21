#!/usr/bin/env python

"""
Executable that does a speedtest and saves it to the database
"""

import sys
import config
import measure

if len(sys.argv) > 1:
    CONFIG = config.load_config(sys.argv[1])
else:
    CONFIG = config.load_config()

SPEED = measure.run_speedtest(CONFIG)
print SPEED
