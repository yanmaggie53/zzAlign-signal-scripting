import scipy.io
import numpy as np
import math
import sys
from pprint import pprint

mat_path = r"C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.mat"

try:
    m = scipy.io.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
except Exception as e:
    print(f"ERROR loading mat: {e}")
    sys.exit(2)

# find a key named 'frames' (case-insensitive)
frames_key = None
for k in m.keys():
    if k.lower() == 'frames':
        frames_key = k
        break
if frames_key is None:
    print('No "frames" key found in MAT file. Keys:')
    print(list(m.keys()))
    sys.exit(3)

frames = m[frames_key]
print(f"Found frames object under key '{frames_key}' with type {type(frames)}")

# If frames is 2D array-like, iterate rows
try:
    shape = frames.shape
except Exception:
    shape = None
print('frames.shape =', shape)

# helper
def is_string(x):
    return isinstance(x, (str, bytes, np.str_, np.bytes_))

def try_numeric_stats(a):
    try:
        arr = np.asarray(a, dtype=float)
        if arr.size == 0:
            return None
        mn = float(np.nanmin(arr))
        mx = float(np.nanmax(arr))
        mean = float(np.nanmean(arr))
        return (mn, mx, mean, arr.shape)
    except Exception:
        return None

heuristics = []

# iterate rows
rows = frames.shape[0] if hasattr(frames, 'shape') and len(frames.shape) >= 1 else 0
for i in range(rows):
    row = frames[i]
    # row may be 1D array of objects
    strings = []
    numeric_stats = []
    reprs = []
    # if row is scalar, wrap
    try:
        iter(row)
        cells = list(row)
    except Exception:
        cells = [row]
    for c in cells:
        if is_string(c):
            try:
                s = c.decode() if isinstance(c, bytes) else str(c)
            except Exception:
                s = repr(c)
            strings.append(s)
        else:
            stats = try_numeric_stats(c)
            if stats is not None:
                numeric_stats.append(stats)
            # record brief repr
            try:
                r = repr(c)
            except Exception:
                r = str(type(c))
            reprs.append(r[:200])
    # pick label candidates
    joined = ' | '.join(strings)
    label = 'unknown'
    jl = joined.lower()
    if 'oral' in jl:
        label = 'oralPressure'
    elif 'trap' in jl or 'saliva' in jl:
        label = 'trapPressure'
    elif 'controller' in jl or 'error' in jl:
        label = 'controllerError'
    elif 'setpoint' in jl or 'set point' in jl or 'setpoint' in jl:
        label = 'setPoint'
    elif 'mv' in jl or 'mv' in jl or 'milli' in jl or 'adc' in jl:
        label = 'rawADC/mV'

    print('\n-- Frame', i, '--')
    print('strings found:', strings)
    if numeric_stats:
        for si, s in enumerate(numeric_stats):
            mn, mx, mean, shape = s
            print(f' numeric array {si}: shape={shape} min={mn:.4f} max={mx:.4f} mean={mean:.4f}')
    else:
        print(' numeric array: none or non-numeric')
    print('repr samples:', reprs[:3])
    print('heuristic label:', label)

    heuristics.append((i, label, strings, numeric_stats))

# Print compact mapping
print('\n\nCompact mapping (frame index -> heuristic label):')
for t in heuristics:
    i, label, strings, numeric_stats = t
    info = f"Frame {i}: {label}"
    if strings:
        info += f" (strings: {strings})"
    if numeric_stats:
        mn, mx, mean, shape = numeric_stats[0]
        info += f" -> numeric min={mn:.3f} max={mx:.3f} mean={mean:.3f} shape={shape}"
    print(info)

print('\nDone.')
