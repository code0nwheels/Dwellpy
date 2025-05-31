#!/bin/bash
# Dwellpy Linux Uninstall Script - Updated Version
# Removes Dwellpy installation and auto-start configuration
# Usage: curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-uninstall.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check what's installed
check_installation() {
    log_info "Checking Dwellpy installation..."
    
    FOUND_FILES=()
    
    # Check XDG autostart entry
    if [ -f ~/.config/autostart/dwellpy.desktop ]; then
        FOUND_FILES+=("Auto-start entry: ~/.config/autostart/dwellpy.desktop")
    fi
    
    # Check desktop menu entry
    if [ -f ~/.local/share/applications/dwellpy.desktop ]; then
        FOUND_FILES+=("Desktop menu entry: ~/.local/share/applications/dwellpy.desktop")
    fi
    
    # Check launcher script
    if [ -f ~/.local/bin/dwellpy ]; then
        FOUND_FILES+=("Launcher script: ~/.local/bin/dwellpy")
    fi
    
    # Check source directory
    if [ -d ~/.local/dwellpy ]; then
        FOUND_FILES+=("Source code: ~/.local/dwellpy/")
    fi
    
    # Check if Dwellpy is currently running
    if pgrep -f "python3 -m dwellpy.main" >/dev/null 2>&1; then
        FOUND_FILES+=("Running Dwellpy process")
    fi
    
    if [ ${#FOUND_FILES[@]} -eq 0 ]; then
        log_info "No Dwellpy installation found"
        exit 0
    fi
    
    echo
    log_info "Found these Dwellpy components:"
    for item in "${FOUND_FILES[@]}"; do
        echo "  - $item"
    done
    echo
}

# Stop running Dwellpy processes
stop_dwellpy() {
    log_info "Stopping Dwellpy processes..."
    
    # Check if Dwellpy is running
    if pgrep -f "python3 -m dwellpy.main" >/dev/null 2>&1; then
        log_info "Found running Dwellpy process, stopping it..."
        pkill -f "python3 -m dwellpy.main" || true
        sleep 2
        
        # Force kill if still running
        if pgrep -f "python3 -m dwellpy.main" >/dev/null 2>&1; then
            log_warning "Force stopping Dwellpy..."
            pkill -9 -f "python3 -m dwellpy.main" || true
        fi
        
        log_success "Dwellpy processes stopped"
    else
        log_info "No running Dwellpy processes found"
    fi
}

# Remove XDG autostart entry
remove_autostart() {
    if [ -f ~/.config/autostart/dwellpy.desktop ]; then
        log_info "Removing auto-start configuration..."
        rm ~/.config/autostart/dwellpy.desktop
        log_success "Auto-start entry removed"
    fi
}

# Remove desktop menu entry
remove_desktop_entry() {
    if [ -f ~/.local/share/applications/dwellpy.desktop ]; then
        log_info "Removing desktop menu entry..."
        rm ~/.local/share/applications/dwellpy.desktop
        
        # Update desktop database if available
        if command -v update-desktop-database >/dev/null 2>&1; then
            update-desktop-database ~/.local/share/applications 2>/dev/null || true
        fi
        
        log_success "Desktop menu entry removed"
    fi
}

# Remove launcher script
remove_launcher() {
    if [ -f ~/.local/bin/dwellpy ]; then
        log_info "Removing launcher script..."
        rm ~/.local/bin/dwellpy
        log_success "Launcher script removed"
    fi
}

# Remove source directory
remove_source() {
    if [ -d ~/.local/dwellpy ]; then
        log_info "Removing source code directory..."
        rm -rf ~/.local/dwellpy
        log_success "Source code directory removed"
    fi
}

# Check and optionally remove PATH modification
check_path_modification() {
    if grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc 2>/dev/null; then
        echo
        log_warning "Found PATH modification in ~/.bashrc"
        echo "This line was added during installation:"
        echo '  export PATH="$HOME/.local/bin:$PATH"'
        echo
        echo "Note: This PATH modification may be used by other applications"
        echo "Only remove it if you're sure no other programs need ~/.local/bin"
        echo
        read -p "Remove this line from ~/.bashrc? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Create backup
            cp ~/.bashrc ~/.bashrc.dwellpy-backup
            # Remove the line
            grep -v 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc.dwellpy-backup > ~/.bashrc
            log_success "PATH modification removed from ~/.bashrc"
            log_info "Backup saved as ~/.bashrc.dwellpy-backup"
        else
            log_info "Keeping PATH modification in ~/.bashrc"
        fi
    fi
}

# Clean up empty directories
cleanup_empty_dirs() {
    log_info "Cleaning up empty directories..."
    
    # Remove ~/.local/bin if empty
    if [ -d ~/.local/bin ] && [ -z "$(ls -A ~/.local/bin)" ]; then
        rmdir ~/.local/bin
        log_info "Removed empty ~/.local/bin directory"
    fi
    
    # Remove ~/.config/autostart if empty
    if [ -d ~/.config/autostart ] && [ -z "$(ls -A ~/.config/autostart)" ]; then
        rmdir ~/.config/autostart
        log_info "Removed empty ~/.config/autostart directory"
    fi
    
    # Remove ~/.local/share/applications if empty
    if [ -d ~/.local/share/applications ] && [ -z "$(ls -A ~/.local/share/applications)" ]; then
        rmdir ~/.local/share/applications
        log_info "Removed empty ~/.local/share/applications directory"
        
        # Remove ~/.local/share if empty
        if [ -d ~/.local/share ] && [ -z "$(ls -A ~/.local/share)" ]; then
            rmdir ~/.local/share
            log_info "Removed empty ~/.local/share directory"
        fi
    fi
}

# Show post-uninstall information
show_completion_info() {
    echo
    echo "========================================="
    log_success "Uninstallation completed!"
    echo "========================================="
    echo
    log_info "All Dwellpy components have been removed:"
    log_info "✅ Auto-start configuration removed"
    log_info "✅ Desktop menu entry removed"  
    log_info "✅ Launcher script removed"
    log_info "✅ Source code removed"
    log_info "✅ Running processes stopped"
    echo
    log_info "What was NOT removed (if present):"
    log_info "• ~/.bashrc PATH modification (if you chose to keep it)"
    log_info "• Other applications in ~/.local/bin/"
    log_info "• System Python packages"
    echo
    log_info "If you want to reinstall Dwellpy later:"
    log_info "  curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/install.sh | bash"
    echo
    log_info "You may need to restart your terminal for PATH changes to take effect"
    echo
}

# Main uninstall function
main() {
    echo "========================================="
    echo "      Dwellpy Linux Uninstaller"
    echo "========================================="
    echo
    
    check_installation
    
    echo "⚠️  This will completely remove Dwellpy from your system"
    echo "Including auto-start configuration, launcher, and source code"
    echo
    read -p "Do you want to uninstall Dwellpy? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstall cancelled"
        exit 0
    fi
    
    echo
    log_info "Starting uninstallation..."
    echo
    
    # Remove components in logical order
    stop_dwellpy               # Stop running processes first
    remove_autostart          # Remove auto-start
    remove_desktop_entry      # Remove from menus
    remove_launcher           # Remove launcher script
    remove_source             # Remove source code
    check_path_modification   # Ask about PATH modification
    cleanup_empty_dirs        # Clean up empty directories
    
    show_completion_info
}

# Run main function
main "$@"