from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']

print('=== SCANNING ALL FRAMES FOR UPTRENDING SALIVA TRAP ===\n')

# Divide each frame into chunks to detect trend
n_chunks = 20
for frame_idx in range(frames.shape[0]):
    frame_row = frames[frame_idx]
    frame_label = frame_row[0]
    frame_data = frame_row[3]
    
    if not isinstance(frame_data, np.ndarray):
        continue
    
    if frame_data.dtype not in [np.float32, np.float64]:
        continue
    
    data = frame_data.flatten()
    
    # Skip if too small or all zeros/constant
    if len(data) < 1000 or np.std(data) < 0.01:
        continue
    
    # Calculate trend
    chunk_size = len(data) // n_chunks
    chunk_means = []
    for i in range(n_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < n_chunks - 1 else len(data)
        chunk_means.append(np.mean(data[start:end]))
    
    trend = chunk_means[-1] - chunk_means[0]
    first_mean = chunk_means[0]
    last_mean = chunk_means[-1]
    
    # Look for uptrending data that starts around 60 and goes to 80
    if trend > 5 and first_mean > 50 and last_mean > 70:
        print(f'✓ UPTREND MATCH: Frame {frame_idx}')
        print(f'  Label: {frame_label}')
        print(f'  Range: {np.min(data):.2f} to {np.max(data):.2f}')
        print(f'  First chunk: {chunk_means[0]:.2f}, Last chunk: {chunk_means[-1]:.2f}')
        print(f'  Trend: +{trend:.2f} cmH2O')
        print(f'  First 10 samples: {data[:10]}')
        print()
    elif trend > 5:  # Any uptrend
        print(f'  Uptrend: Frame {frame_idx} ({frame_label}): {first_mean:.2f} → {last_mean:.2f} (Δ{trend:+.2f})')
    elif trend < -5:  # Any downtrend
        print(f'  Downtrend: Frame {frame_idx} ({frame_label}): {first_mean:.2f} → {last_mean:.2f} (Δ{trend:+.2f})')
    else:  # Flat or small trend
        if np.std(data) > 1:  # Has variation but flat trend
            print(f'  Flat: Frame {frame_idx} ({frame_label}): mean={np.mean(data):.2f}, std={np.std(data):.2f}')
