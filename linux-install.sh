#!/bin/bash
# Enhanced Dwellpy Linux Install Script with Optional GUI Auto-Launch
# Downloads source code and installs Dwellpy with user choice for auto-start
# Usage: curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-install.sh | bash

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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        log_info "Run as a regular user - we'll ask for sudo when needed"
        exit 1
    fi
}

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
        VERSION=$(lsb_release -sr)
    else
        log_error "Cannot detect Linux distribution"
        exit 1
    fi
    
    log_info "Detected: $DISTRO $VERSION"
}

# Detect desktop environment
detect_desktop_environment() {
    if [ -n "$XDG_CURRENT_DESKTOP" ]; then
        DESKTOP_ENV="$XDG_CURRENT_DESKTOP"
    elif [ -n "$DESKTOP_SESSION" ]; then
        DESKTOP_ENV="$DESKTOP_SESSION"
    elif [ -n "$GNOME_DESKTOP_SESSION_ID" ]; then
        DESKTOP_ENV="GNOME"
    elif [ -n "$KDE_FULL_SESSION" ]; then
        DESKTOP_ENV="KDE"
    else
        DESKTOP_ENV="unknown"
    fi
    
    log_info "Desktop environment: $DESKTOP_ENV"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install packages based on distro
install_python() {
    log_info "Installing Python and dependencies..."
    
    case $DISTRO in
        ubuntu|debian|pop|mint)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl
            ;;
        fedora)
            sudo dnf install -y python3 python3-pip git curl
            ;;
        centos|rhel|rocky|almalinux)
            sudo yum install -y python3 python3-pip git curl
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm python git curl
            ;;
        opensuse*|sled|sles)
            sudo zypper install -y python3 python3-pip git curl
            ;;
        *)
            log_error "Unsupported distribution: $DISTRO"
            log_info "Please install Python 3, pip, and git manually"
            exit 1
            ;;
    esac
}

# Check Python installation
check_python() {
    log_info "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION found"
        
        # Check if version is 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            log_success "Python version is compatible"
        else
            log_warning "Python version is older than 3.8, but we'll try anyway"
        fi
    else
        log_warning "Python 3 not found, installing..."
        install_python
    fi
}

# Install Dwellpy from source
install_dwellpy() {
    log_info "Installing Dwellpy from source..."
    
    # Install git if not present
    if ! command_exists git; then
        log_info "Installing git..."
        case $DISTRO in
            ubuntu|debian|pop|mint)
                sudo apt install -y git
                ;;
            fedora)
                sudo dnf install -y git
                ;;
            centos|rhel|rocky|almalinux)
                sudo yum install -y git
                ;;
            arch|manjaro)
                sudo pacman -S --noconfirm git
                ;;
            opensuse*|sled|sles)
                sudo zypper install -y git
                ;;
        esac
    fi
    
    # Create install directory
    INSTALL_DIR="$HOME/.local/dwellpy"
    log_info "Installing to: $INSTALL_DIR"
    
    # Remove existing installation
    if [ -d "$INSTALL_DIR" ]; then
        log_info "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    log_info "Downloading Dwellpy source..."
    if git clone https://github.com/code0nwheels/dwellpy.git "$INSTALL_DIR"; then
        log_success "Source code downloaded"
    else
        log_error "Failed to download source code"
        exit 1
    fi
    
    # Create enhanced launcher script
    mkdir -p ~/.local/bin
    cat > ~/.local/bin/dwellpy << 'EOF'
#!/bin/bash
# Enhanced Dwellpy launcher script with GUI environment setup

# Function to log messages with timestamp
log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> ~/.local/dwellpy/dwellpy.log
}

# Wait for GUI environment to be ready
wait_for_gui() {
    local max_attempts=30
    local attempt=0
    
    log_msg "Waiting for GUI environment to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        # Check if DISPLAY is set and X server is accessible
        if [ -n "$DISPLAY" ] && xset q >/dev/null 2>&1; then
            log_msg "GUI environment is ready (DISPLAY=$DISPLAY)"
            return 0
        fi
        
        # Try to detect DISPLAY if not set
        if [ -z "$DISPLAY" ]; then
            # Common display values to try
            for display in ":0" ":1" ":10"; do
                export DISPLAY="$display"
                if xset q >/dev/null 2>&1; then
                    log_msg "Detected DISPLAY=$DISPLAY"
                    return 0
                fi
            done
        fi
        
        log_msg "Attempt $((attempt + 1))/$max_attempts - GUI not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_msg "ERROR: GUI environment not available after $max_attempts attempts"
    return 1
}

# Set up environment variables for GUI applications
setup_gui_environment() {
    log_msg "Setting up GUI environment..."
    
    # Set DISPLAY if not already set
    if [ -z "$DISPLAY" ]; then
        export DISPLAY=":0"
        log_msg "Set DISPLAY=$DISPLAY"
    fi
    
    # Set XDG_RUNTIME_DIR if not set
    if [ -z "$XDG_RUNTIME_DIR" ]; then
        export XDG_RUNTIME_DIR="/run/user/$(id -u)"
        log_msg "Set XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"
    fi
    
    # Set XAUTHORITY if it exists and is not set
    if [ -z "$XAUTHORITY" ] && [ -f "$HOME/.Xauthority" ]; then
        export XAUTHORITY="$HOME/.Xauthority"
        log_msg "Set XAUTHORITY=$XAUTHORITY"
    fi
    
    # Additional environment variables that might be needed
    export QT_X11_NO_MITSHM=1  # Help with some Qt applications
    export GDK_BACKEND=x11      # Force GTK to use X11
    
    log_msg "GUI environment setup complete"
}

# Main launcher function
main() {
    log_msg "=== Starting Dwellpy launcher ==="
    
    # Change to the dwellpy directory
    DWELLPY_DIR="$HOME/.local/dwellpy"
    if ! cd "$DWELLPY_DIR"; then
        log_msg "ERROR: Failed to change to $DWELLPY_DIR"
        exit 1
    fi
    
    # Set up GUI environment
    setup_gui_environment
    
    # Wait for GUI to be ready (important for auto-start scenarios)
    if ! wait_for_gui; then
        log_msg "ERROR: Cannot start Dwellpy - GUI environment not available"
        exit 1
    fi
    
    # Log system information for debugging
    log_msg "System info: $(uname -a)"
    log_msg "Desktop session: ${XDG_SESSION_TYPE:-unknown}"
    log_msg "Desktop environment: ${XDG_CURRENT_DESKTOP:-unknown}"
    log_msg "DISPLAY=$DISPLAY"
    log_msg "XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"
    
    # Run dwellpy with error logging
    log_msg "Starting Dwellpy application..."
    python3 -m dwellpy.main "$@" 2>&1 | while IFS= read -r line; do
        log_msg "APP: $line"
    done
    
    # Log exit status
    exit_code=${PIPESTATUS[0]}
    log_msg "Dwellpy exited with code: $exit_code"
    
    return $exit_code
}

# Run main function
main "$@"
EOF
    
    chmod +x ~/.local/bin/dwellpy
    log_success "Enhanced Dwellpy launcher created"
    
    # Add ~/.local/bin to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        log_info "Adding ~/.local/bin to PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.local/bin:$PATH"
        log_info "You may need to restart your terminal or run: source ~/.bashrc"
    fi
}

# Create XDG autostart desktop entry
create_xdg_autostart() {
    log_info "Creating XDG autostart entry..."
    
    # Create autostart directory
    mkdir -p ~/.config/autostart
    
    # Create desktop entry for autostart
    cat > ~/.config/autostart/dwellpy.desktop << EOF
[Desktop Entry]
Type=Application
Name=Dwellpy
Comment=Accessibility dwell clicker for motor disabilities
Exec=$HOME/.local/bin/dwellpy
Icon=accessibility
Terminal=false
NoDisplay=false
Hidden=false
X-GNOME-Autostart-enabled=true
AutostartCondition=GNOME3 unless-session gnome
StartupNotify=false
Categories=Accessibility;Utility;
Keywords=accessibility;dwell;click;motor;disability;
EOF
    
    log_success "Auto-start configured successfully"
}

# Prompt user for auto-start preference
prompt_autostart() {
    echo
    log_info "═══ AUTO-START CONFIGURATION ═══"
    echo
    log_info "Dwellpy can automatically start when you log in to your desktop."
    log_info "This is recommended for accessibility tools so they're always available."
    echo
    read -p "Would you like Dwellpy to start automatically when you log in? (Y/n): " -n 1 -r
    echo
    
    # Default to yes if user just presses enter or types 'y'
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "Auto-start disabled - you can enable it later if needed"
        return 1
    else
        log_info "Auto-start enabled - Dwellpy will start automatically on login"
        return 0
    fi
}

# Create desktop entry for application menu
create_desktop_entry() {
    log_info "Creating desktop entry for application menu..."
    
    # Create applications directory
    mkdir -p ~/.local/share/applications
    
    # Create desktop entry
    cat > ~/.local/share/applications/dwellpy.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Dwellpy
GenericName=Accessibility Dwell Clicker
Comment=Accessibility dwell clicker for motor disabilities
Exec=$HOME/.local/bin/dwellpy
Icon=accessibility
Terminal=false
Categories=Accessibility;Utility;
Keywords=accessibility;dwell;click;motor;disability;assistive;
StartupNotify=true
StartupWMClass=Dwellpy
MimeType=
Actions=

[Desktop Action Quit]
Name=Quit Dwellpy
Exec=pkill -f "python3 -m dwellpy.main"
EOF
    
    # Update desktop database
    if command_exists update-desktop-database; then
        update-desktop-database ~/.local/share/applications
    fi
    
    log_success "Desktop entry created - Dwellpy now appears in your application menu"
}

# Check X11 vs Wayland
check_display_server() {
    log_info "Checking display server..."
    
    if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
        log_warning "You are using Wayland"
        log_warning "Dwellpy currently requires X11 (Xorg)"
        log_info "To switch to X11:"
        log_info "1. Log out"
        log_info "2. At login screen, click the gear icon"
        log_info "3. Select 'Ubuntu on Xorg' or similar X11 session"
        log_info "4. Log back in"
        echo
        read -p "Continue installation anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled"
            exit 0
        fi
    else
        log_success "X11 detected - compatible with Dwellpy"
    fi
}

# Test Dwellpy installation
test_dwellpy() {
    log_info "Testing Dwellpy installation..."
    
    # Test the launcher script
    if [ -x ~/.local/bin/dwellpy ]; then
        log_success "Dwellpy launcher is executable"
    else
        log_error "Dwellpy launcher is not executable"
        return 1
    fi
    
    # Try to import dwellpy from the installed location
    if cd "$HOME/.local/dwellpy" && python3 -c "import dwellpy" 2>/dev/null; then
        log_success "Dwellpy Python module loads correctly"
    else
        log_error "Failed to import Dwellpy module"
        return 1
    fi
    
    log_info "Installation test completed"
}

# Provide troubleshooting information
show_troubleshooting_info() {
    echo
    log_info "=== TROUBLESHOOTING ==="
    echo
    log_info "If Dwellpy doesn't start automatically (when auto-start is enabled):"
    echo
    log_info "1. Check if autostart entry exists:"
    log_info "   ls -la ~/.config/autostart/dwellpy.desktop"
    echo
    log_info "2. Verify the desktop entry is enabled:"
    log_info "   cat ~/.config/autostart/dwellpy.desktop | grep -E '(Hidden|X-GNOME-Autostart-enabled)'"
    echo
    log_info "3. Test manual launch:"
    log_info "   dwellpy"
    echo
    log_info "4. Check application logs:"
    log_info "   tail -f ~/.local/dwellpy/dwellpy.log"
    echo
    log_info "5. Desktop environment startup applications:"
    log_info "   GNOME: Search for 'Startup Applications' or run: gnome-session-properties"
    log_info "   KDE: System Settings → Startup and Shutdown → Autostart"
    log_info "   XFCE: Settings → Session and Startup → Application Autostart"
    log_info "   MATE: System → Preferences → Startup Applications"
    echo
    log_info "6. Enable auto-start manually:"
    log_info "   Copy: ~/.local/share/applications/dwellpy.desktop"
    log_info "   To: ~/.config/autostart/dwellpy.desktop"
    echo
    log_info "7. Disable auto-start:"
    log_info "   rm ~/.config/autostart/dwellpy.desktop"
    echo
}

# Main installation function
main() {
    echo "========================================="
    echo "    Enhanced Dwellpy Linux Installer"
    echo "========================================="
    echo
    log_info "This script will install Dwellpy with optional auto-start functionality"
    echo
    
    # Run checks and installation
    check_root
    detect_distro
    detect_desktop_environment
    check_display_server
    check_python
    install_dwellpy
    test_dwellpy
    create_desktop_entry          # Always create menu entry
    
    # Prompt for auto-start and create if desired
    if prompt_autostart; then
        create_xdg_autostart
        AUTO_START_ENABLED=true
    else
        AUTO_START_ENABLED=false
    fi
    
    echo
    echo "========================================="
    log_success "Installation completed successfully!"
    echo "========================================="
    echo
    log_info "✅ Dwellpy installed to: $HOME/.local/dwellpy"
    log_info "✅ Launcher created: $HOME/.local/bin/dwellpy"
    log_info "✅ Desktop menu entry created"
    
    if [ "$AUTO_START_ENABLED" = true ]; then
        log_info "✅ Auto-start enabled - will launch automatically on login"
    else
        log_info "ℹ️  Auto-start disabled - run 'dwellpy' manually when needed"
    fi
    
    echo
    log_info "🚀 To start Dwellpy now:"
    log_info "   dwellpy"
    echo
    
    if [ "$AUTO_START_ENABLED" = true ]; then
        log_info "🔄 Dwellpy will automatically start when you log in"
        log_info "   (May require logout/login to take effect)"
    else
        log_info "🔄 To enable auto-start later:"
        log_info "   Create file: ~/.config/autostart/dwellpy.desktop"
        log_info "   Or search for 'Startup Applications' in your desktop settings"
    fi
    
    echo
    log_info "📋 Application logs: ~/.local/dwellpy/dwellpy.log"
    echo
    
    # Show troubleshooting information
    show_troubleshooting_info
    
    log_info "🔗 Need help? Visit: https://github.com/code0nwheels/dwellpy"
    echo
}

# Run main function
main "$@"