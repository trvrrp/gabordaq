#
# serialcom.py
#
# GaborDAQ functions for communicating with equipment via serial
#
# Last updated: August 2014 by Trevor Arp
#
# Gabor Lab
# University of California, Riverside
# All Rights Reserved

import time
import threading
import serial
import Queue

from parameters import *

# A base class for communicating with serial devices
# 
# %com_port string that sets the COM port used by the serial device e.g. "COM2"
#
class serial_device(threading.Thread):
	def __init__(self, com_port):
		self.running = True
		try:
			self.ser = serial.Serial(
				port=str(com_port),
				baudrate=9600,
				parity=serial.PARITY_ODD,
				stopbits=serial.STOPBITS_ONE,
				bytesize=serial.SEVENBITS,
				timeout=0.05
			)
			self.serial_open = True
		except Exception as e:
			print "Error opening Serial Port" + str(com_port)
			print str(e)
			self.serial_open = False
		#
		
		# initialize data queue
		self.data_queue = Queue.Queue(maxsize=200000)
		
		threading.Thread.__init__(self)
	# end init
	
	# returns the data Queue
	def get_data_queue(self):
		return self.data_queue
	# end get_data_queue
	
	# Sends a request for data to the serial device and listens for a response
	# Returns none and prints to terminal if no response was received
	def get_data(self, command):
		if self.ser.isOpen():
			self.ser.write(str(command) + '\r\n')
			out = self.ser.readline().strip()
			if out == "":
				return None
			else:
				return out
	# end get_data
	
	# Sends a command and does not wait for a response
	def send_command(self, command):
		if self.ser.isOpen():
			self.ser.write(str(command) + '\r\n')
	# end send_command
	
	# Closes the serial connection and stops the thread
	def stop(self):
		self.running = False
		self.ser.close()
	# end stop
# end serial_device

# Defines a controller for a LakeShore Model 625 Superconducting Magnet Power supply
# 
# %com_port string that sets the COM port used by the serial device e.g. "COM6"
#
# Properties that can be accessed after run() is called
# .voltage # The output voltage, Units in Volts
# .current # The output current, Units in Amps
# .field   # The central field, computed from the current based on calibration, Units in Tesla
#
class lakeshore_625(serial_device):
	def __init__(self, com_port, sys_time):
		serial_device.__init__(self,com_port)
		self.name = "LakeShore 625"
		self.current = 0.0
		self.voltage = 0.0
		self.field = 0.0
		self.timer = sys_time
	#
	
	# Runs the magnet
	def run(self):
		self.read_data()
	#	
	
	# Reads the current and voltage and computes the field
	def read_data(self):
		if self.serial_open:
			c = self.get_data("RDGI?") 
			v = self.get_data("RDGV?")
			if c != None and v != None:
				self.current = float(c)
				self.voltage = float(v)
				self.field = self.current * current_to_field * 1.0e-4
				s = str(self.timer.time()) + "\t" + str(self.current) + "\t" + str(self.voltage) + "\t" + str(self.field)
				self.data_queue.put(s)
			#
			self.task = threading.Timer(0.25, self.read_data)
			self.task.start()
	# end read_data
	
	#Closes the serial connection and stops the thread
	def stop(self):
		self.running = False
		self.task.cancel()
		time.sleep(0.1)
		self.ser.close()
	#end stop
# end lakeshore_625
	