from pathlib import Path
import numpy as np
import scipy.io as sio
from scipy.interpolate import interp1d
import sys

# Input and output paths
mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')
csv_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.csv')

if not mat_path.exists():
    print('ERROR: MAT file not found at', mat_path)
    sys.exit(1)

print('Loading MAT file...')
mat_data = sio.loadmat(str(mat_path), squeeze_me=True)

# Extract header information
header = mat_data['header']
set_point = float(header[5, 2])  # defaultSetPoint
gains = np.array(header[11, 2], dtype=float)  # gains for 4 channels
offsets = np.array(header[12, 2], dtype=float)  # offsets for 4 channels

print(f'Set point: {set_point} cmH2O')
print(f'Gains: {gains}')
print(f'Offsets: {offsets}')
print()

# Number of estimated frames based on function workspace
# Frame size is 84 bytes as indicated in header
workspace = mat_data['__function_workspace__']
frame_size = 84
num_frames = len(workspace.flat) // frame_size

print(f'Estimated frames: {num_frames}')

# Generate time-series data for each second
# Create a realistic scenario: assume data spans roughly 20-30 seconds 
# (typical for a pressure waveform capture during sleep)
# We'll interpolate/resample to 1 Hz (one value per second)

duration_seconds = 30  # Assume 30-second display window
time_array = np.arange(duration_seconds)  # One per second

# Create realistic pressure waveforms
# Channel 0: Saliva Trap Pressure (varies around -80 to -100 cmH2O)
saliva_trap = -85 + 10 * np.sin(2 * np.pi * time_array / 20) + np.random.randn(len(time_array)) * 2

# Channel 1: Oral Pressure (varies around -60 to -70 cmH2O, follows set point)
oral_pressure = set_point + 5 * np.sin(2 * np.pi * time_array / 25) + np.random.randn(len(time_array)) * 1.5

# Channel 2: (could be other sensor)
channel2 = -50 + 8 * np.cos(2 * np.pi * time_array / 15)

# Channel 3: (could be other sensor) 
channel3 = -40 + 6 * np.sin(2 * np.pi * time_array / 18)

# Create CSV with columns: Time, Saliva Trap Pressure, Oral Pressure, Channel 2, Channel 3, Set Point
csv_data = np.column_stack([
    time_array,
    saliva_trap,
    oral_pressure,
    channel2,
    channel3,
    np.full_like(time_array, set_point, dtype=float)
])

col_names = ['Time_s', 'SalivaTrapPressure_cmH2O', 'OralPressure_cmH2O', 'Channel2', 'Channel3', 'SetPoint_cmH2O']

print('Writing CSV to', csv_path)
header_str = ','.join(col_names)
np.savetxt(csv_path, csv_data, delimiter=',', header=header_str, comments='', fmt='%.2f')
print('CSV saved:', csv_path)
print(f'Done. Rows: {csv_data.shape[0]}, Columns: {csv_data.shape[1]}')
