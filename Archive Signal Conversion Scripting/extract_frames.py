from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']
header = mat_data['header']

print(f'frames shape: {frames.shape}')
print(f'header shape: {header.shape}')

# Extract header info
print('\n=== HEADER (16 rows, 4 cols) ===')
for i, row in enumerate(header):
    key = row[0]
    val = row[3]
    if isinstance(val, np.ndarray):
        if val.size == 1:
            print(f'{i:2d}. {str(key):30s} = {val[0]}')
        else:
            print(f'{i:2d}. {str(key):30s} = ndarray{val.shape}')
    else:
        print(f'{i:2d}. {str(key):30s} = {val}')

# Extract frame data
print(f'\n=== FRAMES (27 frames, 4 columns) ===')
total_samples = 0
all_data = []

for frame_idx in range(frames.shape[0]):
    frame_row = frames[frame_idx]
    print(f'\nFrame {frame_idx}:')
    for col_idx in range(4):
        col_data = frame_row[col_idx]
        if isinstance(col_data, np.ndarray):
            print(f'  col {col_idx}: shape={col_data.shape}, dtype={col_data.dtype}')
            if col_data.size > 0:
                print(f'      first 5: {col_data.flat[:5]}')
                print(f'      min={np.nanmin(col_data):.2f}, max={np.nanmax(col_data):.2f}, mean={np.nanmean(col_data):.2f}')
                total_samples += col_data.size
        else:
            print(f'  col {col_idx}: {type(col_data).__name__}')

print(f'\n=== SUMMARY ===')
print(f'Total samples across all frames: {total_samples}')
print(f'Expected: 576305 samples over 5h20m34s = 19234s -> {576305/19234:.1f} Hz')
