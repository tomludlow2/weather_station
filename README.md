# weather_station
Tom's RPI Zero W Weather Station

## Credits
- I would not have been able to complete this project without help:
- [Rasberry Pi Foundation](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/2)
- [Pimoroni Libarary](https://learn.pimoroni.com/article/getting-started-with-bme680-breakout)
- [How to Solder](https://www.youtube.com/watch?v=6rmErwU5E-k&ab_channel=wermy)
- [W3 Python References](https://www.w3schools.com/python/python_reference.asp)

## Components:
(I am not affiliated with links, just for comparison and interest)
- [BME680 sensor (outdoor temperature,  humidity,  pressure,  and air quality)](https://shop.pimoroni.com/products/bme680-breakout?variant=12491552129107&currency=GBP)
- [SparkFun](https://www.sparkfun.com/products/15901) Anemometer
- SparkFun Rain Bucket
- SparkFun Wind Vane
- [DS18B20 thermometer](https://thepihut.com/blogs/raspberry-pi-tutorials/18095732-sensors-temperature-with-the-1-wire-interface-and-the-ds18b20)
- [MCP3008](https://thepihut.com/products/adafruit-mcp3008-8-channel-10-bit-adc-with-spi-interface) for analogue to digital conversion
- Raspberry Pi Zero W Model 1 (with headers)
- [Breakout board](https://www.amazon.co.uk/gp/product/B072R5L3QP/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)
- 16GB SanDisk Memory Card
- 2.4GHz WiFi connection
- [3x LEDs with resistors](https://osoyoo.com/2016/04/12/raspberry-pi-3-s/) for external communication
- [Photoresistor](https://osoyoo.com/2016/04/12/raspberry-pi-3-s/) (currently not used)
- [RJ11 breakout boards x3](https://thepihut.com/products/rj11-breakout-board)
- RJ45 cable
- Two outdoor enclosures
- ([One](https://www.ebay.co.uk/itm/393426797123?var=662256933227) contains RPi, Breakout Board, the ADC, and RJ11 breakout boards (and a custom RJ45 breakout) and ([One](https://www.toolstation.com/junction-box-ip55/p60297) contains the BME680 sensor, and houses the LEDs well as space for a 5V Fan)


## Installation
- See pictures for installation
- Required libraries:  os, glob, time, math, statistics
- Also: GPIOZERO
- Also: BME680 library (I use the [pimoroni lib](https://github.com/pimoroni/bme680-python))
- Also: (Optional) - my [weather_api](https://github.com/tomludlow2/weather_api)

## Usage (Python Class):
### Import and Inititate
- Import and create an instance of WeatherStation
```
import WeatherStation
station = WeatherStation.WeatherStation()
```
- It will automatically:
- Setup the LEDs
- Start counting wind speed
- Start counting rain

### Initiate BME sensor
```
station.init_bme_sensor(True|False)
```
Specify **True or False** for if you want to turn on the gas mode or not
- Turning on gas mode will heat the gas resistor module which will affect your temperature readings (from testing by around 2.5 Celsius but this was variable)
- You can turn it on (later) with ```station.bme_sensor_modify_gas(True|False)```

### Taking Readings
#### Rainfall
- Rainfall is recorded by counting ticks and recording the time the ticks started
- To read the rainfall:  ```read_rain(True|False)``` 
- Where **True|False** specifies if you would like to reset the count after reading (e.g. reading hourly then reset the timer)
- This will print out the rain ticks, time and then calculate rainfall using ```RAIN_CONST``` as a conversion from ticks to mm of rain
- It will return to rainfall in **mm**
- To Reset the rainfall count, you can call ```reset_rain()``` - but note you will lose the readings stored at that point

#### Wind Speed
- Wind speed is recorded by counting ticks and recording the time the ticks started
- To read the wind speed: ```read_wind(units, reset)```
- You can specify units: ```("kmh", "mph", "knots", "cms")```
- - Kilometeres per hour,    Miles per hour,   Knots,   Centimeters per second
- - Default is **kmh**
- You can also specify reset as **True|False** if you would like to reset the wind speed
- This will:
- - Print out the interval Ticks and Time since it was last reset
- - Print out the wind speed in your chosen units
- - Return the wind speed in your chosen units
- There are some assumptions for the calculation of windspeed, these are based on the equipement
- This example uses an anemoneter with reed switches, hence the need for:
- ```CLICKS_PER_ROTATION=2    CIRCUMFERENCE_CM=9.0,   CORRECTION_FACTOR```
- ```CORRECTION_FACTOR``` is calculated based on the fact there is some internal resistance in the sytem - see the Raspberry Pi Guide for more information
- To Reset the Wind Count, you can call ```reset_wind()``` - but note you will lose the readings stored at that point


#### Deep Temperature
- This is an **I2C** component
- Reading is simple:  ```read_deep_temp()```
- Reads in Celsius * *Farenheit is easy, just uncomment the Farenheit line* *

#### BME680 Sensor
- The below is an adaptation of the [Pimoroni Code](https://learn.pimoroni.com/article/getting-started-with-bme680-breakout)
- The BME sensor needs to be initated before this function can run (see **Initiation** above)
- ```read_bme_sensor```
- This function will:
- - Print out:  **Temperature** (Celsius), **Humidity** (Rel%) and **Pressure** (hPa)
- - If gas mode is on, it will then Take a reading every second until the difference between the last readings is within 1% and print these
- - Return a dictionary of ```{temperature, humidity, pressure, (resistance)}```

#### Wind Direction
- This sensor seems the most difficult to interpret
- Even following the Raspberry Pi Foundation Guide, it doesn't seem to be particularly accurate, however:
- ```read_wind_direction()```
- - This prints out the raw reading from the Analogue to Digital Converter (multiplied by input voltage * *3.3V* *
- - It will also print out the matching degrees from the ```WIND_ANGLES_DICT``` const. 
- - You can either manipulate this dictionary or dynamically correc this value for your setup
- - It will return the angle from this dictionary, of **False** if it doesn't match a value in the dict
- ```read_wind_direction_const(count)``` where **count** is the number of readings you wish to take
- - This will print out the angle of the wind vane (or * *Null* * every 0.3 seconds x your interval)
- ```read_wind_direction_average(count)``` where **count** is the number of samples you want
- - This will run for 0.3 seconds x your count
- - It will then return a list of angles that were matched during those counts e.g. ```[0,22.5,22.5,67.5,180,67.5...]``` 
- - **Note** that the number of values is unlikely to be your **count** as not all ADC values convert to a direction


#### Blink LED
- This just allows you to blink the LEDs on the side of the smaller enclosure
- ```blink_led(count, led(all|green|white|yellow))```
- On/Off Blinking of relevant LEDs x **count** x 0.4 secs on|off
