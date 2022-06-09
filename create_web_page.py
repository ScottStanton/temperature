#!/usr/bin/python3
#
# This software is covered by The Unlicense license
#

### Change these variables to match your environment:
datadir='/home/pi/temp_sensor_data/'

import argparse
import csv, math, requests, sys
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('axes',edgecolor='#DDDDDD')
import numpy as np
import matplotlib.pyplot as plt
from tenacity import *
import datetime

htmlFile = '/var/www/html/temp.html'
global dataarray
dataarray = np.array([[ "datetime", "temperature", "pressure", "humidity" ]])
global dataarraylength
dataarraylength = int("1")

parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbose', action='store_true',
       help="Show debugging messages on the command line")

args = parser.parse_args()

def current_date_time(flag):
    now = datetime.datetime.now()
    d_string = now.strftime("%Y-%m-%d")
    if flag == "hm":
       t_string = now.strftime("%H:%M")
    if flag == "hms":
       t_string = now.strftime("%H:%M:%S")
    return d_string, t_string

def debug_print(string):
    # Add print statement here is -v is set.
    if args.verbose:
        today, now = current_date_time('hms')
        print(f'DEBUG: {today} {now} - {string}')

def date_days_ago(daysint):
    daymath = datetime.timedelta(days=daysint)
    day = datetime.date.today() - daymath
    debug_print(str(daysint) + ' days ago it was ' + str(day))
    return str(day)


def create_graph(datatype):
    picture='/var/www/html/{datatype}.png' 
#    plt.style.use('dark_background')
#    fig = plt.figure(figsize=(15,3))
#    fig.patch.set_facecolor("#020202")
#    width = .75
#    maxmaxy = roundup(max(maxy))

## End of function

def read_csv_file(filename):
    global dataarray
    global dataarraylength
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file,['dt','t','p','h'])
        print(csv_reader.fieldnames)
        for i in csv_reader:
            dataarray[dataarraylength] = [ i["dt"], i["t"], i["p"], i["h"] ]
            dataarraylength += 1
            debug_print(f'{i["dt"]} - {i["t"]}F - {i["p"]} inHG - {i["h"]}%')

hheader = '''<html>
<head>
<title>Temperature Pressure Humidity</title>
<meta http-equiv="refresh" content="600">
<style type="text/css">
body,html {
  height: 100%;
  padding: 0;
  margin: 0;
  color: #E0E0E0;
  background: #020202;
}
</style>
</head>
<body>
\n'''

hfooter = '</body></html>'

datatype='dummy'

#read_csv_file('/home/pi/temp_sensor_data/2022-06-05.csv')



for i in range(2, -1, -1):
    thisday = date_days_ago(i)
    filename = datadir + thisday + '.csv'
    print(filename)
    read_csv_file(filename)

print(str(len(dataarray)))
