# Speedtest

## Installation

* Install pip packages

```
pip install -r requirements.txt
```

* Install python-tk

```
sudo apt install python-tk
```

## Measure the speed

Run `python speedtest.py` to measure the speed.
It will automatically create a sqlite database if not already given.

## Plot a diagram

Run `plot.py` to plot the last 10 days.

## Cronjob

To measure your speed all 15 minutes, add the following line to your crontab.

```
*/15 * * * * python /path/to/speedtest.py
```

