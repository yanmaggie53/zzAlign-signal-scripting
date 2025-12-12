from pathlib import Path
import numpy as np
import scipy.io as sio

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')
mat_data = sio.loadmat(str(mat_path), squeeze_me=True)

print('=== Detailed Inspection ===\n')

# Get the None key which contains the metadata
if None in mat_data:
    none_obj = mat_data[None]
    print(f'None object: {none_obj}')
    print(f'  s0 (pump name): {none_obj["s0"]}')
    print(f'  s1 (device): {none_obj["s1"]}')
    print(f'  s2 (datetime): {none_obj["s2"]}')
    arr = none_obj['arr']
    print(f'  arr shape: {arr.shape}, dtype: {arr.dtype}')
    print(f'  arr values:\n{arr}')
    print()

# Now look at frames
if 'frames' in mat_data:
    frames = mat_data['frames']
    print(f'frames shape: {frames.shape}, dtype: {frames.dtype}')
    print(f'frames[0]: {frames[0]}')  # First row
    print(f'\nAll frames:')
    for i, row in enumerate(frames):
        print(f'  Row {i}: {row}')
    print()

# And header
if 'header' in mat_data:
    header = mat_data['header']
    print(f'header shape: {header.shape}, dtype: {header.dtype}')
    print(f'\nAll header rows:')
    for i, row in enumerate(header):
        print(f'  Row {i}: {row}')
