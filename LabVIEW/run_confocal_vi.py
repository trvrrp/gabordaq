import win32com.client
labview = win32com.client.Dispatch("Labview.Application")
f = "C:\\Cryomagnetic_Probe_Station\\GaborDAQ\\LabVIEW\\Confocal_Ver3.11.7_python_integrated.vi"
VI = labview.getvireference(f)
VI.run