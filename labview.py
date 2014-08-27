#
# labview.py
#
# Modules for interfacing GaborDAQ with LabVIEW
#
# Last updated: August 2014 by Trevor Arp
#
# Gabor Lab
# University of California, Riverside
# All Rights Reserved

import win32com.client
import subprocess
import threading
import traceback
import Queue
import time

from parameters import *

# Returns true if the given value can be made into a float, false otherwise
def is_float(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

# labview_vi
# A basic class for starting and stopping a labview virtual instrument, along with
# reading and changing a parameter from that vi.
# Requires a loading script to start the vi
#
# DO NOT try and thread this, many threading issues arise from trying to call LabVIEW in multi threaded context
class labview_VI(): #(threading.Thread):
	def __init__(self, vi_file, vi_load_script):
		self.running = True
		self.vi_file = vi_file
		self.vi_load_script = vi_load_script
		self.vi_name = "LabVIEW Virtual Instrument"
		self.is_running = False
		self.data_log = None
		
		# initialize data queue
		self.data_queue = Queue.Queue(maxsize=200000)
		
		# load the VI
		try:
			
			self.labview_client = win32com.client.Dispatch("Labview.Application")
			self.VI = self.labview_client.getvireference(self.vi_file)
			
		except Exception as e:
			print "Could not load labview vi from: " + str(self.vi_file)
			print str(e)
		
		# threading.Thread.__init__(self)
	# end init
	
	# Stops the thread
	def stop(self):
		self.running = False
		if self.is_running:
			self.close_VI()
	
	# Runs the virtual instrument in another python process
	def run_VI(self):
		if not self.is_running:
			try:
				self.VI.OpenFrontPanel
				subprocess.Popen([self.vi_load_script], shell=True)
				self.is_running = True
				time.sleep(0.125)
			except Exception as e:
				print "Could not run labview vi, try checking load script: " + str(self.vi_load_script)
				print str(e)
		else:
			print "Labview Script is already running"
	# end runvi
	
	# Closes the vi
	def close_VI(self):
		if self.is_running:
			try:
				self.VI.abort
				self.is_running = False
				self.VI.CloseFrontPanel
			except Exception as e:
				print "Could not close labview VI"
				print str(e)
		else:
			print "Labview VI is not running"
	# end close_VI
	
	# Reads the value of a Control or indicator from the Virtual Instrument with the input label
	def read(self, label):
		if isinstance(label, basestring):
			try:
				return self.VI.GetControlValue(str(label))
			except Exception as e:
				print "Could not read value " + str(label) + " from: " + str(self.vi_name)
				print str(e)
				traceback.print_stack()
		else:
			print "labview_VI.read(): Could not read value, given label is not string"
	# end read
	
	# Sets the data logger, if logger is set then parameters can be written to the log file by
	# read_write_params()
	def set_log(self,log):
		self.data_log = log
	#
	
	# returns the data queue
	def get_queue(self):
		return self.data_queue
	# 
	
	# Presses a Button on the VI
	def press_button(self, label):
		try:
			self.VI.setcontrolvalue(str(label), True)
		except Exception as e:
			print "Could not press button " + str(label) + " on VI"
			print str(e)
	#
	
	# Sets a boolean value on the VI
	def set_bool(self, label, bool):
		try:
			self.VI.setcontrolvalue(str(label), bool)
		except Exception as e:
			print "Could not set boolean " + str(label) + " on VI"
			print str(e)
	#
	
	# Sets the value of a Control or indicator from the Virtual Instrument 
	# with the input label to a number given by the input value
	def set_num(self, label, value):
		if isinstance(label, basestring) and is_float(value):
			try:
				self.VI.setcontrolvalue(label,str(value))
			except Exception as e:
				print "Could not set value in: " + str(self.name)
				print str(e)
		else:
			print "labview_VI.set_num(): Could not set value, given label is not string or given value is not a number"
	# end set_num
	
	# Sets the value of a Control or indicator from the Virtual Instrument 
	# with the input label to a string given by the input value
	def set_str(self, label, value):
		if isinstance(label, basestring) and not is_float(value):
			try:
				self.VI.setcontrolvalue(label,str(value))
			except Exception as e:
				print "Could not set value in: " + str(self.name)
				print str(e)
		else:
			print "labview_VI.set_num(): Could not set value, given label is not string"
			print "or given value is a number, in which case use set_num()"
	# end set_num
	
# end labview_VI


class temperature_control(labview_VI):
	def __init__(self, stop_watch):
		labview_VI.__init__(self, temperature_vi_path, temperature_run_path)
		self.vi_name = "Lakeshore  336 Temperature Controller"
		self.timer = stop_watch
		# Read starting parameters
		self.tempA = self.read("Sensor A: Sample Mount")
		self.tempB = self.read("Sensor B: 4k Plate")
		self.tempC = self.read("Sensor C: Top of the Magnet")
		self.tempD = self.read("Sensor D: Radiation Shield")
		self.P = self.read("Gain (P)")
		self.I = self.read("Gain (I)")
		self.D = self.read("Gain (D)")
		self.tempA = 0
		self.tempB = 0
		self.tempC = 0
		self.tempD = 0
		self.range = self.read("Range")
		self.mode = self.read("Mode")
		self.setpoint = self.read("Setpoint")
	# end init
	
	#Sets the VI running
	# def run(self):
		# self.read_data()
	
	
	# Reads temperature data from the VI
	def read_data(self):
		if self.is_running:
			self.tempA = self.read("Sensor A: Sample Mount")
			self.tempB = self.read("Sensor B: 4k Plate")
			self.tempC = self.read("Sensor C: Top of the Magnet")
			self.tempD = self.read("Sensor D: Radiation Shield")
			s = str(self.timer.time()) + "\t" + str(self.tempA) + "\t" + str(self.tempB) + "\t" + str(self.tempC) + "\t" + str(self.tempD)
			self.data_queue.put(s)
	#
	
	# Gets the values of the feedback loop parameters
	def get_params(self):
		self.P = self.read("Gain (P)")
		self.I = self.read("Gain (I)")
		self.D = self.read("Gain (D)")
		self.range = self.read("Range")
		self.mode = self.read("Mode")
		self.setpoint = self.read("Setpoint")
	#
	
	# Records the data parameters to the log file
	def read_write_setpoint(self):
		if self.data_log != None:
			self.get_params()
			self.data_log.log("Heater Setpoint", self.setpoint)
	
	# Records the data parameters to the log file
	def read_write_PID(self):
		if self.data_log != None:
			self.get_params()
			w = self.data_log
			w.log("Heater Gain (P)", self.P)
			w.log("Heater Gain (I)", self.I)
			w.log("Heater Gain (D)", self.D)
			w.log("Heater range", self.range)
			w.log("Heater Mode", self.mode)
			#w.log("Heater Setpoint", self.setpoint)
		#
	#
# end temp_control

class photocurrent_control(labview_VI):
	def __init__(self, stop_watch):
		labview_VI.__init__(self, photocurrent_vi_path, photocurrent_run_path)
		self.vi_name = "Confocal_Ver3.11.7_python_integrated"
		self.timer = stop_watch
		self.saving = False
	#
	
	# Reads the ramp up parameters from the VI
	def read_ramp_up(self):
		self.ramp_up_channel = self.read("physical channels 3")
		self.ramp_up_start = self.read("Start")
		self.ramp_up_end = self.read("End")
		self.ramp_up_time = self.read("Time (s)")
		self.ramp_up_rate = self.read("Rate (S/s)")
	# end read_ramp_up
	
	# Records the ramp up parameters to the log file
	def read_write_ramp(self):
		if self.data_log != None:
			self.read_ramp_up()
			w = self.data_log
			w.log("Ramp up channel", self.ramp_up_channel)
			w.log("Ramp up Start", self.ramp_up_start)
			w.log("Ramp up End", self.ramp_up_end)
			w.log("Ramp up Time", self.ramp_up_time)
			w.log("Ramp up Rate", self.ramp_up_rate)
	# end read_write_ramp
	
	# Reads the scan parameters from the VI
	def read_scan(self):
		self.y_scan_size = self.read("Y Scan size(um) ")
		self.x_scan_size = self.read("X Scan size(um)")
		self.scan_rate = self.read("Scan Rate (Hz)")
		self.scan_lines = self.read("Scan Lines")
		if self.read("Outer Voltage Scan"):
			self.outer_scan = True
			self.outer_channel = self.read("physical channels 2")
			self.outer_start = self.read("start voltage")
			self.outer_end = self.read("end voltage")
		else:
			self.outer_scan = False
		if self.read("Inner Voltage Scan"):
			self.inner_scan = True
			self.inner_channel = self.read("physical channels 4")
			self.inner_start = self.read("start voltage 2")
			self.inner_end = self.read("end voltage 2")
		else:
			self.inner_scan = False
		#
	# end read_scan
	
	# Reads and records the scan parameters from the VI
	def read_write_scan(self):
		if self.data_log != None:
			self.read_scan()
			w = self.data_log
			w.log("Y Scan size(um)", self.y_scan_size)
			w.log("X Scan size(um)", self.x_scan_size)
			w.log("Scan Rate (Hz)", self.scan_rate)
			w.log("Scan Lines", self.scan_lines)
			if self.outer_scan:
				w.log_str("OUTER SCAN PARAMETERS")
				w.log("Outer Scan Channel", self.outer_channel)
				w.log("Outer Scan Start Voltage", self.outer_start)
				w.log("Outer Scan End Voltage", self.outer_end)
			if self.inner_scan:
				w.log_str("INNER SCAN PARAMETERS")
				w.log("Inner Scan Channel", self.inner_channel)
				w.log("Inner Scan Start Voltage", self.inner_start)
				w.log("Inner Scan End Voltage", self.inner_end)
	#
	
	# Saves the next set of images
	def save_image(self):
		self.set_bool("Save Image", True)
	
	# Sets the filenames to save the data
	def set_files(self, path, run):
		sref = path + str(run) + "_rfi.dat"
		spc = path + str(run) + "_pci.dat"
		self.set_str("Reflection", str(sref))
		self.set_str("Photocurrent",str(spc))
			
# end photocurrent_control