from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']

# Frame 9 is explicitly labeled 'trapPressure' 
frame_9 = frames[9, 3][0]

print('=== FRAME 9: trapPressure ===')
print(f'Range: min={np.min(frame_9):.2f}, max={np.max(frame_9):.2f}, mean={np.mean(frame_9):.2f}')
print(f'Std: {np.std(frame_9):.2f}')

# Chunk analysis
n_chunks = 20
chunk_size = len(frame_9) // n_chunks
chunk_means = []
for i in range(n_chunks):
    start = i * chunk_size
    end = start + chunk_size if i < n_chunks - 1 else len(frame_9)
    chunk_means.append(np.mean(frame_9[start:end]))

chunk_means = np.array(chunk_means)
trend = chunk_means[-1] - chunk_means[0]

print(f'\nChunk analysis (20 chunks):')
for i in range(0, n_chunks, 5):
    print(f'  Chunk {i:2d}: {chunk_means[i]:7.2f}')
print(f'  ...')
print(f'  Chunk {n_chunks-1:2d}: {chunk_means[-1]:7.2f}')

print(f'\nTrend: {chunk_means[0]:.2f} → {chunk_means[-1]:.2f} (Δ{trend:+.2f})')
print(f'First 20 samples: {frame_9[:20]}')
print(f'Last 20 samples: {frame_9[-20:]}')

# Compare with frame 8 (oralPressure)
frame_8 = frames[8, 3][0]
print(f'\n=== COMPARISON: Frame 8 vs Frame 9 ===')
print(f'Frame 8 (oralPressure):   {np.min(frame_8):.2f} to {np.max(frame_8):.2f}, mean={np.mean(frame_8):.2f}')
print(f'Frame 9 (trapPressure):   {np.min(frame_9):.2f} to {np.max(frame_9):.2f}, mean={np.mean(frame_9):.2f}')
print(f'Are they identical? {np.allclose(frame_8, frame_9)}')

# If frame 9 is the wrong one too, check if there's a way to get the expected uptrend
# Maybe we need to look at difference or derivative?
print(f'\n=== TRYING ALTERNATIVE SIGNALS ===')

# Check frame 20 (controlEffortRaw)
frame_20 = frames[20, 3][0]
chunk_means_20 = []
for i in range(n_chunks):
    start = i * chunk_size
    end = start + chunk_size if i < n_chunks - 1 else len(frame_20)
    chunk_means_20.append(np.mean(frame_20[start:end]))
chunk_means_20 = np.array(chunk_means_20)
trend_20 = chunk_means_20[-1] - chunk_means_20[0]
print(f'Frame 20 (controlEffortRaw): {np.min(frame_20):.2f} to {np.max(frame_20):.2f}')
print(f'  Trend: {chunk_means_20[0]:.2f} → {chunk_means_20[-1]:.2f} (Δ{trend_20:+.2f})')
