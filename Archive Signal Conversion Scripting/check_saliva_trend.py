from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']

# Extract frame 18 (saliva trap)
frame_18 = frames[18, 3][0]

print('=== SALIVA TRAP PRESSURE (Frame 18) ANALYSIS ===')
print(f'Total samples: {len(frame_18)}')
print(f'Data range: min={np.min(frame_18):.2f}, max={np.max(frame_18):.2f}')
print(f'Mean: {np.mean(frame_18):.2f}')
print(f'Median: {np.median(frame_18):.2f}')

# Check trend by dividing into chunks
n_chunks = 100
chunk_size = len(frame_18) // n_chunks
chunk_means = []
for i in range(n_chunks):
    start = i * chunk_size
    end = start + chunk_size if i < n_chunks - 1 else len(frame_18)
    chunk_mean = np.mean(frame_18[start:end])
    chunk_means.append(chunk_mean)
    if i % 10 == 0 or i == n_chunks - 1:
        print(f'  Chunk {i:3d} (samples {start:7d}-{end:7d}): mean={chunk_mean:7.2f}')

# Calculate overall trend
chunk_means = np.array(chunk_means)
trend = chunk_means[-1] - chunk_means[0]
print(f'\nOverall trend: {trend:.2f} cmH2O (from first to last chunk)')
print(f'  First chunk mean: {chunk_means[0]:.2f}')
print(f'  Last chunk mean: {chunk_means[-1]:.2f}')

# Check for anomalies
print(f'\n=== DATA QUALITY ===')
nan_count = np.sum(np.isnan(frame_18))
inf_count = np.sum(np.isinf(frame_18))
print(f'NaN values: {nan_count}')
print(f'Inf values: {inf_count}')
print(f'Valid values: {len(frame_18) - nan_count - inf_count}')

# Show first and last 50 samples
print(f'\n=== FIRST 50 SAMPLES ===')
print(frame_18[:50])
print(f'\n=== LAST 50 SAMPLES ===')
print(frame_18[-50:])

# Check if there's a step change or mode shift
print(f'\n=== PERCENTILE ANALYSIS ===')
for p in [1, 5, 25, 50, 75, 95, 99]:
    print(f'{p:2d}%: {np.percentile(frame_18, p):7.2f}')
