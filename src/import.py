#!/usr/bin/env python

"""
Import speedtest data from csv
"""

from datetime import datetime
import sys
import numpy as np
from persistence import LogPersistence


FILENAME = sys.argv[1]
DATA = np.genfromtxt(
    FILENAME,
    delimiter=',',
    skip_header=0,
    skip_footer=0,
    names=['date', 'time', 'zone', 'ping', 'download', 'upload'],
    dtype="S10,S5,S5,f8,f8,f8"
    )

with LogPersistence('speedtest.db') as persistence:
    for i in range(len(DATA['time'])):
        instance = {
            'measure_dt':
                datetime.strptime(DATA['date'][i] + ' ' + DATA['time'][i], "%Y-%m-%d %H:%M"),
            'ping': DATA['ping'][i],
            'download': DATA['download'][i] * 1000000,
            'upload': DATA['upload'][i] * 1000000,
        }

        print instance

        # Save to database
        persistence.save(instance)

