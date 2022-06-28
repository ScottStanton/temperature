# Temperature

Use BME280 to get the temperature, pressure and humidity meassurements and track them from a web page.


Using code from https://github.com/BoschSensortec/BME280_driver to gather the data from the sensor.

##get_and_store_temp.py 
* This captures the data from the sensor every 10 minutes and sstores it in a csv format in a file.
* optional --backup to scp the data to another server.  must have passwordless ssh setup for this to work.

##create_web_page.py
* This will create an index.html and 6 png files
* 3 of the png files are graphs for 24 hours of temperature, pressure and humidity
* The other 3 are for 7 day graphs of the same

##Usage:
* Both have a -v (--verbose) option that is more useful for debugging than for actual usage.
                        
