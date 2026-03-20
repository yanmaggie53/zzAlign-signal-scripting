from pathlib import Path
import numpy as np

src = Path(r'C:\Users\MITOSA\Downloads\N008N1NoxCSV.csv')
dst = Path(r'C:\Users\MITOSA\Downloads\N008N1NoxCSV_300rows.csv')

if not src.exists():
    print('Source CSV not found:', src)
    raise SystemExit(2)

print('Loading CSV (this may take a moment)...')
# Use genfromtxt to preserve header reading easily
with src.open('r', encoding='utf-8') as f:
    header = f.readline().strip()
# Load numeric data (skip header)
data = np.genfromtxt(src, delimiter=',', skip_header=1)
if data.size == 0:
    print('No numeric data found in', src)
    raise SystemExit(3)

n_rows = data.shape[0]
print(f'Original rows: {n_rows}')

n_target = 300
if n_target >= n_rows:
    print('Target rows >= original rows; copying original file to', dst)
    np.savetxt(dst, data, delimiter=',', header=header, comments='', fmt='%.6f')
    raise SystemExit(0)

# Choose evenly spaced indices across the range including first and last
indices = np.linspace(0, n_rows - 1, n_target).round().astype(int)
indices = np.unique(indices)  # ensure uniqueness
# If uniqueness reduced count, pad by selecting nearest remaining
if indices.size < n_target:
    all_idx = np.arange(n_rows)
    remaining = np.setdiff1d(all_idx, indices)
    need = n_target - indices.size
    add = np.round(np.linspace(0, remaining.size - 1, need)).astype(int)
    indices = np.concatenate([indices, remaining[add]])
    indices = np.sort(indices)

print('Selected indices range:', indices[0], 'to', indices[-1], 'count=', indices.size)

out = data[indices, :]
print('Writing downsampled CSV to', dst)
np.savetxt(dst, out, delimiter=',', header=header, comments='', fmt='%.6f')
print('Done. Rows written:', out.shape[0])
