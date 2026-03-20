from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']
header = mat_data['header']

# Extract key header values
gains = header[11, 3].flatten() if header[11, 3].size > 0 else np.array([])
offsets = header[12, 3].flatten() if header[12, 3].size > 0 else np.array([])
default_setpoint = float(header[5, 3][0]) if header[5, 3].size > 0 else -60
print('=== KEY HEADER INFO ===')
print(f'Gains: {gains}')
print(f'Offsets: {offsets}')
print(f'Default SetPoint: {default_setpoint} cmH2O')
print()

# Extract measurement data from frames
measurements = []
for frame_idx in range(frames.shape[0]):
    frame_row = frames[frame_idx]
    # Column 3 typically contains the actual measurement data
    meas_data = frame_row[3]
    if isinstance(meas_data, np.ndarray) and meas_data.dtype in [np.float32, np.float64, np.int16, np.uint16, np.int32, np.uint32]:
        measurements.append(meas_data.flatten())
        print(f'Frame {frame_idx}: shape={meas_data.shape}, dtype={meas_data.dtype}, size={meas_data.size}')
        if meas_data.size > 0:
            print(f'  first 5: {meas_data.flat[:5]}')
            if meas_data.dtype in [np.float32, np.float64]:
                print(f'  min={np.min(meas_data):.2f}, max={np.max(meas_data):.2f}, mean={np.mean(meas_data):.2f}')

if measurements:
    all_meas = np.concatenate(measurements)
    print(f'\n=== Total measurements ===')
    print(f'Total samples: {len(all_meas)}')
    print(f'Data range: {np.min(all_meas):.2f} to {np.max(all_meas):.2f}')
    print(f'Data mean: {np.mean(all_meas):.2f}')
    
    # Try to split into 4 channels
    if len(all_meas) % 4 == 0:
        num_samples_per_ch = len(all_meas) // 4
        print(f'\nAssuming 4 channels interleaved: {num_samples_per_ch} samples per channel')
        for ch in range(4):
            ch_data = all_meas[ch::4]
            print(f'  CH{ch}: min={np.min(ch_data):.2f}, max={np.max(ch_data):.2f}, mean={np.mean(ch_data):.2f}')
