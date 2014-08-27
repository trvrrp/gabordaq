# test.py
#
# general use testing script

from serialcom import *
import time

magnet = lakeshore_625("COM6")
magnet.start()

time.sleep(0.25)

print magnet.voltage
print magnet.current

print "Got Here"
magnet.stop()