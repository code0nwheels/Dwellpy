#!/bin/bash
# macOS DMG Creation Script for Dwellpy
# Usage: ./create_dmg.sh

set -e

echo "Dwellpy DMG Creator"
echo "=================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "ERROR: This script must be run on macOS"
    exit 1
fi

# Check if we're in the right directory
if [ ! -d "dwellpy" ]; then
    echo "ERROR: Run this script from the project root directory"
    echo "   (where the 'dwellpy' folder is located)"
    exit 1
fi

# Check if build exists
if [ ! -d "dist/Dwellpy.app" ]; then
    echo "ERROR: No app bundle found in dist/"
    echo "   Run the build script first: python utils/build_executable.py"
    exit 1
fi

# Run the DMG creation script
echo "Creating DMG installer..."
python3 utils/create_macos_dmg.py

echo ""
echo "DMG creation complete!"
echo "Check the dist/ folder for your installer."
