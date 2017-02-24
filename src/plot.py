#!/usr/bin/env python

"""
Executable that fetches the last speedtests and plots them
"""

from datetime import datetime, timedelta
import matplotlib

# Force matlib to not use any Xwindows backend
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from app import App, persistence

kernel = App()
kernel.boot()

with persistence.LogPersistence(kernel.config['database']) as persistence:
    # Fetch the data
    START = datetime.now() - timedelta(60)
    DATA = persistence.fetch((START, datetime.now()))

    # Convert values to array
    PLOT_VALUES = {'date': [], 'download': [], 'upload': [], 'ping': []}
    for item in DATA:
        PLOT_VALUES['date'].append(item[0])
        PLOT_VALUES['ping'].append(item[1])
        PLOT_VALUES['download'].append(item[2])
        PLOT_VALUES['upload'].append(item[3])

    FIG = plt.figure()
    #ax1 = fig.add_subplot(111)
    #ax1.plot(datetimes, data['ping'], color='r', label='Ping')
    #leg = ax1.legend()

    AX1 = FIG.add_subplot(111)
    AX1.plot(PLOT_VALUES['date'], PLOT_VALUES['download'], color='b', label='Download')
    leg = AX1.legend()

    #plt.show()
    #loc = matplotlib.ticker.MultipleLocator(base=.5)
    #ax2.xaxis.set_major_locator(loc)
    plt.savefig('plot.png')
