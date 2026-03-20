from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

# Load without squeeze to preserve structure
mat_data = loadmat(mat_path, squeeze_me=False)

print('=== MAT FILE CONTENTS (ALL KEYS) ===')
print(f'Total keys: {len(mat_data.keys())}')
print()

for key in sorted(mat_data.keys()):
    val = mat_data[key]
    print(f'{key}:')
    print(f'  Type: {type(val).__name__}')
    if isinstance(val, np.ndarray):
        print(f'  Shape: {val.shape}')
        print(f'  Dtype: {val.dtype}')
        if val.dtype == object:
            print(f'  Object array contents:')
            for i, elem in enumerate(val.flat[:5]):
                print(f'    [{i}]: {type(elem).__name__} - {str(elem)[:100]}')
    print()

# Check for any embedded binary or image data
print('\n=== CHECKING FOR EMBEDDED IMAGES/BINARY DATA ===')
for key in mat_data.keys():
    val = mat_data[key]
    if isinstance(val, np.ndarray):
        # Check if it's bytes-like or image-like
        if val.dtype == np.uint8 and val.size > 100:
            # Could be PNG/image data
            # PNG files start with magic bytes: 137 80 78 71 (0x89504E47)
            if val.ndim == 1 and len(val) > 8:
                if val[0] == 137 and val[1] == 80 and val[2] == 78 and val[3] == 71:
                    print(f'✓ FOUND PNG DATA in key "{key}"')
                    print(f'  Size: {val.size} bytes')
            elif val.ndim > 1:
                # Could be image matrix (uint8 2D or 3D)
                print(f'  {key}: uint8 array, shape={val.shape} (could be image)')
        elif val.dtype in [np.uint32, np.uint16] and val.size > 1000:
            print(f'  {key}: {val.dtype}, shape={val.shape}')

print('\nNote: If PNG is embedded, it should have magic bytes 137,80,78,71 at the start.')
print('Or it might be stored as a base64 string or other encoding in a variable.')
