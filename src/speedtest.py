#!/usr/bin/env python

"""
Executable that does a speedtest and saves it to the database
"""

import sys
from app import App, measure

if len(sys.argv) > 1:
    kernel = App(sys.argv[1])
else:
    kernel = App()

kernel.boot()
measure.run_speedtest()
