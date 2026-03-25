import os
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import DASHBOARD_PATH

class CSVHandler(FileSystemEventHandler):
    def __init__(self, dashboard_path):
        self.dashboard_path = Path(dashboard_path)
        self.dashboard_data_path = self.dashboard_path / "data"  # Assuming dashboard has a data folder

        # Create dashboard data directory if it doesn't exist
        self.dashboard_data_path.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() == '.csv':
            # Wait for file to be fully written (check if size is stable)
            self.wait_for_file_stable(file_path)
            self.move_csv_to_dashboard(file_path)

    def wait_for_file_stable(self, file_path, timeout=5):
        """Wait for file to be fully written by checking if size is stable"""
        initial_size = -1
        stable_count = 0
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                current_size = file_path.stat().st_size
                if current_size == initial_size:
                    stable_count += 1
                    if stable_count >= 3:  # File size stable for 3 checks
                        break
                else:
                    initial_size = current_size
                    stable_count = 0
                time.sleep(0.1)  # Check every 100ms
            except (OSError, FileNotFoundError):
                time.sleep(0.1)  # File might not be accessible yet

    def move_csv_to_dashboard(self, csv_file):
        try:
            # Copy to dashboard data directory
            destination = self.dashboard_data_path / csv_file.name
            shutil.copy2(csv_file, destination)

            print(f"Moved {csv_file.name} to dashboard data directory: {destination}")

            # Optional: Notify dashboard to refresh (if it has a refresh endpoint)
            # self.notify_dashboard_refresh(csv_file.name)

        except Exception as e:
            print(f"Error moving {csv_file.name}: {e}")

    def notify_dashboard_refresh(self, filename):
        # If your dashboard has an API endpoint to refresh data, implement here
        # For example, if it's a local web server:
        # import requests
        # requests.post('http://localhost:3000/api/refresh', json={'file': filename})
        pass

def start_watching(conversion_dirs, dashboard_path):
    """Start watching multiple conversion directories for CSV files"""
    observer = Observer()

    for conv_dir in conversion_dirs:
        conv_path = Path(conv_dir)
        if conv_path.exists():
            handler = CSVHandler(dashboard_path)
            observer.schedule(handler, str(conv_path), recursive=False)
            print(f"Watching {conv_path} for CSV files...")
        else:
            print(f"Warning: Conversion directory {conv_path} does not exist")

    observer.start()
    print("File watcher started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("File watcher stopped.")

    observer.join()

if __name__ == "__main__":
    # Configuration loaded from config.py
    CONVERSION_DIRS = [
        "Sleep Signal Conversion Scripting",
        "Sleep Stats Conversion Scripting",
        "Pump Signal Conversion Scripting"
    ]

    # Convert relative paths to absolute
    script_dir = Path(__file__).parent
    abs_conversion_dirs = [script_dir / d for d in CONVERSION_DIRS]

    print("CSV File Auto-Mover for Dashboard Integration")
    print("=" * 50)
    print(f"Dashboard path: {DASHBOARD_PATH}")
    print(f"Watching directories: {[str(d) for d in abs_conversion_dirs]}")
    print()

    start_watching(abs_conversion_dirs, DASHBOARD_PATH)