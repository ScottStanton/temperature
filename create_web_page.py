#!/usr/bin/python3
#
# This software is covered by The Unlicense license
#
# Created by ScottStanton
# https://github.com/ScottStanton/temperature

### Change these variables to match your environment:
datadir='/home/pi/temp_sensor_data/'
htmldir = '/usr/share/caddy/'

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
    
    # Find the min and max values for the Y axis of the graph
    nmax = np.amax(yarray)
    nmin = np.amin(yarray)
    miny = rounddown(nmin, sigfig)
    maxy = roundup(nmax, sigfig)

    # The number of labels on the bottom of the graph need to be vastly different
    # for 24 hour graph vs. 7 day graphs
    # tickdivide of 6 gives a label every hour
    # tickdivide of 36 give a label every 6 hours
    if dataarraylength < 300:
        tickdivide = 6
    else:
        tickdivide = 36

    plt.plot(np.arange(0,dataarraylength,1),yarray)
    
    # Create an array and fill it with count and with date/time labels for the X axis
    xtickarr = np.array([[ 0, 0 ]])
    for x in np.arange(0,dataarraylength,tickdivide):
        xtickarr = np.append(xtickarr, [[ x , xarray[x] ]], axis=0)

    xtickarr = np.delete(xtickarr, 0,axis = 0)  # delete the initial 0,0 row in the array
    xticknum, xticklabel = xtickarr.T           # transpose the table into 1 by X arrays
    xticknum = xticknum.astype(int)             # Make the numbers integer
    plt.xticks(xticknum, xticklabel, rotation = 45)  # rotate the label to make it easier to read
    plt.title(datatype)
    plt.savefig(picture, bbox_inches="tight")
    # bbox_inches="tight" makes the graph take up all the space instead of being padded
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


def get_array_for_days(numdays):
    # Set the global variables
    debug_print(f'trim_array_for_seven_days::Function entered')
    global dataarray
    global dataarraylength
    today, now = current_date_time('hm')   # Get today's date and current time
    now = now[:-1] + '0'                   # truncate time to the last ten minute mark
    debug_print(f'trim_array_for_seven_days: now: {now}')

    for i in range(numdays,-1,-1):
       thatday = date_days_ago(i)           # Get that day's date
       debug_print(f'trim_array_for_seven_days: thatday: {thatday}')
       thatdayfile = datadir + thatday + '.csv'        # Get that day's filename
       read_csv_file(thatdayfile)                      #Read data from today's file
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
        dts = last_line.split(',')[0]
        temp = float(last_line.split(',')[1])
        pres = float(last_line.split(',')[2])
        humi = float(last_line.split(',')[3])
        da = (( 29.92 - float(last_line.split(',')[2]) ) * 1000 ) + 147
        tablehtml = '''<table class="center">
  <tr>
  <tr>
    <th>Date/time</th>
    <th>Temperature</th>
    <th>Pressure</th>
    <th>Humidity</th>
    <th>Density Altitude</th>
  </tr>        
  <tr>
    <td>{0}</td>
    <td>{1:.1f}{4}F</td>
    <td>{2:.2f} inHG</td>
    <td>{3:.1f}%</td>
    <td>{5:.0f}ft</td>
  </tr>        
</table>'''
        thestring = tablehtml.format(dts,temp,pres,humi,degree_sign,da)
    return thestring
## End of function

# Create the header for the html page
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

##### Main Program #####

openFile = open(f'{htmldir}index.html','w')
openFile.write(hheader)
openFile.write(print_current_html())

dataarray = np.array([[ "datetime", "temperature", "pressure", "humidity" ]])
dataarraylength = int("1")

adatetime, at, ap, ah = get_array_for_days(1)
create_graph('24 Hr Temperature', adatetime, at, 1)
openFile.write(insertgraph('24 Hr Temperature'))
create_graph('24 Hr Pressure', adatetime, ap, 1)
openFile.write(insertgraph('24 Hr Pressure'))
create_graph('24 Hr Humidity', adatetime, ah, 1)
openFile.write(insertgraph('24 Hr Humidity'))

dataarray = np.array([[ "datetime", "temperature", "pressure", "humidity" ]])
dataarraylength = int("1")
debug_print(f'main::Cleared dataarray and dataarraylength for use in 7 day graphs')

adatetime, at, ap, ah = get_array_for_days(7)
create_graph('7 day Temperature', adatetime, at, 1)
openFile.write(insertgraph('7 day Temperature'))
create_graph('7 day Pressure', adatetime, ap, 1)
openFile.write(insertgraph('7 day Pressure'))
create_graph('7 day Humidity', adatetime, ah, 1)
openFile.write(insertgraph('7 day Humidity'))

openFile.write(hfooter)
openFile.close()

