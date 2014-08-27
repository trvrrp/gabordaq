#
# gui.py
#
# GaborDAQ module for the graphical user interfaces
#
# Last updated: August 2014 by Trevor Arp
#
# Gabor Lab
# University of California, Riverside
# All Rights Reserved

import threading
import Tkinter as tk
import tkMessageBox

from parameters import *

# Base graphical user interface
# %writer is the data writer for the program
# %command_queue is a queue with which the GUI can send commands  to the main thread
class interface(threading.Thread):
	# Constructs and starts the GUI
	def __init__(self, writer, command_queue):
		self.running = True
		self.screen = tk.Tk()
		self.data_out = writer
		
		#LabView commands
		self.command_queue = command_queue
		
		# Set up the window
		self.screen.protocol("WM_DELETE_WINDOW", self.stop)
		self.screen.resizable(0,0)
		self.screen.wm_title(str(DAQ_name))
		
		# start the thread
		threading.Thread.__init__(self)
		self.start()
	#
	
	# Sets up then runs the program
	def run(self):
		# Recording Frame
		self.recordingFRAME = tk.Frame(self.screen)
		
		self.recordingTEXT = tk.StringVar()
		self.recordingTEXT.set("Not Recording")
		self.recordingLABLE = tk.Label(self.recordingFRAME, textvariable=self.recordingTEXT, width=13)
		self.recordingLABLE.grid(row=0, column =1)
		
		rec = lambda: self.toggle_record()
		self.recordingBUTTON = tk.Button(self.recordingFRAME, text='Recording On/Off', command=rec)
		self.recordingBUTTON.grid(row=0, column =0)
		
		tk.Label(self.recordingFRAME, text="Run Number:").grid(row=1, column=0)
		self.run_numTEXT = tk.StringVar()
		self.run_numTEXT.set(self.data_out.run_number)
		self.run_numLABEL = tk.Label(self.recordingFRAME, textvariable=self.run_numTEXT, width=14)
		self.run_numLABEL.grid(row=1, column=1)
		
		# Pack the frames
		self.recordingFRAME.grid(row=0)
		
		# Start the GUI
		self.screen.mainloop() # Must be last line
	#
	
	# Stops the program, deletes the GUI
	def stop(self):
		if self.data_out.recording:
			if not tkMessageBox.askokcancel("Confirm Close?", str(DAQ_name) + " is recording, are you sure you want to close?"):
				return
			#
		#
		self.running = False
		self.screen.destroy()
	#
	
	# Toggles the recording on the front panel
	def toggle_record(self):
		self.command_queue.put("Toggle recording")
		if self.data_out.recording:
			self.data_out.toggle_record()
			self.recordingTEXT.set("Not Recording")
			self.run_numTEXT.set(self.data_out.run_number)
		else:
			self.data_out.toggle_record()
			self.recordingTEXT.set("  Recording  ")
			self.run_numTEXT.set(self.data_out.run_number)
	#
	
	# Toggles the recording on the front panel without queueing the command
	def quiet_toggle_record(self):
		if self.data_out.recording:
			self.data_out.toggle_record()
			self.recordingTEXT.set("Not Recording")
			self.run_numTEXT.set(self.data_out.run_number)
		else:
			self.data_out.toggle_record()
			self.recordingTEXT.set("  Recording  ")
			self.run_numTEXT.set(self.data_out.run_number)
	#
	
# end interface

# Interface including magnet control and LabVIEW VIs controlling temperature and photocurrent
class interface_lab_mag(interface):	
	# Constructor
	def __init__(self, writer, command_queue):
		interface.__init__(self, writer, command_queue)
		self.magnetcurrentTEXT = tk.StringVar()
		self.magnetcurrentTEXT.set(str(0.0))
		self.magnetvoltageTEXT = tk.StringVar()
		self.magnetvoltageTEXT.set(str(0.0))
		self.magnetfieldTEXT = tk.StringVar()
		self.magnetfieldTEXT.set(str(0.0))
	#
	
	# Sets the magnet voltage and current displays
	def set_magnet(self, volts, amps, field):
		self.magnetcurrentTEXT.set(str(round(amps,5)))
		self.magnetvoltageTEXT.set(str(round(volts,5)))
		self.magnetfieldTEXT.set(str(round(field,4)))
	#
	
	# Sets up then runs the program
	def run(self):
		# Recording Frame
		self.recordingFRAME = tk.Frame(self.screen)
		
		self.recordingTEXT = tk.StringVar()
		self.recordingTEXT.set("Not Recording")
		self.recordingLABLE = tk.Label(self.recordingFRAME, textvariable=self.recordingTEXT, width=13)
		self.recordingLABLE.grid(row=0, column =1)
		
		rec = lambda: self.toggle_record()
		self.recordingBUTTON = tk.Button(self.recordingFRAME, text='Recording On/Off', command=rec)
		self.recordingBUTTON.grid(row=0, column =0)
		
		tk.Label(self.recordingFRAME, text="Run Number:").grid(row=1, column=0, sticky=tk.W)
		self.run_numTEXT = tk.StringVar()
		self.run_numTEXT.set(self.data_out.run_number)
		self.run_numLABEL = tk.Label(self.recordingFRAME, textvariable=self.run_numTEXT, width=14)
		self.run_numLABEL.grid(row=1, column=1)
		
		# Heater Control Frame
		self.heaterFRAME = tk.Frame(self.screen)
		
		heater_PID = lambda: self.command_queue.put("Set Heater Params")
		self.heaterparamsBUTTON = tk.Button(self.heaterFRAME, text='Set Heater PID', command=heater_PID)
		heater_setpoint = lambda: self.command_queue.put("Set Heater Setpoint")
		self.heatersetptBUTTON = tk.Button(self.heaterFRAME, text='Enter Heater Setpoint', command=heater_setpoint)
		heater_off = lambda: self.command_queue.put("Turn Heater Off")
		self.heateroffBUTTON = tk.Button(self.heaterFRAME, text='Heater Off', command=heater_off)
		tk.Label(self.heaterFRAME, text="Temperature Controls").grid(row=0, column=0)
		self.heaterparamsBUTTON.grid(row=1, column=0)
		self.heatersetptBUTTON.grid(row=2, column=0)
		self.heateroffBUTTON.grid(row=3, column=0, sticky=tk.W+tk.N+tk.E+tk.S)
		
		# Photocurrent Control Frame
		self.photocurrentFRAME = tk.Frame(self.screen)
		
		ramp_up = lambda: self.command_queue.put("Photocurrent Ramp Up")
		self.rampupBUTTON = tk.Button(self.photocurrentFRAME, text="Ramp Up", command=ramp_up)
		finite_scan = lambda: self.command_queue.put("Photocurrent Finite Scan")
		self.finitescanBUTTON = tk.Button(self.photocurrentFRAME, text="Finite Scan", command=finite_scan)
		cont_scan = lambda: self.command_queue.put("Photocurrent Cont. Scan")
		self.contscanBUTTON = tk.Button(self.photocurrentFRAME, text="Cont. Scan", command=cont_scan)
		
		tk.Label(self.photocurrentFRAME, text="Photocurrent Controls").grid(row=0, column=0)
		self.rampupBUTTON.grid(row=1, column=0)
		self.finitescanBUTTON.grid(row=2, column=0)
		#self.contscanBUTTON.grid(row=3, column=0)
		
		# Magnet Control Frame
		self.magnetFRAME = tk.Frame(self.screen)
		

		self.currentLABEL = tk.Label(self.magnetFRAME, textvariable=self.magnetcurrentTEXT, width=6)
		self.voltageLABEL = tk.Label(self.magnetFRAME, textvariable=self.magnetvoltageTEXT, width=6)
		self.fieldLABEL = tk.Label(self.magnetFRAME, textvariable=self.magnetfieldTEXT, width=6)
		
		tk.Label(self.magnetFRAME, text="Magnet Controls").grid(row=0, column=0)
		
		tk.Label(self.magnetFRAME, text="Output Current (A):").grid(row=1, column=0)
		self.currentLABEL.grid(row=1,column=1)
		tk.Label(self.magnetFRAME, text="Output Voltage (V):").grid(row=2, column=0)
		self.voltageLABEL.grid(row=2,column=1)
		tk.Label(self.magnetFRAME, text="Central Field (T):").grid(row=3, column=0)
		self.fieldLABEL.grid(row=3,column=1)
		
		# Pack the frames
		self.recordingFRAME.grid(row=0, column=0, sticky=tk.W+tk.N)
		self.heaterFRAME.grid(row=1,column=0,padx=5, pady=0, sticky=tk.N+tk.W)
		self.photocurrentFRAME.grid(row=1,column=1, padx=5, pady=0, sticky=tk.N+tk.W)
		self.magnetFRAME.grid(row=2, column=0, columnspan=2)
		
		# Start the GUI
		self.screen.mainloop() # Must be last line
	#
# end interface_lab_mag

# Interface including magnet control and LabVIEW VIs temperature and direct control of DAQ card
class interface_labtemp_mag(interface_lab_mag):	
	# Constructor
	def __init__(self, writer, command_queue):
		interface_lab_mag.__init__(self, writer, command_queue)
	#
	
	# Sets up then runs the program
	def run(self):
		# Recording Frame
		self.recordingFRAME = tk.Frame(self.screen)
		
		self.recordingTEXT = tk.StringVar()
		self.recordingTEXT.set("Not Recording")
		self.recordingLABLE = tk.Label(self.recordingFRAME, textvariable=self.recordingTEXT, width=13)
		self.recordingLABLE.grid(row=0, column =1)
		
		rec = lambda: self.toggle_record()
		self.recordingBUTTON = tk.Button(self.recordingFRAME, text='Recording On/Off', command=rec)
		self.recordingBUTTON.grid(row=0, column =0)
		
		tk.Label(self.recordingFRAME, text="Run Number:").grid(row=1, column=0, sticky=tk.W)
		self.run_numTEXT = tk.StringVar()
		self.run_numTEXT.set(self.data_out.run_number)
		self.run_numLABEL = tk.Label(self.recordingFRAME, textvariable=self.run_numTEXT, width=14)
		self.run_numLABEL.grid(row=1, column=1)
		
		# Heater Control Frame
		self.heaterFRAME = tk.Frame(self.screen)
		
		heater_PID = lambda: self.command_queue.put("Set Heater Params")
		self.heaterparamsBUTTON = tk.Button(self.heaterFRAME, text='Set Heater PID', command=heater_PID)
		heater_setpoint = lambda: self.command_queue.put("Set Heater Setpoint")
		self.heatersetptBUTTON = tk.Button(self.heaterFRAME, text='Enter Heater Setpoint', command=heater_setpoint)
		heater_off = lambda: self.command_queue.put("Turn Heater Off")
		self.heateroffBUTTON = tk.Button(self.heaterFRAME, text='Heater Off', command=heater_off)
		tk.Label(self.heaterFRAME, text="Temperature Controls").grid(row=0, column=0)
		self.heaterparamsBUTTON.grid(row=1, column=0)
		self.heatersetptBUTTON.grid(row=2, column=0)
		self.heateroffBUTTON.grid(row=3, column=0, sticky=tk.W+tk.N+tk.E+tk.S)
		
		# Photocurrent Control Frame
		self.photocurrentFRAME = tk.Frame(self.screen)
		
		ramp_up = lambda: self.command_queue.put("Photocurrent Ramp Up")
		self.rampupBUTTON = tk.Button(self.photocurrentFRAME, text="Ramp Up", command=ramp_up)
		finite_scan = lambda: self.command_queue.put("Photocurrent Finite Scan")
		self.finitescanBUTTON = tk.Button(self.photocurrentFRAME, text="Finite Scan", command=finite_scan)
		cont_scan = lambda: self.command_queue.put("Photocurrent Cont. Scan")
		self.contscanBUTTON = tk.Button(self.photocurrentFRAME, text="Cont. Scan", command=cont_scan)
		
		tk.Label(self.photocurrentFRAME, text="Photocurrent Controls").grid(row=0, column=0)
		self.rampupBUTTON.grid(row=1, column=0)
		self.finitescanBUTTON.grid(row=2, column=0)
		#self.contscanBUTTON.grid(row=3, column=0)
		
		# Magnet Control Frame
		self.magnetFRAME = tk.Frame(self.screen)

		self.currentLABEL = tk.Label(self.magnetFRAME, textvariable=self.magnetcurrentTEXT, width=6)
		self.voltageLABEL = tk.Label(self.magnetFRAME, textvariable=self.magnetvoltageTEXT, width=6)
		self.fieldLABEL = tk.Label(self.magnetFRAME, textvariable=self.magnetfieldTEXT, width=6)
		
		tk.Label(self.magnetFRAME, text="Magnet Controls").grid(row=0, column=0)
		
		tk.Label(self.magnetFRAME, text="Output Current (A):").grid(row=1, column=0)
		self.currentLABEL.grid(row=1,column=1)
		tk.Label(self.magnetFRAME, text="Output Voltage (V):").grid(row=2, column=0)
		self.voltageLABEL.grid(row=2,column=1)
		tk.Label(self.magnetFRAME, text="Central Field (T):").grid(row=3, column=0)
		self.fieldLABEL.grid(row=3,column=1)
		
		# Pack the frames
		self.recordingFRAME.grid(row=0, column=0, sticky=tk.W+tk.N)
		self.heaterFRAME.grid(row=1,column=0,padx=5, pady=0, sticky=tk.N+tk.W)
		self.photocurrentFRAME.grid(row=1,column=1, padx=5, pady=0, sticky=tk.N+tk.W)
		self.magnetFRAME.grid(row=2, column=0, columnspan=2)
		
		# Start the GUI
		self.screen.mainloop() # Must be last line
	#
# end interface_labtemp_mag