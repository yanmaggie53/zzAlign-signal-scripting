# Configuration for CSV Auto-Mover
# Update the DASHBOARD_PATH to point to your Cursor dashboard project directory

DASHBOARD_PATH = r"C:\Users\MITOSA\Maggie Stuff (EverythingDashboard)\zzAlign-patient-dashboard\prototype 4"

# The script will automatically watch these subdirectories for new CSV files:
# - Sleep Signal Conversion Scripting
# - Sleep Stats Conversion Scripting
# - Pump Signal Conversion Scripting

# When a CSV file is created in any of these directories, it will be automatically
# copied to: DASHBOARD_PATH/data/

# To run the auto-mover:
# python csv_auto_mover.py