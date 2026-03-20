from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']
header = mat_data['header']

# Extract gains and offsets for conversion
gains = header[11, 3].flatten()
offsets = header[12, 3].flatten()
print('=== CALIBRATION ===')
print(f'Gains: {gains}')
print(f'Offsets: {offsets}')
print()

# Print all frame labels and basic stats
print('=== ALL FRAMES ===')
for frame_idx in range(frames.shape[0]):
    frame_row = frames[frame_idx]
    frame_label = frame_row[0][0] if isinstance(frame_row[0], np.ndarray) else frame_row[0]
    frame_data = frame_row[3]
    
    if not isinstance(frame_data, np.ndarray):
        print(f'Frame {frame_idx:2d}: {frame_label:30s} (not ndarray)')
        continue
    
    data = frame_data.flatten()
    if data.size == 0:
        print(f'Frame {frame_idx:2d}: {frame_label:30s} (empty)')
        continue
    
    # Skip string/object data
    if data.dtype.kind in ['U', 'O', 'S']:
        print(f'Frame {frame_idx:2d}: {frame_label:30s} (string/object type)')
        continue
    
    # Try to convert ADC → pressure if it looks like ADC data (mV0-3)
    if frame_label.startswith('mV'):
        try:
            ch_idx = int(frame_label[2])
            if ch_idx < len(gains) and ch_idx < len(offsets):
                gain = gains[ch_idx]
                offset = offsets[ch_idx]
                # Conversion: pressure = (ADC - offset) / gain
                data_converted = (data - offset) / gain
                print(f'Frame {frame_idx:2d}: {frame_label:30s} (ADC Ch{ch_idx} → cmH2O)')
                print(f'  Raw ADC: min={np.min(data):.0f}, max={np.max(data):.0f}, mean={np.mean(data):.0f}')
                print(f'  Converted: min={np.min(data_converted):.2f}, max={np.max(data_converted):.2f}, mean={np.mean(data_converted):.2f}')
                
                # Check trend
                n_chunks = 20
                chunk_size = len(data_converted) // n_chunks
                chunk_means = [np.mean(data_converted[i*chunk_size:(i+1)*chunk_size if i < n_chunks-1 else len(data_converted)]) for i in range(n_chunks)]
                trend = chunk_means[-1] - chunk_means[0]
                print(f'  Trend: {chunk_means[0]:.2f} → {chunk_means[-1]:.2f} (Δ{trend:+.2f})')
                print(f'  First 5 converted: {data_converted[:5]}')
                print()
        except:
            pass
    else:
        print(f'Frame {frame_idx:2d}: {frame_label:30s}')
        print(f'  dtype={data.dtype}, Range: {np.min(data):.2f} to {np.max(data):.2f}, mean={np.mean(data):.2f}')
        print()
