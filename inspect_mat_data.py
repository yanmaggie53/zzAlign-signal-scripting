from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

try:
    mat_data = loadmat(mat_path, squeeze_me=True)
except Exception as e:
    print(f'Error loading MAT: {e}')
    exit(1)

# Inspect data and header
data = mat_data.get('data')
header = mat_data.get('header')

if data is None or header is None:
    print('Missing data or header')
    exit(1)

print(f'data shape: {data.shape}, dtype: {data.dtype}')
print(f'header shape: {header.shape}')

# Print header info (should contain gain/offset/labels)
print('\n=== HEADER ===')
if header.ndim == 2:
    for i, row in enumerate(header[:10]):  # First 10 rows
        print(f'header[{i}]: {row}')

# Print first 10 data rows to see raw values
print(f'\n=== First 10 data rows ===')
print('shape:', data[:10].shape)
if data.ndim == 2:
    for i in range(min(10, data.shape[0])):
        print(f'row {i}: {data[i]}')

# Print column statistics
print(f'\n=== Column statistics (all {data.shape[0]} rows) ===')
if data.ndim == 2:
    for col_idx in range(data.shape[1]):
        col_data = data[:, col_idx]
        print(f'col {col_idx}: min={np.nanmin(col_data):.2f}, max={np.nanmax(col_data):.2f}, mean={np.nanmean(col_data):.2f}')
        print(f'           first 3: {col_data[:3]}, last 3: {col_data[-3:]}')

# Try to find sampling frequency
print(f'\n=== Try to infer sampling frequency ===')
total_rows = data.shape[0]
print(f'Total samples: {total_rows}')
# Check count column (should be index 1 if it exists)
if data.ndim == 2 and data.shape[1] >= 2:
    col1 = data[:, 1]
    if np.allclose(col1, np.arange(total_rows)):
        print('Column 1 appears to be a sequential index.')
    print(f'Col 1 range: {col1[0]} to {col1[-1]}')

# Assume 576305 samples covers the full duration (5h 20m 34s = 19234 s)
if total_rows > 0:
    estimated_sfreq = total_rows / 19234.0
    print(f'If total duration is 5h20m34s (19234s), estimated sfreq = {estimated_sfreq:.2f} Hz')
    print(f'At that rate, ~1662 samples would be: {1662 / estimated_sfreq:.2f} seconds')
