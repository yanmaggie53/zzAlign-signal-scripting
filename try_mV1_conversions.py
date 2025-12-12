from scipy.io import loadmat
from pathlib import Path
import numpy as np

mat_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat')

mat_data = loadmat(mat_path, squeeze_me=False)
frames = mat_data['frames']
header = mat_data['header']

gains = header[11, 3].flatten()
offsets = header[12, 3].flatten()

print('=== TRYING DIFFERENT CONVERSION FORMULAS FOR mV1 (Frame 5) ===')

frame_5_raw = frames[4, 3][0]  # mV1 raw ADC

# Try different formulas
print(f'\nRaw ADC (Frame 5): min={np.min(frame_5_raw):.0f}, max={np.max(frame_5_raw):.0f}, mean={np.mean(frame_5_raw):.0f}')

# Formula 1: (ADC - offset) / gain
converted_1 = (frame_5_raw - offsets[1]) / gains[1]
print(f'\nFormula 1: (ADC - offset) / gain')
print(f'  Range: {np.min(converted_1):.2f} to {np.max(converted_1):.2f}, mean={np.mean(converted_1):.2f}')

# Formula 2: ADC / gain - offset
converted_2 = frame_5_raw / gains[1] - offsets[1]
print(f'\nFormula 2: ADC / gain - offset')
print(f'  Range: {np.min(converted_2):.2f} to {np.max(converted_2):.2f}, mean={np.mean(converted_2):.2f}')

# Formula 3: (ADC - offset/gain)
converted_3 = frame_5_raw - offsets[1] / gains[1]
print(f'\nFormula 3: ADC - offset/gain')
print(f'  Range: {np.min(converted_3):.2f} to {np.max(converted_3):.2f}, mean={np.mean(converted_3):.2f}')

# Formula 4: offset - ADC (inverted)
converted_4 = offsets[1] - frame_5_raw
print(f'\nFormula 4: offset - ADC (inverted)')
print(f'  Range: {np.min(converted_4):.2f} to {np.max(converted_4):.2f}, mean={np.mean(converted_4):.2f}')

# Formula 5: (offset - ADC) / gain (inverted + scaled)
converted_5 = (offsets[1] - frame_5_raw) / gains[1]
print(f'\nFormula 5: (offset - ADC) / gain (inverted+scaled)')
print(f'  Range: {np.min(converted_5):.2f} to {np.max(converted_5):.2f}, mean={np.mean(converted_5):.2f}')

# Check trends for each
for formula_num, data_converted in enumerate([converted_1, converted_2, converted_3, converted_4, converted_5], 1):
    n_chunks = 20
    chunk_size = len(data_converted) // n_chunks
    chunk_means = [np.mean(data_converted[i*chunk_size:(i+1)*chunk_size]) for i in range(n_chunks)]
    trend = chunk_means[-1] - chunk_means[0]
    print(f'  Formula {formula_num}: {chunk_means[0]:.2f} → {chunk_means[-1]:.2f} (Δ{trend:+.2f})', end='')
    if trend > 5 and 50 < chunk_means[0] < 70 and 70 < chunk_means[-1] < 90:
        print(' ✓ MATCHES UPTREND 60→80')
    else:
        print()
