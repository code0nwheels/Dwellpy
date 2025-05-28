#!/bin/bash
# Dwellpy Linux Install Script
# Downloads source code and installs Dwellpy locally
# Usage: curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/install.sh | bash

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install packages based on distro
install_python() {
    log_info "Installing Python..."
    
    case $DISTRO in
        ubuntu|debian|pop|mint)
            sudo apt update
            sudo apt install -y python3 git
            ;;
        fedora)
            sudo dnf install -y python3 git
            ;;
        centos|rhel|rocky|almalinux)
            sudo yum install -y python3 git
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm python git
            ;;
        opensuse*|sled|sles)
            sudo zypper install -y python3 git
            ;;
        *)
            log_error "Unsupported distribution: $DISTRO"
            log_info "Please install Python 3 and git manually"
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
    
    # Create launcher script
    mkdir -p ~/.local/bin
    cat > ~/.local/bin/dwellpy << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 -m dwellpy.main "\$@"
EOF
    
    chmod +x ~/.local/bin/dwellpy
    log_success "Dwellpy launcher created"
    
    # Test installation
    if cd "$INSTALL_DIR" && python3 -c "import dwellpy" 2>/dev/null; then
        log_success "Dwellpy installed successfully"
    else
        log_error "Failed to install Dwellpy"
        log_info "You can try running manually from: $INSTALL_DIR"
        exit 1
    fi
    
    # Add ~/.local/bin to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        log_info "Adding ~/.local/bin to PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.local/bin:$PATH"
        log_info "You may need to restart your terminal or run: source ~/.bashrc"
    fi
}

# Create systemd user service
create_systemd_service() {
    log_info "Creating systemd user service..."
    
    # Create systemd user directory
    mkdir -p ~/.config/systemd/user
    
    # Create service file
    cat > ~/.config/systemd/user/dwellpy.service << EOF
[Unit]
Description=Dwellpy accessibility tool
After=graphical-session.target

[Service]
Type=simple
ExecStart=$HOME/.local/bin/dwellpy
Restart=on-failure
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF
    
    log_success "Systemd service file created"
    
    # Reload systemd and enable service
    log_info "Enabling Dwellpy service..."
    systemctl --user daemon-reload
    systemctl --user enable dwellpy.service
    
    log_success "Dwellpy service enabled for auto-start"
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
        log_info "3. Select 'Ubuntu on Xorg' or similar"
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

# Test Dwellpy
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

# Main installation function
main() {
    echo "========================================="
    echo "       Dwellpy Linux Installer"
    echo "========================================="
    echo
    log_info "This script will download and install Dwellpy from source"
    echo
    
    # Run checks and installation
    check_root
    detect_distro
    check_display_server
    check_python
    install_dwellpy
    test_dwellpy
    create_systemd_service
    
    echo
    echo "========================================="
    log_success "Installation completed!"
    echo "========================================="
    echo
    log_info "To start Dwellpy now: dwellpy"
    log_info "To start the service: systemctl --user start dwellpy.service"
    log_info "To check service status: systemctl --user status dwellpy.service"
    echo
    log_info "Dwellpy will automatically start when you log in"
    echo
    log_info "Need help? Check: https://github.com/code0nwheels/dwellpy/wiki"
    echo
}

# Run main function
main "$@"