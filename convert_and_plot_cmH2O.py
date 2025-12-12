from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates

# Paths
interpolated_in = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.csv')
actual_in = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s_actual.csv')
interpolated_out = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s_interpolated_cmH2O.csv')
actual_out = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s_actual_cmH2O.csv')
plot_out = Path(r'C:\Users\MITOSA\Downloads\data_comparison_cmH2O.png')

# Read CSVs (skip header)
interp = np.genfromtxt(interpolated_in, delimiter=',', skip_header=1)
act = np.genfromtxt(actual_in, delimiter=',', skip_header=1)

# Column convention assumed: [time, SalivaTrap, Oral, Ch2, Ch3, SetPoint]
# Convert / clip to requested ranges
# Saliva trap: 0 to 100 cmH2O
# Oral pressure: 50 to -250 cmH2O (note reversed range)

# For interpolated (synthetic) - ensure in cmH2O and clip
interp_clipped = interp.copy()
if interp_clipped.size == 0:
    raise SystemExit('Interpolated CSV not found or empty')

# Clip saliva (col 1)
interp_clipped[:,1] = np.clip(interp_clipped[:,1], 0.0, 100.0)
# Clip oral (col 2) to [-250, 50]
interp_clipped[:,2] = np.clip(interp_clipped[:,2], -250.0, 50.0)

# For actual - values might be in ADC-derived units; we will treat them as already converted
act_clipped = act.copy()
if act_clipped.size == 0:
    raise SystemExit('Actual CSV not found or empty')

# If actual CSV has SampleIndex as first column and pressures in cols 1,2
# Clip
act_clipped[:,1] = np.clip(act_clipped[:,1], 0.0, 100.0)
act_clipped[:,2] = np.clip(act_clipped[:,2], -250.0, 50.0)

# Save clipped files with headers
h_interp = 'Time_s,SalivaTrapPressure_cmH2O,OralPressure_cmH2O,Channel2,Channel3,SetPoint_cmH2O'
np.savetxt(interpolated_out, interp_clipped, delimiter=',', header=h_interp, comments='', fmt='%.6f')

h_act = 'SampleIndex,Pressure_Ch0_cmH2O,Pressure_Ch1_cmH2O,Pressure_Ch2_cmH2O,Pressure_Ch3_cmH2O,SetPoint_cmH2O'
np.savetxt(actual_out, act_clipped, delimiter=',', header=h_act, comments='', fmt='%.6f')

# Plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Actual vs Interpolated (cmH2O, requested ranges)', fontsize=14)

# Create datetime x-axis spanning 02:00 - 08:00 on the current date
start_dt = dt.datetime(2025, 12, 10, 2, 0, 0)
end_dt = dt.datetime(2025, 12, 10, 8, 0, 0)

# Map sample indices / seconds to datetimes
def samples_to_datetimes(sample_indices, start=start_dt):
    return [start + dt.timedelta(seconds=float(s)) for s in sample_indices]

actual_times = samples_to_datetimes(act_clipped[:, 0])
interp_times = samples_to_datetimes(interp_clipped[:, 0])

# Actual - Saliva Trap
ax = axes[0,0]
ax.plot(actual_times, act_clipped[:,1], '.', label='Actual SalivaTrap')
ax.set_xlabel('Time')
ax.set_ylabel('Saliva Trap (cmH2O)')
ax.set_ylim(0, 100)
ax.set_title('Actual: Saliva Trap (0 → 100 cmH2O)')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

# Actual - Oral Pressure
ax = axes[0,1]
ax.plot(actual_times, act_clipped[:,2], '.', label='Actual Oral', color='tab:red')
ax.set_xlabel('Time')
ax.set_ylabel('Oral Pressure (cmH2O)')
ax.set_ylim(50, -250)
ax.set_title('Actual: Oral Pressure (50 → -250 cmH2O)')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

# Interpolated - Saliva Trap
ax = axes[1,0]
ax.plot(interp_times, interp_clipped[:,1], '-o', label='Interpolated SalivaTrap')
ax.set_xlabel('Time')
ax.set_ylabel('Saliva Trap (cmH2O)')
ax.set_ylim(0, 100)
ax.set_title('Interpolated: Saliva Trap (0 → 100 cmH2O)')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

# Interpolated - Oral Pressure
ax = axes[1,1]
ax.plot(interp_times, interp_clipped[:,2], '-o', label='Interpolated Oral', color='tab:red')
ax.set_xlabel('Time')
ax.set_ylabel('Oral Pressure (cmH2O)')
ax.set_ylim(50, -250)
ax.set_title('Interpolated: Oral Pressure (50 → -250 cmH2O)')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(2,9), interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(start_dt, end_dt)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(plot_out, dpi=150, bbox_inches='tight')
print('Wrote:', interpolated_out)
print('Wrote:', actual_out)
print('Plot saved to:', plot_out)
