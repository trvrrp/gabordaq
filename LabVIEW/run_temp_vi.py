import win32com.client
labview = win32com.client.Dispatch("Labview.Application")
#f = 'C:\\Cryomagnetic_Probe_Station\\labview\\Temp Controller\\Temperature DAQ v1.1.vi'
f = 'C:\\Cryomagnetic_Probe_Station\\GaborDAQ\\LabVIEW\\Temperature DAQ v1.1.vi'
VI = labview.getvireference(f)
VI.run