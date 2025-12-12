from scipy.io import loadmat
from pathlib import Path
import numpy as np
import datetime as dt

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']
header = mat_data['header']

# Extract key header values
gains = header[11, 3].flatten()
offsets = header[12, 3].flatten()

# Extract frames - each frame has 576305 samples
# Frame 8 (oralPressure): already converted to cmH2O (min=-80.64, max=-0.23, mean=-58.44)
# Frame 9 (trapPressure): saliva trap pressure
# Frame 18 (controllerError): controller error signal to display
# Frame 11 (setpoint): setpoint (-60 cmH2O)

frame_8 = frames[8, 3][0]  # Oral pressure
frame_9 = frames[9, 3][0]  # Trap pressure (saliva trap)
frame_18 = frames[18, 3][0]  # Controller error
frame_11 = frames[11, 3][0]  # Setpoint

print('=== SIGNAL CANDIDATES ===')
print('Frame 8 (oralPressure):')
print(f'  Stats: min={np.min(frame_8):.2f}, max={np.max(frame_8):.2f}, mean={np.mean(frame_8):.2f}')
print(f'  First 10: {frame_8[:10]}')

print('\nFrame 9 (trapPressure):')
print(f'  Stats: min={np.min(frame_9):.2f}, max={np.max(frame_9):.2f}, mean={np.mean(frame_9):.2f}')
print(f'  First 10: {frame_9[:10]}')

print('\nFrame 18 (controllerError):')
print(f'  Stats: min={np.min(frame_18):.2f}, max={np.max(frame_18):.2f}, mean={np.mean(frame_18):.2f}')
print(f'  First 10: {frame_18[:10]}')

print('\nFrame 11 (setpoint):')
print(f'  all values = {frame_11[0]:.1f} (should be -60)')

# Resample to ~30 second window for quick display (if 576305 samples over 19234 s, that's ~30 Hz)
total_samples = len(frame_8)
total_seconds = 5*3600 + 20*60 + 34  # 19234 seconds
sfreq_est = total_samples / total_seconds
print(f'\n=== SAMPLING INFO ===')
print(f'Total samples: {total_samples}')
print(f'Total duration: {total_seconds} seconds')
print(f'Estimated sampling frequency: {sfreq_est:.2f} Hz')

# Downsample to 10 Hz for CSV (factor = sfreq_est / 10)
ds_factor = int(sfreq_est / 10.0 + 0.5)
print(f'Downsample factor (to 10 Hz): {ds_factor}')

trap_pressure_10hz = frame_9[::ds_factor]
oral_pressure_10hz = frame_8[::ds_factor]
controller_error_10hz = frame_18[::ds_factor]
setpoint_10hz = frame_11[::ds_factor]

print(f'\nAfter downsampling to 10 Hz:')
print(f'  Oral pressure: {len(oral_pressure_10hz)} samples')
print(f'  Trap pressure: {len(trap_pressure_10hz)} samples')
print(f'  Controller error: {len(controller_error_10hz)} samples')
print(f'  Setpoint: {len(setpoint_10hz)} samples')

# Create time array (map to 02:00 - 08:00 spanning full duration)
start_dt = dt.datetime(2025, 12, 10, 2, 0, 0)
times_10hz = np.arange(len(oral_pressure_10hz)) * (1.0 / 10.0)  # seconds since start

# Write CSV
csv_out = Path(r'C:\Users\MITOSA\Downloads\PN018_pump_data.csv')
# Ensure all arrays same length
min_len = min(len(oral_pressure_10hz), len(trap_pressure_10hz), len(controller_error_10hz), len(setpoint_10hz))
csv_data = np.column_stack((
    times_10hz[:min_len],
    trap_pressure_10hz[:min_len],
    oral_pressure_10hz[:min_len],
    controller_error_10hz[:min_len],
    setpoint_10hz[:min_len]
))

header_str = 'Time_s,TrapPressure_cmH2O,OralPressure_cmH2O,ControllerError_cmH2O,Setpoint_cmH2O'
np.savetxt(csv_out, csv_data, delimiter=',', header=header_str, comments='', fmt='%.4f')
print(f'\nCSV saved: {csv_out}')
print(f'  Shape: {csv_data.shape}')
print(f'  Duration: {times_10hz[min_len-1]:.1f} seconds = {times_10hz[min_len-1]/3600:.2f} hours')
