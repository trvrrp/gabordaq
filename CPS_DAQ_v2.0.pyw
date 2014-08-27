#
# CPSDAQ
#
# Data Acquisition for the Cryomagnetic Probe Station
#
# Version 2.0
#
# Last updated: August 2014 by Trevor Arp
#
# Gabor Lab
# University of California, Riverside
# All Rights Reserved

#### General Imports ####
import sys
import time
import Queue

#### Import CPSDAQ Modules ####
from serialcom import *
from parameters import *
from utilities import *
from labview import *
from nidaq import *
from gui import *

#### Core Class initializations ####

# Initialize terminal logger
sys.stdout = Logger()

# Initialize peripheral timer, linked to system time
sys_time = Stopwatch()

# Initialize DAQ card
card_in  =  analog_voltage_time_input(10,"Dev1/ai0:7, Dev1/ai16:17",1)
card_ao0 = analog_output(0)
card_ao1 = analog_output(1)
card_ao2 = analog_output(2)
card_ao3 = analog_output(3)
card_in.start()
card_ao0.start()
card_ao1.start()
card_ao2.start()
card_ao3.start()
card_ao0.set_voltage(0.00)
card_ao1.set_voltage(0.00)
card_ao2.set_voltage(0.00)
card_ao3.set_voltage(0.00)

# Initialize LabVIEW VIs
temp_control = temperature_control(sys_time)
temp_control.run_VI()

# Initialize command Queue
com_q = Queue.Queue(maxsize=200000)

# Initialize Data Writer, hand log to labview VIs
card_q = card_in.get_queues()
data_out = data_writer(card_q[0],[temp_control.get_queue()],sys_time)
data_out.start()
temp_control.set_log(data_out)

# Initialize the GUI
UI = interface_lab_mag(data_out, com_q)

#### Main program ####

# Main loop
while (UI.running):
	time.sleep(0.25)
	if not com_q.empty():
		s = com_q.get()
		if s == "Set Heater Params":
			temp_control.read_write_PID()
			temp_control.press_button("Configure")
		elif s == "Set Heater Setpoint":
			temp_control.read_write_setpoint()
			temp_control.press_button("Enter")
		else:
			print s
	temp_control.read_data()
#

#### End Main Program and Shut Down ####

# Close the data writer
data_out.stop()

# Close LabVIEW VIs
temp_control.stop()

# Shut down the DAQ card
card_in.stop()
card_ao0.stop()
card_ao1.stop()
card_ao2.stop()
card_ao3.stop()