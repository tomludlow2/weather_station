#This is a test service
from time import sleep
import logging

try:
	i = 0
	while True:
		i += 1
		print( "Hello World")
		print( "i = " + str(i))
		sleep(20)

except KeyboardInterrupt:
	print("Stopping...")
	logging.info("Stopping...")