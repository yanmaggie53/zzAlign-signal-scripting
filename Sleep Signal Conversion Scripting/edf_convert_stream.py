from pathlib import Path
import numpy as np
import mne
from scipy.signal import resample_poly
import sys

edf_path = Path(r'C:\Users\MITOSA\Downloads\N008N1NoxEDF.edf')
csv_path = Path(r'C:\Users\MITOSA\Downloads\N008N1NoxCSV.csv')
events_path = Path(r'C:\Users\MITOSA\Downloads\N008N1Nox_apnea_events.csv')

if not edf_path.exists():
    print('ERROR: EDF file not found at', edf_path)
    sys.exit(2)

# Parameters
TARGET_SFREQ = 10.0  # Hz
BLOCK_SECONDS = 30   # how many seconds per read block
MIN_APNEA_SECONDS = 10.0
APNEA_THRESHOLD_FRACTION = 0.20

print('Opening EDF (no preload)...')
raw = mne.io.read_raw_edf(str(edf_path), preload=False, verbose='ERROR')
orig_sfreq = float(raw.info['sfreq'])
n_channels_total = raw.info['nchan']
print(f'Original sampling rate: {orig_sfreq} Hz, channels: {n_channels_total}')

# Requested mapping
requested = [
    ('Saturation', 'SpO2'),
    ('Pulse', 'HeartRate_bpm'),
    ('Nasal Pressure', 'NasalPressure'),
    ('Flow', 'Flow'),
    ('RIP Flow', 'RIPFlow'),
    ('PosAngle', 'PosAngle'),
    ('X Axis', 'X'),
    ('Y Axis', 'Y'),
    ('Z Axis', 'Z'),
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
combined_flow_blocks = []

# find flow positions in selected_idxs
flow_output_names = ['NasalPressure', 'Flow', 'RIPFlow']
flow_positions = [i for i, (_, outname) in enumerate(requested) if outname in flow_output_names]
# But selected_idxs order corresponds to requested order filtering; ensure positions map correctly
selected_output_names = [out for _, out in requested]
flow_positions = [i for i, out in enumerate(selected_output_names) if out in flow_output_names]

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
    # combined airflow envelope
    flow_arrays = []
    for pos_name in flow_output_names:
        try:
            pos_idx = output_colnames.index(pos_name) - 1  # subtract 1 because output_colnames has 'time' first
            if pos_idx >= 0 and pos_idx < data_dec.shape[0]:
                flow_arrays.append(np.abs(data_dec[pos_idx]))
        except ValueError:
            continue
    if len(flow_arrays) > 0:
        flow_stack = np.vstack(flow_arrays)
        combined = np.mean(flow_stack, axis=0)
    else:
        combined = np.zeros(data_dec.shape[1], dtype=float)
    combined_flow_blocks.append(combined)
    processed = min(stop, n_times)
    print(f'Processed samples {processed}/{n_times} (time {processed/orig_sfreq:.1f}s)')

print('Concatenating blocks...')
channel_data = [np.concatenate(b) if len(b) else np.array([], dtype=float) for b in channel_blocks]
combined_flow = np.concatenate(combined_flow_blocks) if len(combined_flow_blocks) else np.array([], dtype=float)

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
        combined_flow = combined_flow[:n_samples]

times = np.arange(n_samples) / TARGET_SFREQ

# apnea detection
apnea_events = []
if combined_flow.size > 0:
    baseline_rms = np.sqrt(np.mean(combined_flow ** 2))
    thresh = baseline_rms * APNEA_THRESHOLD_FRACTION
    print(f'Baseline RMS (flow): {baseline_rms:.6g}; threshold: {thresh:.6g}')
    mask = combined_flow < thresh
    in_event = False
    evt_start = None
    for i, v in enumerate(mask):
        if v and not in_event:
            in_event = True
            evt_start = i
        elif (not v) and in_event:
            in_event = False
            evt_end = i
            dur = (evt_end - evt_start) / TARGET_SFREQ
            if dur >= MIN_APNEA_SECONDS:
                apnea_events.append((evt_start / TARGET_SFREQ, dur))
    if in_event:
        evt_end = len(mask)
        dur = (evt_end - evt_start) / TARGET_SFREQ
        if dur >= MIN_APNEA_SECONDS:
            apnea_events.append((evt_start / TARGET_SFREQ, dur))

print(f'Found {len(apnea_events)} apnea events')

# write CSV
print('Writing CSV to', csv_path)
header = ','.join(output_colnames)
out_matrix = np.vstack([times] + channel_data).T
np.savetxt(csv_path, out_matrix, delimiter=',', header=header, comments='', fmt='%.6f')
print('CSV saved:', csv_path)

# write events
print('Writing events to', events_path)
with open(events_path, 'w') as f:
    f.write('onset_seconds,duration_seconds,method\n')
    for onset, dur in apnea_events:
        f.write(f'{onset:.3f},{dur:.3f},apnea_simple_threshold\n')
print('Events saved:', events_path)

print('Done. Rows:', n_samples, 'Columns:', len(output_colnames))
