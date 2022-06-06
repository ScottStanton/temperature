#!/usr/bin/python3
#
# This software is covered by The Unlicense license
#

import argparse
import csv, math, requests, sys
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('axes',edgecolor='#DDDDDD')
import numpy as np
import matplotlib.pyplot as plt
from tenacity import *
from datetime import datetime

htmlFile = '/var/www/html/pihole.html'

parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbose', action='store_true',
       help="Show debugging messages on the command line")

args = parser.parse_args()

def current_date_time(flag):
    now = datetime.now()
    d_string = now.strftime("%Y-%m-%d")
    if flag == "hm":
       t_string = now.strftime("%H:%M")
    if flag == "hms":
       t_string = now.strftime("%H:%M:%S")
    return d_string, t_string
## End of function

def debug_print(string):
    # Add print statement here is -v is set.
    if args.verbose:
        today, now = current_date_time('hms')
        print(f'DEBUG: {today} {now} - {string}')
## End of function

def create_graph(datatype)
    picture='/var/www/html/{datatype}.png' 
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(15,3))
    fig.patch.set_facecolor("#020202")
    width = .75
    maxmaxy = roundup(max(maxy))

## End of function

def read_csv_file(filename)
    with open('employee_birthday.txt', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)


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

