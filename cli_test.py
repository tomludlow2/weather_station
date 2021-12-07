import WeatherStation as ws
import time

station = ws.WeatherStation()


#This section will collect wind speeds every 3 seconds, demonstrating how to reset the count
#time.sleep(3)
#print( station.read_wind("kmh", False) )
#time.sleep(3)
#print( station.read_wind("kmh", True) )
#time.sleep(3)
#print( station.read_wind("kmh", False) )


#This section will perform an averaging function
import statistics
wind_speeds = []
average_speed = 0
#In minutes - average period
AVERAGE_PERIOD = 0.5
wind_average_i = 0
while( wind_average_i < AVERAGE_PERIOD*60):
	time.sleep(5)
	speed = station.read_wind("kmh", True)
	print("Wind speed " + str(speed) + "kmh-1")
	wind_average_i += 5
	wind_speeds.append(speed)
	average_speed = statistics.mean(wind_speeds)
	

print("Completed!")
print("Max Speed:\t" + str(max(wind_speeds)))
print("Mean Speed:\t" + str(statistics.mean(wind_speeds)))
print("Min Speed:\t" + str(min(wind_speeds)))

#station.read_rain()
#time.sleep(120)
#station.read_rain()


#x = 0
#while( x < 10 ):
#	if( station.read_wind_direction() == True):
#		x += 1
#	time.sleep(0.1)

#station.read_wind_direction_const(100)

#directions = station.read_wind_direction_average(100)
#print (directions)

station.blink_led(1,"all")