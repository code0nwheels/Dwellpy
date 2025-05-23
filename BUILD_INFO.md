# Dwellpy Build Information

## Executable Location
- **One-file build**: `dist/Dwellpy.exe` (Windows) or `dist/Dwellpy` (Linux/Mac)
- Ready to distribute - single file, no dependencies needed

## Distribution
1. Simply distribute the single executable file
2. Users run the .exe file directly
3. No Python installation required on target machine

## Features Included
- All Python dependencies bundled
- PyQt6 GUI framework  
- pynput mouse control library
- Application configuration and documentation

## Build Environment
- System: Windows 11
- Python: 3.13.3
- PyInstaller: Latest version
- Target: Single executable file

## Troubleshooting
- **Antivirus detection**: Some antivirus may flag PyInstaller executables as suspicious
- **Slow startup**: First run may take a few seconds to extract bundled files
- **Debugging**: Change `console=True` in dwellpy.spec and rebuild to see console output
- **UAC prompts**: Windows UAC enabled for mouse control access

## Usage
Double-click the executable to run Dwellpy. The application will create its settings file in the same directory as the executable.
