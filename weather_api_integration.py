import WeatherStation as ws
import time, statistics, json, sys

#Import the weather_api module
import sys
sys.path.append("/home/pi")
import weather_api.weather_api as api
a = api.API()

def collect_data_set(station, full_set = False, countdown=15):
	reading = {
		"time": time.time(),
		"active": "test"
	}
	deep_temp = station.read_deep_temp()
	reading["deep_temp"] = deep_temp
	if( full_set == True):
		station.init_bme_sensor(False)
		bme_readings = station.read_bme_sensor(True)
		reading = reading | bme_readings
		station.bme_sensor_modify_gas(True)

	i = 0
	wind_speeds = []
	while( i < countdown ):
		i += 1
		if( i % 5 == 0 ):		
			ws = station.read_wind("kmh",True,quiet=True)
			wind_speeds.append(ws)
		time.sleep(1)
	ws_average = round(statistics.mean(wind_speeds),2)
	ws_gust = round(max(wind_speeds),2)
	reading["ws_average"] = ws_average
	reading["ws_gust"] = ws_gust
	rainfall = station.read_rain(True)
	reading["rainfall"] = rainfall
	wd = station.read_wind_direction_average(30)
	if( len(wd) != 0 ):
		reading["wd_mode"] = statistics.mode(wd)
	if( full_set == True):
		new_bme_readings = station.read_bme_sensor(True)
		reading["resistance"] = round(new_bme_readings["resistance"])
	return(reading)


def process_data_dict(d):
	#Necessary to post-process to get the right format for the server
	readings = []
	if "deep_temp" in d:
		r = {"pond_temperature": d["deep_temp"]}
		readings.append(r)
	if "rainfall" in d:
		r = {"rainfall": d["rainfall"]}
		readings.append(r)
	if "ws_average" in d:
		r = {"wind_speed_average": d["ws_average"]}
		readings.append(r)
	if "ws_gust" in d:
		r = {"wind_speed_gust": d["ws_gust"]}
		readings.append(r)
	if "wd_mode" in d:
		r = {"wind_direction": d["wd_mode"]}
		readings.append(r)
	if "temperature" in d:
		r = {"bme680_temperature": d["temperature"]}
		readings.append(r)
	if "humidity" in d:
		r = {"bme680_humidity": d["humidity"]}
		readings.append(r)
	if "pressure" in d:
		r = {"bme680_pressure": d["pressure"]}
		readings.append(r)
	if "resistance" in d:
		r = {"bme680_air_quality": d["resistance"]}
		readings.append(r)
	#Processed
	print("Data has been post-processed")
	print( json.dumps(readings, indent=3))
	return readings



#Setup the weather station
station = ws.WeatherStation()

#Collect one set of data (This is for a single snapshot)
data = collect_data_set(station, True, (10*60))
print( json.dumps(data, indent=3))

#Now process the data
readings = process_data_dict(data)
a.send_multiple(readings)
