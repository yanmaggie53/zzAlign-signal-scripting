from pathlib import Path
import numpy as np
import scipy.io as sio
import struct
import sys

# Input and output paths
mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')
csv_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s_actual.csv')

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

# Extract raw frame data from function workspace
workspace = mat_data['__function_workspace__']
frame_size = 84  # bytes per frame
num_frames = len(workspace.flat) // frame_size

print(f'Extracting {num_frames} frames from workspace...')

# Parse the binary frame data
# Each frame appears to contain: pressure readings (floats) + timestamp + other data
# Frame structure (84 bytes): likely 4 pressure channels (4 floats = 16 bytes) + timestamp (4 bytes) + other data

frame_data_list = []
time_samples = []

for frame_idx in range(min(num_frames, 10000)):  # Limit to 10000 frames for now
    start_byte = frame_idx * frame_size
    end_byte = start_byte + frame_size
    
    frame_bytes = workspace.flat[start_byte:end_byte].tobytes()
    
    try:
        # Try multiple unpack formats to find valid data
        # Format 1: 4 floats + uint32 + padding
        values_1 = struct.unpack('<ffffI' + 'B'*(frame_size-20), frame_bytes)
        
        # Format 2: uint16 array (10 channels of 16-bit ADC data)
        values_2 = struct.unpack('<' + 'H'*42, frame_bytes[:84])  # 42 uint16s = 84 bytes
        
        # Use format that gives reasonable pressure values (-200 to 100 cmH2O)
        # Try the uint16 format as it's more likely for ADC data
        if len(values_2) >= 4:
            # Assume first 4 uint16 values are our pressure channels
            # Apply gains and offsets if needed
            pressure_ch0 = float(values_2[0])
            pressure_ch1 = float(values_2[1])
            pressure_ch2 = float(values_2[2])
            pressure_ch3 = float(values_2[3])
            
            # Filter: keep non-zero, reasonable values
            if abs(pressure_ch0) < 10000 or abs(pressure_ch1) < 10000:  # Basic validity check
                frame_data_list.append([pressure_ch0, pressure_ch1, pressure_ch2, pressure_ch3, frame_idx])
                
    except (struct.error, ValueError):
        continue

if not frame_data_list:
    print('ERROR: Could not extract valid frame data')
    sys.exit(2)

frame_array = np.array(frame_data_list)
print(f'Extracted {len(frame_data_list)} valid frames')
print(f'Sample frame values (first 5):')
print(frame_array[:5])
print()

# Convert raw ADC values to pressure using gains and offsets
# Try different conversion formula: (ADC_value - offset) / gain
# This is more typical for ADC conversions
gains_arr = np.atleast_1d(gains)
offsets_arr = np.atleast_1d(offsets)

for ch in range(4):
    if ch < len(gains_arr) and ch < len(offsets_arr):
        # Try formula: (ADC - offset) / gain
        frame_array[:, ch] = (frame_array[:, ch] - offsets_arr[ch]) / gains_arr[ch]

print('After conversion with formula (ADC - offset) / gain:')
print(f'Channel 0 range: [{frame_array[:, 0].min():.2f}, {frame_array[:, 0].max():.2f}]')
print(f'Channel 1 range: [{frame_array[:, 1].min():.2f}, {frame_array[:, 1].max():.2f}]')
print()

# Create output: Time (sample index), Pressure Ch0, Ch1, Ch2, Ch3, SetPoint
time_array = np.arange(len(frame_data_list))
csv_data = np.column_stack([
    time_array,
    frame_array[:, 0],  # Pressure channel 0
    frame_array[:, 1],  # Pressure channel 1
    frame_array[:, 2],  # Pressure channel 2
    frame_array[:, 3],  # Pressure channel 3
    np.full_like(time_array, set_point, dtype=float)
])

col_names = ['SampleIndex', 'Pressure_Ch0', 'Pressure_Ch1', 'Pressure_Ch2', 'Pressure_Ch3', 'SetPoint']

print('Writing CSV to', csv_path)
header_str = ','.join(col_names)
np.savetxt(csv_path, csv_data, delimiter=',', header=header_str, comments='', fmt='%.6f')
print('CSV saved:', csv_path)
print(f'Done. Rows: {csv_data.shape[0]}, Columns: {csv_data.shape[1]}')
