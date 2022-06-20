#!/usr/bin/python3
#
# This software is covered by The Unlicense license
#

### Change these variables to match your environment:
datadir='/home/pi/temp_sensor_data/'
htmlDir = '/home/pi/git/temperature/'

import argparse
import csv, math, requests, sys
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('axes',edgecolor='#DDDDDD')
import numpy as np
import matplotlib.pyplot as plt
from tenacity import *
import datetime

degree_sign = u'\N{DEGREE SIGN}'
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
## End of function

def debug_print(string):
    # Add print statement here is -v is set.
    if args.verbose:
        today, now = current_date_time('hms')
        print(f'DEBUG: {today} {now} - {string}')
## End of function

def date_days_ago(daysint):
    debug_print(f'Doing date_days_ago({daysint}) math')
    daymath = datetime.timedelta(days=daysint)
    day = datetime.date.today() - daymath
    debug_print(str(daysint) + ' days ago it was ' + str(day))
    return str(day)
## End of function


def create_graph(datatype):
    picture='f{htmlDir}{datatype}.png' 
#    plt.style.use('dark_background')
#    fig = plt.figure(figsize=(15,3))
#    fig.patch.set_facecolor("#020202")
#    width = .75
#    maxmaxy = roundup(max(maxy))

## End of function

def read_csv_file(filename):
    global dataarray
    global dataarraylength
    debug_print(f'read_csv_file: filename : {filename}')
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file,['dt','t','p','h'])
        debug_print(csv_reader.fieldnames)
        for filerow in csv_reader:
            dataarray = np.append(dataarray, [[ filerow["dt"], filerow["t"], filerow["p"], filerow["h"] ]],axis = 0)
            dataarraylength += 1
            #debug_print(f'{filerow["dt"]} - {filerow["t"]}F - {filerow["p"]} inHG - {filerow["h"]}%')
            #print(dataarray)
        debug_print(f'read_csv_file: dataarraylength: {dataarraylength}')
## End of function

def trim_array_for_twentyfour_hours():
    # Set the global variables
    global dataarray
    global dataarraylength
    today, now = current_date_time('hm')   # Get today's date and current time
    now = now[:-1] + '0'                   # truncate time to the last ten minute mark
    yesterday = date_days_ago(1)           # Get yesterday's date
    debug_print(f'trim_array_for_twentyfour_hours: yesterday: {yesterday}')
    yesterdayfile = datadir + yesterday + '.csv'        # Get yesterday's filename
    debug_print(f'trim_array_for_twentyfour_hours: yesterdayfile: {yesterdayfile}')
    read_csv_file(yesterdayfile)                        # Read data from yesterday's file
    todayfile = datadir + today + '.csv'                # Get today's filename
    debug_print(f'trim_array_for_twentyfour_hours: todayfile: {todayfile}')
    read_csv_file(todayfile)                            Read data from today's file

    #print(dataarray)
    print(dataarray[0])
    print(dataarray[1])
    print(dataarray[dataarraylength - 1 ])

## End of function

def print_current_html():
    thisday = date_days_ago(0)
    filename = datadir + thisday + '.csv'
    with open(filename, 'r') as f:
        last_line = f.readlines()[-1]
        tablehtml = '''<table class="center">
  <tr>
  <tr>
    <th>Date/time</th>
    <th>Temperature</th>
    <th>Pressure</th>
    <th>Humidity</th>
  </tr>        
  <tr>
    <td>{0}</td>
    <td>{1}{4}F</td>
    <td>{2} inHG</td>
    <td>{3}%</td>
  </tr>        
</table>'''
        thestring = tablehtml.format(last_line.split(',')[0],last_line.split(',')[1],last_line.split(',')[2],last_line.split(',')[3],degree_sign)
    return thestring
## End of function


hheader = '''<html>
<head>
<title>Temperature Pressure Humidity</title>
<meta http-equiv="refresh" content="300">
<style type="text/css">
body,html {
  height: 100%;
  padding: 0;
  margin: 0;
  color: #E0E0E0;
  background: #020202;
}
table, td, th {
  border: 1px solid black;
  text-align: center;
  padding: 10px;
}

table {
  font-size: 1.7em;
  border-collapse: collapse;
  width: 60%;
}
table.center {
  margin-left: auto; 
  margin-right: auto;
}
</style>
</head>
<body>
\n'''

hfooter = '</body></html>'

#for datatype in ['temp', 'pressure', 'humidity']:
    
trim_array_for_twentyfour_hours()

#for i in range(2, -1, -1):
    #thisday = date_days_ago(i)
    #filename = datadir + thisday + '.csv'
    #print(filename)
    #read_csv_file(filename)

#print(str(len(dataarray)))

openFile = open(f'{htmlDir}index.html','w')
openFile.write(hheader)
openFile.write(print_current_html())
openFile.write(hfooter)
openFile.close()


