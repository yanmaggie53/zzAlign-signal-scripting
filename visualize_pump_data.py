from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates

# Load the CSV
csv_path = Path(r'C:\Users\MITOSA\Downloads\PN018_pump_data.csv')
data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)

times_s = data[:, 0]
trap_pressure = data[:, 1]
oral_pressure = data[:, 2]
controller_error = data[:, 3]
setpoint = data[:, 4]

print(f'Data shape: {data.shape}')
print(f'Time range: {times_s[0]:.1f} to {times_s[-1]:.1f} seconds ({times_s[-1]/3600:.2f} hours)')
print(f'Trap pressure range: {np.min(trap_pressure):.2f} to {np.max(trap_pressure):.2f} cmH2O')
print(f'Oral pressure range: {np.min(oral_pressure):.2f} to {np.max(oral_pressure):.2f} cmH2O')
print(f'Controller error range: {np.min(controller_error):.2f} to {np.max(controller_error):.2f} cmH2O')

# Map to 6-hour window (02:00 - 08:00)
start_dt = dt.datetime(2025, 12, 10, 2, 0, 0)
end_dt = dt.datetime(2025, 12, 10, 8, 0, 0)
six_hours_seconds = 6 * 3600

# Normalize times to 0..1, then scale to 6 hours
times_norm = times_s / times_s[-1]
times_mapped = times_norm * six_hours_seconds
times_dt = np.array([start_dt + dt.timedelta(seconds=float(t)) for t in times_mapped])

# Create figure with three subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
fig.suptitle('Pump Data: Trap Pressure, Oral Pressure with Setpoint, and Controller Error', fontsize=16, fontweight='bold')

# Subplot 1: Trap Pressure
ax1.plot(times_dt, trap_pressure, color='green', linewidth=0.8, label='Trap Pressure')
ax1.set_ylabel('Trap Pressure (cmH2O)', fontsize=12)
ax1.set_ylim(0, 100)
ax1.set_title('Trap Pressure (0 → 100 cmH2O)', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.set_xlim(start_dt, end_dt)
fig.autofmt_xdate()

# Subplot 2: Oral Pressure with Setpoint
ax2.plot(times_dt, oral_pressure, color='red', linewidth=0.8, label='Oral Pressure')
ax2.plot(times_dt, setpoint, color='black', linewidth=2, linestyle='--', label='Setpoint (-60 cmH2O)')
ax2.set_ylabel('Oral Pressure (cmH2O)', fontsize=12)
ax2.set_ylim(-250, 50)
ax2.set_title('Oral Pressure (-250 → 50 cmH2O) with Setpoint', fontsize=12)
ax2.legend(loc='upper right', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax2.set_xlim(start_dt, end_dt)
fig.autofmt_xdate()

# Subplot 3: Controller Error
ax3.plot(times_dt, controller_error, color='orange', linewidth=0.8, label='Controller Error')
ax3.set_ylabel('Controller Error (cmH2O)', fontsize=12)
ax3.set_xlabel('Time', fontsize=12)
ax3.set_title('Controller Error Signal', fontsize=12)
ax3.legend(loc='upper right', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax3.set_xlim(start_dt, end_dt)
fig.autofmt_xdate()

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig(Path(r'C:\Users\MITOSA\Downloads\pump_data_visualization.png'), dpi=150, bbox_inches='tight')
print('Visualization saved: C:\\Users\\MITOSA\\Downloads\\pump_data_visualization.png')

# Also create a zoomed version for the first 30 minutes
zoom_end_dt = start_dt + dt.timedelta(minutes=30)
mask_zoom = times_dt <= zoom_end_dt

fig_zoom, (ax1z, ax2z, ax3z) = plt.subplots(3, 1, figsize=(14, 12))
fig_zoom.suptitle('Pump Data — Zoom: First 30 minutes', fontsize=16, fontweight='bold')

ax1z.plot(times_dt[mask_zoom], trap_pressure[mask_zoom], 'o-', color='green', markersize=3, linewidth=1, label='Trap Pressure')
ax1z.set_ylabel('Trap Pressure (cmH2O)', fontsize=12)
ax1z.set_ylim(0, 100)
ax1z.set_title('Trap Pressure (0 → 100 cmH2O)', fontsize=12)
ax1z.grid(True, alpha=0.3)
ax1z.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
ax1z.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1z.set_xlim(start_dt, zoom_end_dt)
fig_zoom.autofmt_xdate()

ax2z.plot(times_dt[mask_zoom], oral_pressure[mask_zoom], 'o-', color='red', markersize=3, linewidth=1, label='Oral Pressure')
ax2z.plot(times_dt[mask_zoom], setpoint[mask_zoom], 'k--', linewidth=2, label='Setpoint')
ax2z.set_ylabel('Oral Pressure (cmH2O)', fontsize=12)
ax2z.set_ylim(-250, 50)
ax2z.set_title('Oral Pressure (-250 → 50 cmH2O) with Setpoint', fontsize=12)
ax2z.legend(loc='upper right', fontsize=10)
ax2z.grid(True, alpha=0.3)
ax2z.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
ax2z.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax2z.set_xlim(start_dt, zoom_end_dt)
fig_zoom.autofmt_xdate()

ax3z.plot(times_dt[mask_zoom], controller_error[mask_zoom], 'o-', color='orange', markersize=3, linewidth=1, label='Controller Error')
ax3z.set_ylabel('Controller Error (cmH2O)', fontsize=12)
ax3z.set_xlabel('Time', fontsize=12)
ax3z.set_title('Controller Error Signal', fontsize=12)
ax3z.legend(loc='upper right', fontsize=10)
ax3z.grid(True, alpha=0.3)
ax3z.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
ax3z.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax3z.set_xlim(start_dt, zoom_end_dt)
fig_zoom.autofmt_xdate()

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig(Path(r'C:\Users\MITOSA\Downloads\pump_data_visualization_zoom.png'), dpi=150, bbox_inches='tight')
print('Zoom visualization saved: C:\\Users\\MITOSA\\Downloads\\pump_data_visualization_zoom.png')
