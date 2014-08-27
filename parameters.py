# parameters.py
import ctypes

DAQ_name = "CPSDAQ"

# Data Writing Parameters
data_file_ext = "dat" # Data file extension, i.e. filename.ext
data_file_types = ['bnc','tmp', 'mag','log'] # Types of data file, 'bnc' should always be first and 'log' should always be last

# Data Acquisition Parameters
masterSampleFreq = 100.0 # 1000.0 # DAQ card sample frequency, type = float

# System Paths
data_dir_path = "C:\\Cryomagnetic_Probe_Station\\Data\\" # Path to data directory
labview_dir_path = "C:\\Cryomagnetic_Probe_Station\\GaborDAQ\\LabVIEW\\" # Path to labview VIs

# LabVIEW Virtual Instrument Paths
temperature_vi_path = labview_dir_path + 'Temperature DAQ v1.1.vi'
photocurrent_vi_path = labview_dir_path + 'Confocal_Ver3.11.7_python_integrated.vi'

# LabVIEW Run Script Paths
temperature_run_path = labview_dir_path + 'run_temp_vi.py'
photocurrent_run_path = labview_dir_path + 'run_confocal_vi.py'

# Magnet Parameters
current_to_field = 1070.0 # Based on Janis research calibration # Units Gauss/Amps

# NI_DAQmx typedefs and constants, correspond with values in
# C:\Program Files(x86)\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
pointsRead = uInt32()
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0
DAQmx_Val_ChanForAllLines = 1
DAQmx_Val_RSE = 10083
DAQmx_Val_NRSE = 10078
DAQmx_Val_Diff =  10106
DAQmx_Val_Volts = 10348
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByScanNumber = 1
DAQ_AO_Max = float64(5.0)
DAQ_AO_Min = float64(-5.0)
DAQ_AI_Max = float64(5.0)
DAQ_AI_Min = float64(-5.0)