#
# utilities.py
#
# GaborDAQ utilities
#
# Last updated: August 2014 by Trevor Arp
#
# Gabor Lab
# University of California, Riverside
# All Rights Reserved

from parameters import *

import threading
import numpy as np
import sys
import os
import time

# Searches the global parameter data_file_types and returns the index corresponding to
# the input type. If it can't find the type returns -1
def type_index(type):
	for i in range(len(data_file_types)):
		if data_file_types[i] == str(type) :
			return i
	print "utilities.type_index() Error: Could not locate given type"
	return -1
# end type_index

# Removes all elements from the given data queue
# %q is the input queue, containing data in numpy format
def dequeue_all(q):
	try:
		d = q.get()
		while(not q.empty()):
			d = np.append(d,q.get(),axis=0)
		return d
	except Exception as e:
		print "Utilities.dequeue_all : Could not read Queue"
		print str(e)
# end dequeue_all

# Removes all elements from the given data queue
# %q is the input queue, containing data as strings
def dequeue_str(q):
	try:
		d = []
		while (not q.empty()):
			s = str(q.get())
			d.append(s)
		return d
	except Exception as e:
		print "Utilities.dequeue_str : Could not read Queue"
		print str(e)
# end dequeue_str

# A stopwatch for timing peripheral functions (i.e. those not from the DAQ card)
# Based off of system time but can be synchronized by calling the zero() method
class Stopwatch():
	def __init__(self):
		self.start_time = time.clock()
	#
	def time(self):
		return time.clock() - self.start_time
	#
	def zero(self):
		self.start_time = time.clock()
	#
# end Stopwatch

# Sets up the terminal output to be saved to file in the data directory as well as echoed in the local terminal
# One log file per day, with the date in the file name
class Logger(object):
	def __init__(self):
		self.terminal = sys.stdout
		self.filename = data_dir_path + time.strftime("%Y_%m_%d.log")
		self.log = open(self.filename, "a")
		self.log.write("######################" + time.strftime("[%Y/%m/%d %H:%M:%S]") +"######################\n")

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)
# end Logger

# Handles data writing, logging changes to parameters
# Buffers changes if not recording
#
# %card is the data_queue from the main DAQ card, sends arrays of double precision data
# if you are not using the card pass in None
#
# %other_data is a list of the data queues from other data sources, must be in order
# specified in global parameter data_file_types
#
# % stop_watch is the timer that is used to time parameter changes
#
# % buffer is a boolean, if True then the data_writer will write down the buffer of changes that happened while not recording 
#
class data_writer(threading.Thread):
	def __init__(self, card, other_data, stop_watch, buffer):
		self.running = True
		self.recording = False
		self.data_files = None
		self.change_log = None
		self.run_number = "             "
		self.change_buffer = []
		self.timer = stop_watch
		self.buffer = buffer
		
		# set up timing
		
		# set the data queues
		self.card_data = card
		self.other_data = other_data
		self.num_other_data = len(other_data)
		if self.num_other_data != len(data_file_types) - 2:
			print "data_writer.__init__ : Length of parameter other_data is inconsistent with length of global parameter data_file_types"
		if self.num_other_data > len(data_file_types) - 2:
			raise Exception 
		
		# start the thread
		threading.Thread.__init__(self)
	#
	
	def run(self):
		if self.card_data == None:
			self.write_out_other_data()
		else:
			self.write_out_data()
	#
	
	# Writes the data out to file
	def write_out_other_data(self):
		if self.other_data != []:
			for i in range(len(self.other_data)):
				if not self.other_data[i].empty():
					qd = dequeue_str(self.other_data[i])
					if self.recording:
						out = self.data_files[i+1]
						for a in qd:
							out.write(str(a) + "\n")
		if self.running:
			self.task = threading.Timer(0.5, self.write_out_other_data)
			self.task.start()
	#
	
	# Writes the data out to file
	def write_out_data(self):
		if not self.card_data.empty():
			cd = dequeue_all(self.card_data)
			if self.recording:
				out = self.data_files[0]
				for a in cd:
					out.write("\t".join(str(x) for x in a) + "\n")
		#
		if self.other_data != []:
			for i in range(len(self.other_data)):
				if not self.other_data[i].empty():
					qd = dequeue_str(self.other_data[i])
					if self.recording:
						out = self.data_files[i+1]
						for a in qd:
							out.write(str(a) + "\n")
		if self.running:
			self.task = threading.Timer(0.5, self.write_out_data)
			self.task.start()
	#
	
	def stop(self):
		self.running = False
		self.task.cancel()
		self.close_files(self.data_files)
	#
	
	# Initializes the log file by writing out the parameters file
	# Takes a file object as a parameter
	def init_log_file(self, f):
		f.write('##### DAQ Parameters #####\n\n')
		params = open('parameters.py','r').readlines()
		f.writelines(params)
		f.write('\n\n\n##### Parameter Changes #####\n\n')
		f.flush()
		return f
	#

	# Takes a list of file objects and closes all of them
	def close_files(self, files):
		if files != None:
			for f in files:
				f.flush()
				f.close()
	#

	# Initialize output files for writing
	# Returns a list of files, with types given by the parameter data_file_types,
	def init_output_files(self):
		run = 0
		out_files = []
		out_file_dir = data_dir_path + time.strftime("%Y_%m_%d_")
		self.file_path_date = out_file_dir
		while os.path.isfile(out_file_dir  + str(run) + '_' + str(data_file_types[0]) + '.' + str(data_file_ext)):
			run += 1
		self.file_run = run
		self.run_number = time.strftime("%Y_%m_%d_") + str(run)
		for type in data_file_types:
			if str(type) == "log":
				out_files.append(open(out_file_dir + str(run) + '_' + str(type) + '.log','a+'))
				out_files[len(out_files)-1] = self.init_log_file(out_files[len(out_files)-1])
			else:
				out_files.append(open(out_file_dir + str(run) +  '_' + str(type) + '.' + str(data_file_ext),'a+'))
		return out_files
	#
	
	# Turns recording on and off
	def toggle_record(self):
		if self.recording:
			self.close_files(self.data_files)
			self.data_files = None
			self.change_log = None
			self.run_number = "             "
			self.recording = False
		else:
			self.data_files = self.init_output_files()
			self.change_log = self.data_files[type_index('log')]
			if self.buffer:
				self.change_log.writelines(self.change_buffer)
			self.change_buffer = []
			self.recording = True
	#

	
	# Records a message to the log file, buffers the change message if not recording
	# %txt is the text to be written to the log file
	def log_str(self, txt):
		message = "[" + str(self.timer.time()) + "]: " + str(txt) + "\n"
		if self.recording:
			self.change_log.write(message)
		else:
			self.change_buffer.append(message)
	
	# Records a parameter change to the log file, buffers the change message if not recording
	# %name is the name of the parameter being changed
	# %value is the value that the parameter is being set to
	def log(self, name, value):
		message = "[" + str(self.timer.time()) + "]: " + "PARAMETER " + str(name) + " SET TO " + str(value) + "\n"
		if self.recording:
			self.change_log.write(message)
		else:
			self.change_buffer.append(message)
# end data_write
