import WeatherStation as ws
import time, statistics, json


def collect_data_set(station, full_set = False):
	#This function will get a full set of readings from the weather station
	#For that purpose we need to wait a period of time before we collect wind data
	#However we should collect the initial temperature from the box so that heating up the element doesn't have an effect

	print("Attempting to create Weather Station dataset")

	reading = {
		"time": time.time(),
		"active": "test"
	}

	#Take readings:
	#Deep temperature:
	deep_temp = station.read_deep_temp()

	print("Reading Deep Temperature: " + str(deep_temp))
	reading["deep_temp"] = deep_temp

	if( full_set == True):
		#Get box temperature, humidity, and pressure
		station.init_bme_sensor(False)
		bme_readings = station.read_bme_sensor(True)
		print( "BME Readings Taken t= " + str(bme_readings["temperature"]) + "\th= " + str(bme_readings["humidity"]) + "\tp= " + str(bme_readings["pressure"]))
		reading = reading | bme_readings

		#Set the gas mode on:
		station.bme_sensor_modify_gas(True)

	#Count Down (ideally 30? seconds)
	#Each 5 seconds, get the wind speed
	countdown = 15
	i = 0
	wind_speeds = []
	while( i < countdown ):
		i += 1
		if( i % 5 == 0 ):		
			ws = station.read_wind("kmh",True,quiet=True)
			wind_speeds.append(ws)
		time.sleep(1)
		printProgressBar(i, countdown, "Collecting Data", length=50)


	#Log Windspeeds:
	ws_average = round(statistics.mean(wind_speeds),2)
	ws_gust = round(max(wind_speeds),2)
	print("Wind Analysis: Mean= " + str(ws_average) + "kmh\tGust= " + str(ws_gust) + "kmh")
	reading["ws_average"] = ws_average
	reading["ws_gust"] = ws_gust

	#Get Rainfall
	rainfall = station.read_rain(True)
	reading["rainfall"] = rainfall
	print("Rainfall: " + str(rainfall) + "mm")

	#Get Wind Direction
	wd = station.read_wind_direction_average(30)
	if( len(wd) != 0 ):
		reading["wd_mode"] = statistics.mode(wd)
		print( "Wind Direction (mode): " + str(statistics.mode(wd)) )

	if( full_set == True):
		#Get air quality
		new_bme_readings = station.read_bme_sensor(True)
		print( "BME Readings Taken t= " + str(new_bme_readings["temperature"]) + "\th= " + str(new_bme_readings["humidity"]) + "\tp= " + str(new_bme_readings["pressure"]) + "\tAQ= " + str(new_bme_readings["resistance"]))
		reading["resistance"] = round(new_bme_readings["resistance"])

	#Completed
	print("Completed")
	return(reading)

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
	# Print New Line on Complete
	if iteration == total: 
		print()



try:
	station = ws.WeatherStation()
	r = collect_data_set(station)
	print( json.dumps(r, indent=3))
	r2 = collect_data_set(station, True)
	print( json.dumps(r2, indent=3))
except Exception as e:
	print( "There was an error" )
	print (e)
else:
	print( "Inside the else block" )
finally:
	print( "The function is finally finished" )