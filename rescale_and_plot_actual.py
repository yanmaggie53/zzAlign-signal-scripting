from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates

# Inputs
interp_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.csv')
actual_path = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s_actual.csv')
plot_out = Path(r'C:\Users\MITOSA\Downloads\data_comparison_rescaled_cmH2O.png')
plot_zoom_out = Path(r'C:\Users\MITOSA\Downloads\data_comparison_rescaled_cmH2O_zoom.png')

# Known full duration (user-provided): 5 hours 20 minutes 34 seconds
total_seconds = 5*3600 + 20*60 + 34
print('Total duration (s):', total_seconds)

# Read files
interp = np.genfromtxt(interp_path, delimiter=',', skip_header=1)
act = np.genfromtxt(actual_path, delimiter=',', skip_header=1)

# Basic checks
if interp.size == 0 or act.size == 0:
    raise SystemExit('Missing input CSVs')

# Start datetime for plotting
start_dt = dt.datetime(2025, 12, 10, 2, 0, 0)
end_dt = start_dt + dt.timedelta(seconds=6*3600)  # 6 hours to 08:00

# Map interpolated times: assume col0 is seconds already
interp_times = [start_dt + dt.timedelta(seconds=float(s)) for s in interp[:,0]]

# Map actual times by rescaling to full recording duration
n = act.shape[0]
if n <= 1:
    raise SystemExit('Actual CSV has too few rows to rescale')
act_indices = act[:,0]
# Normalize 0..1
act_norm = (act_indices - act_indices.min()) / float(act_indices.max() - act_indices.min())
act_times = [start_dt + dt.timedelta(seconds=float(x) * total_seconds) for x in act_norm]

# Clip pressures (same as before)
interp_clipped = interp.copy()
interp_clipped[:,1] = np.clip(interp_clipped[:,1], 0.0, 100.0)
interp_clipped[:,2] = np.clip(interp_clipped[:,2], -250.0, 50.0)

act_clipped = act.copy()
act_clipped[:,1] = np.clip(act_clipped[:,1], 0.0, 100.0)
act_clipped[:,2] = np.clip(act_clipped[:,2], -250.0, 50.0)

# Plot full 6-hour comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Actual (rescaled) vs Interpolated (cmH2O) — rescaled to full recording', fontsize=14)

# Actual - Saliva
ax = axes[0,0]
ax.plot(act_times, act_clipped[:,1], '.', ms=2, label='Actual (rescaled)')
ax.set_ylabel('Saliva Trap (cmH2O)')
ax.set_ylim(0, 100)
ax.set_title('Actual: Saliva Trap (0 → 100)')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

# Actual - Oral
ax = axes[0,1]
ax.plot(act_times, act_clipped[:,2], '.', ms=2, color='tab:red')
ax.set_ylabel('Oral Pressure (cmH2O)')
ax.set_ylim(50, -250)
ax.set_title('Actual: Oral Pressure (50 → -250)')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

# Interp - Saliva
ax = axes[1,0]
ax.plot(interp_times, interp_clipped[:,1], '-o', label='Interpolated', markersize=4)
ax.set_ylabel('Saliva Trap (cmH2O)')
ax.set_ylim(0, 100)
ax.set_title('Interpolated: Saliva Trap')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

# Interp - Oral
ax = axes[1,1]
ax.plot(interp_times, interp_clipped[:,2], '-o', color='tab:red', markersize=4)
ax.set_ylabel('Oral Pressure (cmH2O)')
ax.set_ylim(50, -250)
ax.set_title('Interpolated: Oral Pressure')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(plot_out, dpi=150, bbox_inches='tight')
print('Saved:', plot_out)

# Also save a zoom around 02:00-02:30 for close visual comparison
zoom_end = start_dt + dt.timedelta(seconds=30)
fig2, axes2 = plt.subplots(2, 1, figsize=(12, 6))
axes2[0].plot(act_times, act_clipped[:,1], '.', ms=2, label='Actual (rescaled)')
axes2[0].plot(interp_times, interp_clipped[:,1], '-o', markersize=6, label='Interpolated')
axes2[0].set_xlim(start_dt, zoom_end)
axes2[0].set_ylim(0, 100)
axes2[0].set_title('Saliva Trap — zoom 02:00–02:00:30')
axes2[0].legend()
axes2[0].grid(True)

axes2[1].plot(act_times, act_clipped[:,2], '.', ms=2, color='tab:red')
axes2[1].plot(interp_times, interp_clipped[:,2], '-o', color='tab:red', markersize=6)
axes2[1].set_xlim(start_dt, zoom_end)
axes2[1].set_ylim(50, -250)
axes2[1].set_title('Oral Pressure — zoom 02:00–02:00:30')
axes2[1].grid(True)

plt.tight_layout()
plt.savefig(plot_zoom_out, dpi=150, bbox_inches='tight')
print('Saved zoom:', plot_zoom_out)
