from pathlib import Path
import numpy as np
import datetime as dt

interpolated_in = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.csv')
actual_in = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s_actual.csv')

start_dt = dt.datetime(2025, 12, 10, 2, 0, 0)
end_dt = dt.datetime(2025, 12, 10, 8, 0, 0)

print('Reading (may fail if files missing):', interpolated_in, actual_in)

for p, name in ((interpolated_in, 'interpolated'), (actual_in, 'actual')):
    try:
        data = np.genfromtxt(p, delimiter=',', skip_header=1)
    except Exception as e:
        print(f'ERROR reading {name}:', e)
        continue
    if data.size == 0:
        print(f'{name}: empty')
        continue
    print(f'--- {name} ---')
    print('shape:', data.shape)
    print('first 5 rows:')
    print(data[:5])
    col0 = data[:,0]
    print('col0 dtype:', col0.dtype)
    print('col0 min/max:', np.nanmin(col0), np.nanmax(col0))
    # Heuristic: are values integers stepping by 1?
    diffs = np.diff(col0)
    if np.all(np.isfinite(diffs)) and len(diffs)>0:
        med_diff = np.median(np.abs(diffs))
    else:
        med_diff = None
    print('median delta of col0 (abs):', med_diff)
    # Map to datetimes assuming col0 is seconds
    try:
        times = [start_dt + dt.timedelta(seconds=float(s)) for s in col0]
        print('mapped start/end datetimes:', times[0], times[-1])
        inside = sum(1 for t in times if start_dt <= t <= end_dt)
        print('rows inside 02:00-08:00 window:', inside, '/', len(times))
    except Exception as e:
        print('mapping to datetimes failed:', e)
    # Heuristic: are values small (e.g., 0..30) or large (e.g., sample indices)
    if np.nanmax(col0) > 1e4:
        print('col0 looks like large sample indices ( > 10k )')
    elif np.nanmax(col0) > 100:
        print('col0 looks like sample indices or seconds > 100s')
    else:
        print('col0 looks like small seconds (<=100s)')

print('Done')
