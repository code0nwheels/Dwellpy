# Dwellpy Build Information

## Executable Location
- Windows: dist/Dwellpy/Dwellpy.exe
- The entire 'dist/Dwellpy' folder needs to be distributed together

## Distribution
1. Zip the entire 'dist/Dwellpy' folder
2. Users extract and run Dwellpy.exe
3. No Python installation required on target machine

## Files Included
- All Python dependencies
- PyQt6 GUI framework  
- pynput mouse control
- Application assets and documentation

## Troubleshooting
- If antivirus flags it: Add exception (common with PyInstaller)
- If it won't start: Run from command line to see error messages
- Missing DLLs: Ensure all dependencies were bundled correctly

## Build Environment
- Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)]
- Platform: win32
