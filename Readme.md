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

Run `plot.py` to plot the last 60 days.

![Example Plot](doc/images/example.png)

## Import CSV

Run `import.py filename.csv` to import your existing data into your database.
The CSV format to import is as follows:

```csv
date,time,timezone,ping,download (MBit/s),upload (MBit/s)
2017-02-19,18:45,CET,47.126,4.07,1.90
2017-02-19,19:00,CET,66.101,3.94,0.86
```

You might adapt the script to import your own files.

## Cronjob

To measure your speed all 15 minutes, add the following line to your crontab.

```
*/15 * * * * python /path/to/speedtest.py
```

