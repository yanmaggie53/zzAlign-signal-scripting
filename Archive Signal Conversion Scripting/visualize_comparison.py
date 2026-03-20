import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Load both CSV files
actual_csv = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s_actual.csv')
interpolated_csv = Path(r'C:\Users\MITOSA\Downloads\PN018-CUP-20250815-02h12m47s.csv')

# Load actual data
actual_data = np.genfromtxt(actual_csv, delimiter=',', skip_header=1)
print(f'Actual data shape: {actual_data.shape}')
print(f'Actual data first 5 rows:')
print(actual_data[:5])
print()

# Load interpolated data
interpolated_data = np.genfromtxt(interpolated_csv, delimiter=',', skip_header=1)
print(f'Interpolated data shape: {interpolated_data.shape}')
print(f'Interpolated data first 5 rows:')
print(interpolated_data[:5])
print()

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Actual Data vs Interpolated Data Comparison', fontsize=16, fontweight='bold')

# Plot 1: Actual data - Pressure Ch0 (Saliva Trap)
ax = axes[0, 0]
ax.plot(actual_data[:, 0], actual_data[:, 1], 'b.-', label='Ch0 (Saliva Trap)', linewidth=1, markersize=3)
ax.set_xlabel('Sample Index')
ax.set_ylabel('Pressure (cmH2O)')
ax.set_title('Actual Data - Pressure Channel 0')
ax.grid(True, alpha=0.3)
ax.legend()

# Plot 2: Actual data - Pressure Ch1 (Oral)
ax = axes[0, 1]
ax.plot(actual_data[:, 0], actual_data[:, 2], 'r.-', label='Ch1 (Oral)', linewidth=1, markersize=3)
ax.axhline(y=actual_data[0, 5], color='g', linestyle='--', label='Set Point', linewidth=1)
ax.set_xlabel('Sample Index')
ax.set_ylabel('Pressure (cmH2O)')
ax.set_title('Actual Data - Pressure Channel 1 + Set Point')
ax.grid(True, alpha=0.3)
ax.legend()

# Plot 3: Interpolated data - Ch0 vs Ch1
ax = axes[1, 0]
ax.plot(interpolated_data[:, 0], interpolated_data[:, 1], 'b.-', label='Saliva Trap', linewidth=2, markersize=6)
ax.plot(interpolated_data[:, 0], interpolated_data[:, 2], 'r.-', label='Oral', linewidth=2, markersize=6)
ax.axhline(y=interpolated_data[0, 5], color='g', linestyle='--', label='Set Point', linewidth=2)
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Pressure (cmH2O)')
ax.set_title('Interpolated Data - 30 Second View')
ax.grid(True, alpha=0.3)
ax.legend()

# Plot 4: Comparison - First 100 samples of actual vs downsampled
ax = axes[1, 1]
# Downsample actual data to 30 points to match interpolated data length
downsample_factor = len(actual_data) // len(interpolated_data)
actual_downsampled = actual_data[::downsample_factor, :]
ax.plot(actual_downsampled[:30, 0], actual_downsampled[:30, 1], 'b-o', label='Actual (downsampled)', linewidth=1, markersize=5)
ax.plot(interpolated_data[:, 0], interpolated_data[:, 1], 'r--s', label='Interpolated', linewidth=1.5, markersize=5, alpha=0.7)
ax.set_xlabel('Time')
ax.set_ylabel('Saliva Trap Pressure (cmH2O)')
ax.set_title('Data Comparison - Saliva Trap Pressure')
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
output_path = Path(r'C:\Users\MITOSA\Downloads\data_comparison.png')
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f'Visualization saved to {output_path}')

# Print statistics
print('\n=== Data Statistics ===')
print(f'Actual data - Ch0 range: [{actual_data[:, 1].min():.2f}, {actual_data[:, 1].max():.2f}]')
print(f'Actual data - Ch1 range: [{actual_data[:, 2].min():.2f}, {actual_data[:, 2].max():.2f}]')
print(f'Interpolated data - Ch0 range: [{interpolated_data[:, 1].min():.2f}, {interpolated_data[:, 1].max():.2f}]')
print(f'Interpolated data - Ch1 range: [{interpolated_data[:, 2].min():.2f}, {interpolated_data[:, 2].max():.2f}]')
