import pyspeedtest
import persistence
from datetime import datetime
import thread
from persistence import LogPersistence

CONFIG = None

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

def run_speedtest():
    """
    Execute the speedtest, save the result and return the result
    """
    with LogPersistence(CONFIG['database']) as database:

        # Speedtest
        print "Starting measurement..."
        speed = test_speed()

        database.save(speed)
        print speed
    return speed

def start_speedtest():
    """
    Do a speedtest in the background
    """
    thread.start_new_thread(run_speedtest)
    