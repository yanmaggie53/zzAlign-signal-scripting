from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

try:
    mat_data = loadmat(mat_path, squeeze_me=False)
except Exception as e:
    print(f'Error loading MAT: {e}')
    exit(1)

print('=== All keys in MAT ===')
for key in sorted(mat_data.keys()):
    val = mat_data[key]
    if isinstance(val, np.ndarray):
        print(f'{key}: ndarray shape={val.shape}, dtype={val.dtype}')
    else:
        print(f'{key}: {type(val).__name__}')

# Try to access the data structure
print('\n=== Trying to extract measurements/data ===')

# Common keys to look for
for key in ['measurements', 'Measurements', 'data', 'Data', 'frames', 'Frames']:
    if key in mat_data:
        val = mat_data[key]
        print(f'Found {key}:')
        print(f'  Type: {type(val).__name__}')
        if isinstance(val, np.ndarray):
            print(f'  Shape: {val.shape}, dtype: {val.dtype}')
            # If it's a structured array or object array, inspect
            if val.dtype.names:
                print(f'  Structured array fields: {val.dtype.names}')
            # Print sample
            if val.size > 0:
                try:
                    if val.ndim == 1:
                        print(f'  First element: {val[0]}')
                    elif val.ndim == 2:
                        print(f'  First row: {val[0, :]}')
                        print(f'  Shape summary: {val.shape}')
                except:
                    pass

# Check if there's a structured array or object with measurement data
print('\n=== Checking for any structured/object arrays ===')
for key in mat_data.keys():
    val = mat_data[key]
    if isinstance(val, np.ndarray):
        if val.dtype == object or (val.dtype.names is not None):
            print(f'{key}: {val.shape}, dtype={val.dtype}')
            if val.size > 0:
                try:
                    elem = val.flat[0]
                    print(f'  First element type: {type(elem).__name__}')
                    if isinstance(elem, np.ndarray):
                        print(f'    ndarray shape: {elem.shape}')
                except:
                    pass
