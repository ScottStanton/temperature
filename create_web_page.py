#!/usr/bin/python3
#
# This software is covered by The Unlicense license
#
# Created by ScottStanton
# https://github.com/ScottStanton/temperature

### Change these variables to match your environment:
datadir='/home/pi/temp_sensor_data/'
#htmldir = '/usr/share/caddy/'
htmldir = '/home/pi/git/temperature/'

import argparse
import csv, math, requests, sys
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('axes',edgecolor='#DDDDDD')
import numpy as np
import matplotlib.pyplot as plt
from tenacity import *
import datetime

# Initialize required variables
degree_sign = u'\N{DEGREE SIGN}'
global dataarray
global dataarraylength
#dataarray = np.array([[ "datetime", "temperature", "pressure", "humidity" ]])
#dataarraylength = int("1")

parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbose', action='store_true',
       help="Show debugging messages on the command line")

args = parser.parse_args()

def current_date_time(flag):
    # Get today's date and current time
    # pass 'hm' if minutes are needed
    # pass 'hms' if seconds are needed
    debug_print(f'current_date_time::flag: {flag}')
    now = datetime.datetime.now()
    d_string = now.strftime("%Y-%m-%d")
    if flag == "hm":
       t_string = now.strftime("%H:%M")
    if flag == "hms":
       t_string = now.strftime("%H:%M:%S")
    return d_string, t_string
## End of function


def debug_print(string):
    # Add print statement here if -v is set.
    if args.verbose:
        now = datetime.datetime.now()
        rightnow = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f'DEBUG: {rightnow} - {string}')
## End of function


def roundup(x, y):
    return x if x % y == 0 else x + y - x % y
## End of function


def rounddown(x, y):
    return x if x % y == 0 else x - x % y
## End of function


def date_days_ago(daysint):
    # Get the date from 'daysint' days ago.
    # This is helpful on the first days of the month.
    # Use 0 to get today
    debug_print(f'date_days_ago::daysint: {daysint}')
    daymath = datetime.timedelta(days=daysint)
    day = datetime.date.today() - daymath
    debug_print(f'date_days_ago::returning date {day}')
    return str(day)
## End of function


def create_graph(datatype, xarray, yarray, sigfig):
    global dataarraylength
    picture=f'{htmldir}{datatype.replace(" ", "")}.png' 
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(15,3))
    fig.patch.set_facecolor("#020202")
    width = .75
    nmax = np.amax(yarray)
    nmin = np.amin(yarray)
    miny = rounddown(nmin, sigfig)
    maxy = roundup(nmax, sigfig)
    plt.plot(np.arange(0,dataarraylength,1),yarray)
    xtickarr = np.array([[ 0, 0 ]])
    for x in np.arange(0,dataarraylength,6):
        xtickarr = np.append(xtickarr, [[ x , xarray[x] ]], axis=0)

    xtickarr = np.delete(xtickarr, 0,axis = 0)
    xticknum, xticklabel = xtickarr.T
    xticknum = xticknum.astype(int)
    #print(xtickarr)
    plt.xticks(xticknum, xticklabel, rotation = 45)
    plt.xlabel('Time')
    plt.title(datatype)
    plt.savefig(picture, bbox_inches="tight")
## End of function
 

def insertgraph(datatype):
    return f'<p><center><img src={datatype.replace(" ", "")}.png alt=graph width=90%></center>'
## End of function


def read_csv_file(filename):
    # Read the date/time stamp, temperature, pressure, and humitidy data from a csv file and put it in a global array.
    global dataarray
    global dataarraylength
    debug_print(f'read_csv_file::filename: {filename}')
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file,['dt','t','p','h'])
        for filerow in csv_reader:
            dataarray = np.append(dataarray, [[ filerow["dt"], filerow["t"], filerow["p"], filerow["h"] ]],axis = 0)
            dataarraylength += 1
            #debug_print(f'{filerow["dt"]} - {filerow["t"]}F - {filerow["p"]} inHG - {filerow["h"]}%')
        debug_print(f'read_csv_file::dataarraylength: {dataarraylength}')
## End of function

def trim_top_of_array(nowhour, nowmin):
    global dataarray
    global dataarraylength
    for hour in range(0,nowhour , 1):
        for min in range(0, 60, 10):
            #print(f'{hour}:{min}')
            dataarray = np.delete(dataarray, 1,axis = 0)
            dataarraylength -= 1
    for min in range(0, nowmin + 10, 10):
        #print(f'{nowhour}:{min}')
        dataarray = np.delete(dataarray, 1,axis = 0)
        dataarraylength -= 1
    dataarray = np.delete(dataarray, 0,axis = 0)
    dataarraylength -= 1
## End of function

def trim_array_for_twentyfour_hours():
    # Set the global variables
    debug_print(f'trim_array_for_twentyfour_hours::Function entered')
    global dataarray
    global dataarraylength
    today, now = current_date_time('hm')   # Get today's date and current time
    now = now[:-1] + '0'                   # truncate time to the last ten minute mark
    debug_print(f'trim_array_for_twentyfour_hours: now: {now}')

    yesterday = date_days_ago(1)           # Get yesterday's date
    debug_print(f'trim_array_for_twentyfour_hours: yesterday: {yesterday}')
    yesterdayfile = datadir + yesterday + '.csv'        # Get yesterday's filename
    debug_print(f'trim_array_for_twentyfour_hours: yesterdayfile: {yesterdayfile}')
    read_csv_file(yesterdayfile)                        # Read data from yesterday's file

    todayfile = datadir + today + '.csv'                # Get today's filename
    debug_print(f'trim_array_for_twentyfour_hours: todayfile: {todayfile}')
    read_csv_file(todayfile)                            #Read data from today's file
    debug_print(f'trim_array_for_twentyfour_hours::Data read from files')

    nowhour = int(now.split(':')[0])
    nowmin = int(now.split(':')[1])
    trim_top_of_array(nowhour, nowmin)

    dt, temp, pres, humi = dataarray.T
    t = temp.astype(float)
    p = pres.astype(float)
    h = humi.astype(float)
    return dt, t, p, h
## End of function


def trim_array_for_seven_days():
    # Set the global variables
    debug_print(f'trim_array_for_seven_days::Function entered')
    global dataarray
    global dataarraylength
    today, now = current_date_time('hm')   # Get today's date and current time
    now = now[:-1] + '0'                   # truncate time to the last ten minute mark
    debug_print(f'trim_array_for_seven_days: now: {now}')

    yesterday = date_days_ago(1)           # Get yesterday's date
    debug_print(f'trim_array_for_seven_days: yesterday: {yesterday}')
    yesterdayfile = datadir + yesterday + '.csv'        # Get yesterday's filename
    debug_print(f'trim_array_for_seven_days: yesterdayfile: {yesterdayfile}')
    read_csv_file(yesterdayfile)                        # Read data from yesterday's file
    todayfile = datadir + today + '.csv'                # Get today's filename
    debug_print(f'trim_array_for_seven_days: todayfile: {todayfile}')
    read_csv_file(todayfile)                            #Read data from today's file
    debug_print(f'trim_array_for_seven_days::Data read from files')

    nowhour = int(now.split(':')[0])
    nowmin = int(now.split(':')[1])
    trim_top_of_array(nowhour, nowmin)

    dt, temp, pres, humi = dataarray.T
    t = temp.astype(float)
    p = pres.astype(float)
    h = humi.astype(float)
    return dt, t, p, h
## End of function


def print_current_html():
    debug_print(f'print_current_html::Function entered')
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
<meta http-equiv="refresh" content="60">
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

openFile = open(f'{htmldir}index.html','w')
openFile.write(hheader)
openFile.write(print_current_html())

dataarray = np.array([[ "datetime", "temperature", "pressure", "humidity" ]])
dataarraylength = int("1")

adatetime, at, ap, ah = trim_array_for_twentyfour_hours()
create_graph('24 Hr Temperature', adatetime, at, 1)
openFile.write(insertgraph('24 Hr Temperature'))
create_graph('24 Hr Pressure', adatetime, ap, 1)
openFile.write(insertgraph('24 Hr Pressure'))
create_graph('24 Hr Humidity', adatetime, ah, 1)
openFile.write(insertgraph('24 Hr Humidity'))

dataarray = np.array([[ "datetime", "temperature", "pressure", "humidity" ]])
dataarraylength = int("1")


openFile.write(hfooter)
openFile.close()

