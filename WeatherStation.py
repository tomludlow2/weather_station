import os
import glob
import time
import math
from gpiozero import Button
from gpiozero import MCP3008
from gpiozero import LED


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


WIND_SPEED_BUTTON = 21
RADIUS_CM = 9.0
CLICKS_PER_ROTATION = 2.0
CIRCUMFERENCE_CM = (2*math.pi*RADIUS_CM)
CORRECTION_FACTOR = 2.4 / (18*math.pi*60*60/100/1000)

RAIN_BUTTON = 23
RAIN_CONST = 0.2794

WIND_ANGLES_DICT = {}
WIND_ANGLES_DICT[3.0] = 0
WIND_ANGLES_DICT[2.9] = 22.5
WIND_ANGLES_DICT[2.8] = 22.5
WIND_ANGLES_DICT[3.2] = 45
WIND_ANGLES_DICT[2.1] = 67.5
WIND_ANGLES_DICT[2.0] = 67.5
WIND_ANGLES_DICT[2.2] = 90
WIND_ANGLES_DICT[2.3] = 90
WIND_ANGLES_DICT[1.0] = 112.5
WIND_ANGLES_DICT[0.9] = 112.5
WIND_ANGLES_DICT[1.1] = 135
WIND_ANGLES_DICT[1.3] = 135
WIND_ANGLES_DICT[1.2] = 135
WIND_ANGLES_DICT[0.6] = 157.5
WIND_ANGLES_DICT[0.7] = 157.5
WIND_ANGLES_DICT[0.8] = 180
WIND_ANGLES_DICT[0.5] = 202.5
WIND_ANGLES_DICT[0.3] = 225
WIND_ANGLES_DICT[0.4] = 225
WIND_ANGLES_DICT[1.6] = 247.5
WIND_ANGLES_DICT[1.7] = 270
WIND_ANGLES_DICT[1.5] = 292.5
WIND_ANGLES_DICT[2.7] = 315
WIND_ANGLES_DICT[2.6] = 315
WIND_ANGLES_DICT[2.5] = 337.5


GREEN_LED_PIN = 19
WHITE_LED_PIN = 26
YELLOW_LED_PIN = 13 

class WeatherStation:
    def __init__(self):
        print( "Initiating Weather Station Class" )
        global WIND_SPEED_BUTTON, RAIN_BUTTON
        self.wind_speed_sensor = Button(WIND_SPEED_BUTTON)
        self.wind_count = 0
        self.wind_speed_sensor.when_pressed = self.tick_wind
        self.wind_started = time.time()

        self.rain_sensor = Button(RAIN_BUTTON)
        self.rain_count = 0
        self.rain_sensor.when_pressed = self.tick_rain
        self.rain_started = time.time()

        self.wind_vane_adc = MCP3008(channel=0)

        global GREEN_LED_PIN, YELLOW_LED_PIN, WHITE_LED_PIN
        self.green_led = LED(GREEN_LED_PIN)
        self.yellow_led = LED(YELLOW_LED_PIN)
        self.white_led = LED(WHITE_LED_PIN)

    #Define the function to read the raw input from DS18B2
    def read_deep_temp_raw(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        device_file = device_folder + '/w1_slave'
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_deep_temp(self):
        #This function opens the raw input, and waits until it gets a single reading
        lines = self.read_deep_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_deep_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            #temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c

    def read_wind(self, units="kmh", reset=False):
        #Assuming that the tick_wind listener is running:
        #time_now gets a current time
        #time_diff gets the difference between the time wind count was reset and now
        print("Reading Wind Speed")
        time_now = time.time()
        time_diff = time_now - self.wind_started
        ticks = self.wind_count
        print("Ticks:\t" + str(ticks) + "\tTime:\t" + str(round(time_diff,2) ) )
        global CIRCUMFERENCE_CM, CLICKS_PER_ROTATION, CORRECTION_FACTOR
        interval_distance_moved_cm = ticks / CLICKS_PER_ROTATION * CIRCUMFERENCE_CM
        interval_speed_cm = CORRECTION_FACTOR * interval_distance_moved_cm / time_diff
        print("Interval Speed " + str(interval_speed_cm) + " cm.seconds-1")

        return_speed = interval_speed_cm

        if( reset == True):
            self.reset_wind()

        #Now convert to units
        if( units == "kmh"):
            interval_speed_kmh = interval_speed_cm * 60 * 60 /100 /1000
            return_speed = interval_speed_kmh
        elif( units == "mph"):
            interval_speed_mph = interval_speed_kmh * 5 / 8
            return_speed = interval_speed_mph
        elif( units == "knots"):
            interval_speed_knots = interval_speed_mph / 1.151
            return_speed = interval_speed_knots
        elif( units == "cms" ):
            return_speed = interval_speed_cm
        else:
            return_speed = 0
            print("You supplied an invalid units value:  cms, kmh, mph, knots are accepted values")
        return return_speed

    def tick_wind(self):
        self.wind_count += 1

    def reset_wind(self):
        self.wind_count = 0
        self.wind_started = time.time()

    def read_rain(self, reset=False):
        #Assuming that the tick_rain listener is running:
        print("Reading Rain Count")
        time_now = time.time()
        time_diff = time_now - self.rain_started
        ticks = self.rain_count
        print("Ticks:\t" + str(ticks) + "\tTime:\t" + str(round(time_diff,2)))
        global RAIN_CONST
        print("Rainfall in that time: " + str(ticks*RAIN_CONST) + "mm")
        if(reset == True):
            self.reset_rain()
        return (ticks*RAIN_CONST)

    def tick_rain(self):
        self.rain_count += 1

    def reset_rain(self):
        self.rain_count = 0
        self.rain_started = time.time()


    def read_wind_direction(self):
        reading = round(self.wind_vane_adc.value*3.3,1)
        #print("Reading:\t" + str(reading))
        global WIND_ANGLES_DICT
        if( WIND_ANGLES_DICT.get(reading)):
            angle = WIND_ANGLES_DICT[reading]
            print("Angle:\t" + str(angle) + "deg")
            return True
        else:
            return False

    def read_wind_direction_const(self, count):
        i = 0
        while( i < count):
            reading = round(self.wind_vane_adc.value*3.3,1)
            print("Reading:\t" + str(reading))
            if( WIND_ANGLES_DICT.get(reading)):
                angle = WIND_ANGLES_DICT[reading]
                print("Angle:\t" + str(angle) + "deg")
            else:
                print("Angle:\tNull")
            i += 1
            time.sleep(0.3)


    def read_wind_direction_average(self, count):
        #This function will return a list of the "matched" angles taken from the weather station at intervals of 0.3 seconds over a count as specified in the function arguments
        i = 0
        directions = []
        while( i < count):
            reading = round(self.wind_vane_adc.value*3.3,1)
            #print("Reading:\t" + str(reading))
            if( WIND_ANGLES_DICT.get(reading)):
                angle = WIND_ANGLES_DICT[reading]
                directions.append(angle)
            i += 1
            time.sleep(0.3)        
        return directions

    def blink_led(self, count, led="all"):
        i = 0
        while( i < count ):
            if( led == "all" ):
                self.yellow_led.on()
                self.green_led.on()
                self.white_led.on()
                time.sleep(0.4)
                self.yellow_led.off()
                self.green_led.off()
                self.white_led.off()
                time.sleep(0.4)
                i += 1
            elif( led == "green" ):
                self.green_led.on()
                time.sleep(0.4)
                self.green_led.off()
                time.sleep(0.4)
                i += 1
            elif( led == "yellow" ):
                self.yellow_led.on()
                time.sleep(0.4)
                self.yellow_led.off()
                time.sleep(0.4)
                i += 1
            elif( led == "white" ):
                self.white_led.on()
                time.sleep(0.4)
                self.white_led.off()
                time.sleep(0.4)
                i += 1
            else:
                i = count
                print("Invalid LED specified, all, green, yellow, white allowed values")
        self.yellow_led.off()
        self.green_led.off()
        self.white_led.off()
