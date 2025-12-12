from pathlib import Path
import numpy as np
import mne
from scipy.signal import resample_poly
import sys

# Input EDF and outputs
edf_path = Path(r'C:\Users\MITOSA\Downloads\N018TN2Signal.edf')
csv_path = Path(r'C:\Users\MITOSA\Downloads\N018TN2Signal_6signals.csv')
position_summary_path = Path(r'C:\Users\MITOSA\Downloads\N018TN2Signal_position_summary.csv')

if not edf_path.exists():
    print('ERROR: EDF file not found at', edf_path)
    sys.exit(2)

# Parameters
TARGET_SFREQ = 10.0  # Hz
BLOCK_SECONDS = 30   # how many seconds per read block

print('Opening EDF (no preload)...')
raw = mne.io.read_raw_edf(str(edf_path), preload=False, verbose='ERROR')
orig_sfreq = float(raw.info['sfreq'])
n_channels_total = raw.info['nchan']
print(f'Original sampling rate: {orig_sfreq} Hz, channels: {n_channels_total}')

# Requested signals (EDF channel name -> output column name)
# These names were observed previously in the EDF; if slightly different, we try case-insensitive contains match.
requested = [
    ('Nasal Pressure', 'NasalFlow_cmH2O'),
    ('Saturation', 'SpO2_pct'),
    ('Activity', 'Activity_gps'),
    ('PosAngle', 'PosAngle_deg'),
    ('Audio Volume dB', 'AudioVolume_dB'),
    ('cRIP Flow', 'cRIP_Flow'),
]

ch_names = raw.info['ch_names']
name_to_idx = {name: i for i, name in enumerate(ch_names)}

selected_idxs = []
output_colnames = ['time']
for name, outname in requested:
    if name in name_to_idx:
        selected_idxs.append(name_to_idx[name])
        output_colnames.append(outname)
    else:
        # try case-insensitive contains
        found = None
        lname = name.lower()
        for ch in ch_names:
            if lname in ch.lower():
                found = ch
                break
        if found:
            selected_idxs.append(name_to_idx[found])
            output_colnames.append(outname)
            print(f"Mapped requested '{name}' -> '{found}'")
        else:
            print(f"ERROR: Required channel '{name}' not found in EDF channels")
            sys.exit(3)

print('Selected channels:')
for idx, col in zip(selected_idxs, output_colnames[1:]):
    print(f' - {col}: index {idx} (EDF name: {ch_names[idx]})')

n_times = raw.n_times
block_samples = int(BLOCK_SECONDS * orig_sfreq)
if block_samples <= 0:
    block_samples = int(orig_sfreq * 10)

ratio = orig_sfreq / TARGET_SFREQ
use_integer_decimation = abs(round(ratio) - ratio) < 1e-8
if use_integer_decimation:
    decim = int(round(ratio))
    print(f'Using integer decimation by factor {decim}')
else:
    from fractions import Fraction
    frac = Fraction(orig_sfreq / TARGET_SFREQ).limit_denominator(10000)
    up = frac.numerator
    down = frac.denominator
    print(f'Using resample_poly with up={up}, down={down}')

# Buffers
channel_blocks = [[] for _ in selected_idxs]

print('Beginning streaming read/resample...')
for start in range(0, n_times, block_samples):
    stop = min(n_times, start + block_samples)
    data = raw.get_data(picks=selected_idxs, start=start, stop=stop)
    if data.size == 0:
        continue
    # data shape: (n_selected, n_samples_block)
    if use_integer_decimation:
        data_dec = data[:, ::decim]
    else:
        # use resample_poly to get close to target sfreq
        data_dec = resample_poly(data, up=up, down=down, axis=1)
    for i in range(len(selected_idxs)):
        channel_blocks[i].append(data_dec[i])
    processed = min(stop, n_times)
    print(f'Processed samples {processed}/{n_times} (time {processed/orig_sfreq:.1f}s)')

print('Concatenating blocks...')
channel_data = [np.concatenate(b) if len(b) else np.array([], dtype=float) for b in channel_blocks]

if len(channel_data) == 0 or channel_data[0].size == 0:
    print('No data extracted. Exiting.')
    sys.exit(4)

n_samples = channel_data[0].shape[0]
# ensure equal length
for i in range(len(channel_data)):
    if channel_data[i].shape[0] != n_samples:
        min_len = min(n_samples, channel_data[i].shape[0])
        channel_data[i] = channel_data[i][:min_len]
        n_samples = min_len

# times vector
times = np.arange(n_samples) / TARGET_SFREQ

# Build output matrix: time + selected channels
out_matrix = np.vstack([times] + channel_data).T
header = ','.join(output_colnames)
print('Writing CSV to', csv_path)
np.savetxt(csv_path, out_matrix, delimiter=',', header=header, comments='', fmt='%.6f')
print('CSV saved:', csv_path)

# Compute sleeping position summary from PosAngle channel
# Assumption: PosAngle is in degrees; classification thresholds:
#  - supine: angle in [-45, 45]
#  - left: angle > 45
#  - right: angle < -45
pos_idx = None
try:
    pos_idx = output_colnames.index('PosAngle_deg') - 1
except ValueError:
    pos_idx = None

position_summary = {'supine_seconds': 0.0, 'left_seconds': 0.0, 'right_seconds': 0.0}
if pos_idx is not None:
    pos_values = channel_data[pos_idx]
    # classify per sample
    sup_mask = (pos_values >= -45.0) & (pos_values <= 45.0)
    left_mask = pos_values > 45.0
    right_mask = pos_values < -45.0
    position_summary['supine_seconds'] = float(np.sum(sup_mask) / TARGET_SFREQ)
    position_summary['left_seconds'] = float(np.sum(left_mask) / TARGET_SFREQ)
    position_summary['right_seconds'] = float(np.sum(right_mask) / TARGET_SFREQ)

print('Writing position summary to', position_summary_path)
with open(position_summary_path, 'w') as f:
    f.write('position,seconds\n')
    f.write(f"supine,{position_summary['supine_seconds']:.3f}\n")
    f.write(f"left,{position_summary['left_seconds']:.3f}\n")
    f.write(f"right,{position_summary['right_seconds']:.3f}\n")
print('Position summary saved:', position_summary_path)

print('Done. Rows:', n_samples, 'Columns:', len(output_colnames))
