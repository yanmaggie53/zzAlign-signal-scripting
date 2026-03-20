from pathlib import Path
import numpy as np
import scipy.io as sio
import struct

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')
mat_data = sio.loadmat(str(mat_path), squeeze_me=True)

# Get header info
header = mat_data['header']
print('Header Information:')
print('  defaultSetPoint:', header[5, 2])  # Set point
print('  gains:', header[11, 2])  # Gains for 4 channels
print('  offsets:', header[12, 2])  # Offsets for 4 channels
print()

# Get frames
frames = mat_data['frames']
print(f'Frames shape: {frames.shape}')
print('Frame info:')
for i, row in enumerate(frames):
    print(f'  Row {i}: {row}')
print()

# The function workspace might contain the actual binary data
if '__function_workspace__' in mat_data:
    workspace = mat_data['__function_workspace__']
    print(f'Function workspace shape: {workspace.shape}')
    print(f'Function workspace size (bytes): {workspace.nbytes}')
    print(f'First 100 bytes (hex): {workspace.flat[:100].tobytes().hex()}')
    print()
    
    # Try to interpret as raw binary data
    # Based on frame size of 84 bytes and frameSz header, 
    # each frame should be 84 bytes
    frame_size = 84
    num_frames = len(workspace.flat) // frame_size
    print(f'Estimated number of frames: {num_frames}')
    
    # Try to parse a frame
    if num_frames > 0:
        frame_data = workspace.flat[:frame_size]
        print(f'\nFirst frame (84 bytes):')
        print(f'  Raw hex: {frame_data.tobytes().hex()}')
        
        # Try to interpret as 4 uint16 + 1 uint32 (time) + padding
        # Or similar structure based on sensor count
        try:
            # Unpack as floats (4 channels of pressure data + time)
            values = struct.unpack('ffffI' + 'B'*(frame_size-20), frame_data.tobytes())
            print(f'  As 4 floats + 1 uint32: {values[:5]}')
        except:
            print('  Could not unpack as floats')
