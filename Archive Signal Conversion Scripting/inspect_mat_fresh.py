from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

try:
    mat_data = loadmat(mat_path, squeeze_me=True)
except Exception as e:
    print(f'Error loading MAT: {e}')
    import traceback
    traceback.print_exc()
    exit(1)

print('=== MAT file keys ===')
for key in sorted(mat_data.keys()):
    val = mat_data[key]
    if isinstance(val, np.ndarray):
        print(f'{key}: ndarray shape={val.shape}, dtype={val.dtype}')
        # Show first few values if 1D or 2D with reasonable size
        if val.size <= 20:
            print(f'  values: {val}')
        elif val.ndim == 1:
            print(f'  first 5: {val[:5]}, last 5: {val[-5:]}')
        elif val.ndim == 2 and val.shape[1] <= 10:
            print(f'  shape {val.shape}, first 3 rows:\n{val[:3]}')
    else:
        print(f'{key}: {type(val).__name__}')

# Check for common pressure/pump signal keys
print('\n=== Looking for pressure/pump signals ===')
for key in mat_data.keys():
    key_lower = key.lower()
    if any(x in key_lower for x in ['pres', 'oral', 'saliva', 'trap', 'pump', 'flow', 'signal', 'data', 'ch', 'channel']):
        print(f'MATCH: {key}')
