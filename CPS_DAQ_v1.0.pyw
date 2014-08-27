#
# CPSDAQ
#
# Data Acquisition for the Cryomagnetic Probe Station
#
# Version 1.0
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

# Initialize the magnet control
magnet = lakeshore_625("COM6", sys_time)
magnet.start()

# Initialize LabVIEW VIs
temp_control = temperature_control(sys_time)
temp_control.run_VI()

photo = photocurrent_control(sys_time)
photo.run_VI()

# Initialize command Queue
com_q = Queue.Queue(maxsize=200000)

# Initialize Data Writer, hand log to labview VIs
data_out = data_writer(None,[temp_control.get_queue(), magnet.get_data_queue()],sys_time, True)
data_out.start()
temp_control.set_log(data_out)
photo.set_log(data_out)

# Initialize the GUI
UI = interface_lab_mag(data_out, com_q)

# Function needed to pass labview the correct filenames
already_scanned = False
def setup_scan():
	global already_scanned
	if data_out.recording:
		if already_scanned:
			# Reset the recording and pass the filenames to the VI
			UI.quiet_toggle_record()
			time.sleep(0.1)
			UI.quiet_toggle_record()
			time.sleep(0.1)
			photo.set_files(data_out.file_path_date ,data_out.file_run)
			photo.save_image()
		else:
			already_scanned = True
			photo.set_files(data_out.file_path_date ,data_out.file_run)
			photo.save_image()
# end setup_scan

#### Main program ####

# Main loop
while (UI.running):
	time.sleep(0.25)
	if not com_q.empty():
		s = com_q.get()
		if s == "Photocurrent Ramp Up":
			data_out.log_str("Ramp Up Started")
			photo.read_write_ramp()
			photo.press_button("Ramp Up")
		elif s == "Photocurrent Finite Scan":
			setup_scan()
			data_out.log_str("Finite Scan Started")
			photo.read_write_scan()
			photo.press_button("Finite scan")
		elif s == "Photocurrent Cont. Scan":
			setup_scan()
			data_out.log_str("Continuous Scan Started")
			photo.read_write_scan()
			photo.press_button("Continuous Scan")
		elif s == "Photocurrent stop":
			data_out.log_str("Scan Stopped Manually")
			photo.press_button("Stop")
		elif s == "Turn Heater Off":
			data_out.log_str("Heater Turned off")
			temp_control.press_button("Heater Off")
		elif s == "Set Heater Params":
			temp_control.read_write_PID()
			temp_control.press_button("Configure")
		elif s == "Set Heater Setpoint":
			temp_control.read_write_setpoint()
			temp_control.press_button("Enter")
		elif s == "Toggle recording":
			already_scanned = False
	temp_control.read_data()
	UI.set_magnet(magnet.voltage, magnet.current, magnet.field)
#

#### End Main Program and Shut Down ####

# Close the data writer
data_out.stop()

# Close LabVIEW VIs
temp_control.stop()
photo.stop()

# Stop the magnet controller
magnet.stop()