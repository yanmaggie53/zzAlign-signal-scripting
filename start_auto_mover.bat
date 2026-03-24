@echo off
echo Starting CSV Auto-Mover for Dashboard Integration...
echo.
echo This will monitor your conversion folders and automatically move
echo any new CSV files to your dashboard's data directory.
echo.
echo Press Ctrl+C to stop monitoring.
echo.
python csv_auto_mover.py
pause