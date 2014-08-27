#
# nidaq.py
#
# GaborDAQ modules for talking to National Instruments Data Acquisition Card
#
# Last updated: August 2014 by Trevor Arp
#
# Gabor Lab
# University of California, Riverside
# All Rights Reserved

import ctypes
import time
import Queue
import threading
import numpy as np
from parameters import *

nidaq = ctypes.windll.nicaiu # load the DLL

# NIDAQ drivers Error Checker
def CHK(err):
   if err < 0:
      buf_size = 100
      buf = ctypes.create_string_buffer('\000' * buf_size)
      nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
      raise RuntimeError('nidaq call failed with error %d: %s'%(err, repr(buf.value)))
   if err > 0:
      buf_size = 100
      buf = ctypes.create_string_buffer('\000' * buf_size)
      nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
      raise RuntimeError('nidaq generated warning %d: %s'%(err, repr(buf.value)))
#

# analogVoltageTimeChannel creates a channel to read voltages from a NI DAQ card
# %channels is the number of channels to be read, should match number requested with %physical_chan
#
# %physical_chan is the computer identifiers for the physical channels to be read out,
# it is to be formatted in NI channel syntax for example,
# "Dev1/ai0:4" for channels ai0 through ai4 
# "Dev1/ai0:4, Dev1/ai16:17" for channels ai0 through ai4 and ai16, ai17
#
# %num_queues is the number of Queues that the data is being written into
# multiple queues facilitates sending data into multiple places, for example a data
# writing queue, a data analysis queue and a display queue
# The function get_queues returns a list containing all the queues
class analog_voltage_time_input(threading.Thread):
	# Constructor
	def __init__(self, channels, physical_chan, num_queues):
		self.running = True
		self.numChannels = channels
		self.poll_delay = 0.05
		self.taskHandle = TaskHandle(0)
		self.min = DAQ_AI_Min
		self.max = DAQ_AI_Max 
		self.timeout = float64(10.0)
		self.bufferSize = uInt32(10)                   
		self.pointsRead = uInt32()
		self.sampleRate = float64(masterSampleFreq)
		self.samplesPerChan = uInt64(2000)
		self.chan = ctypes.create_string_buffer(physical_chan)
		self.clockSource = ctypes.create_string_buffer('OnboardClock')
		self.data = np.zeros((1000,),dtype=np.float64)
		self.points = int(masterSampleFreq / 2.0)
		self.polling = True
		self.currentTime = time.clock()
		
		self.dataQueue =[]
		for i in range(num_queues):
			self.dataQueue.append(Queue.Queue(maxsize=200000))
		
		self.dataCount = 0
		CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.taskHandle)))
					
		CHK(nidaq.DAQmxCreateAIVoltageChan(self.taskHandle, self.chan, "", DAQmx_Val_RSE, self.min, self.max,
							DAQmx_Val_Volts, None))
							
		CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle, self.clockSource, self.sampleRate,
							DAQmx_Val_Rising, DAQmx_Val_ContSamps, self.samplesPerChan))
							
		CHK(nidaq.DAQmxCfgInputBuffer(self.taskHandle,200000))
					
		threading.Thread.__init__(self)
	#
		
	# Starts the thread
	def run(self):
		CHK(nidaq.DAQmxStartTask (self.taskHandle))
		self.poll()
	#
	
	# Returns a list containing all the Queues that the data is being written into
	def get_queues(self):
		return self.dataQueue
	# end get_queues
	
	# Re-zeros the time and also zeros the time of the given stopwatch object
	def sync_zero(self, stop_watch):
		self.dataCount = 0
		stop_watch.zero()
	#
		
	# polls the DAQ card for voltage measurements
	def poll(self):
		if self.polling:
			pointsToRead = uInt32(-1)
			data = np.zeros((self.points,self.numChannels),dtype=np.float64)
			CHK(nidaq.DAQmxReadAnalogF64(self.taskHandle,pointsToRead,self.timeout,
					DAQmx_Val_GroupByScanNumber,data.ctypes.data,
					uInt32(data.size),ctypes.byref(pointsRead),None))
			#
			pts = int(pointsRead.value)
			d = np.zeros((pts,self.numChannels+1),dtype=np.float64)
			cnt = 0
			for j in range(0,pts):
				self.dataCount += 1
				d[cnt][0] = self.dataCount/masterSampleFreq
				d[cnt][1:] = data[j][:]
				cnt +=1
			#
			for q in self.dataQueue:
				q.put(d)
			#
			threading.Timer(self.poll_delay, self.poll).start()
	#
	
	# Closes the analog voltage channel
	def stop(self):
		self.running = False
		self.polling = False
		if self.taskHandle.value != 0:
			nidaq.DAQmxStopTask(self.taskHandle)
			nidaq.DAQmxClearTask(self.taskHandle)
	#
# end analog_voltage_time_input

# This class sets the voltage of an analog output on an NI DAQ board
# Default voltage is zero
# constructor parameter is the output channel, for example 5 for channel 'ao5'
class analog_output(threading.Thread):
	# Constructor
	def __init__(self, channel):
		self.running = True
		self.voltage = 2
		self.taskHandle = TaskHandle(0)
		self.chan = ctypes.create_string_buffer('Dev1/ao' + str(channel))

		# Set up the DAQ software
		CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandle)))
		CHK(nidaq.DAQmxCreateAOVoltageChan( self.taskHandle,
			self.chan, "", DAQ_AO_Min, DAQ_AO_Max, DAQmx_Val_Volts, None))
		CHK(nidaq.DAQmxWriteAnalogScalarF64(self.taskHandle,1,float64(-1),float64(self.voltage),None))

		threading.Thread.__init__(self)

	def run(self):
		counter = 0
		CHK(nidaq.DAQmxStartTask(self.taskHandle))
	def set_voltage(self, newVoltage):
		self.voltage = newVoltage
		CHK(nidaq.DAQmxWriteAnalogScalarF64(self.taskHandle,1,float64(-1),float64(self.voltage),None))
	def stop(self):
		self.running = False
		CHK(nidaq.DAQmxWriteAnalogScalarF64(self.taskHandle,1,float64(-1),float64(0),None))
		nidaq.DAQmxStopTask(self.taskHandle)
		nidaq.DAQmxClearTask(self.taskHandle)
# end analog_output