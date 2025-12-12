from pathlib import Path
import numpy as np
import scipy.io as sio
import sys

# Load the MAT file
mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

# Try loading with different options
print('=== Loading with struct_as_record=True, squeeze_me=False ===\n')
mat_data = sio.loadmat(str(mat_path), struct_as_record=True, squeeze_me=False)

for key in sorted(mat_data.keys()):
    if key.startswith('__'):
        continue
    val = mat_data[key]
    if isinstance(val, np.ndarray):
        print(f'{key}:')
        print(f'  Shape: {val.shape}')
        print(f'  Dtype: {val.dtype}')
        
        # If structured array, show fields
        if val.dtype.names:
            print(f'  Fields: {val.dtype.names}')
            # Print first element
            if val.size > 0:
                print(f'  First element:')
                for fname in val.dtype.names:
                    fval = val[fname].flat[0]
                    if isinstance(fval, np.ndarray):
                        print(f'    {fname}: array {fval.shape}')
                    else:
                        print(f'    {fname}: {fval}')
        print()
