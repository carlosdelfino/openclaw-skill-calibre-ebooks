#!/bin/bash

# Calibre OpenClaw Server - Systemd Service Installer
# This script installs and manages the Calibre OpenClaw Server as a systemd service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="calibre-openclaw-server"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "ℹ $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. It will use sudo when needed."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    ENV_FILE=""
    CALL_DIR="$(pwd)"
    PARENT_DIR="$(dirname "$SCRIPT_DIR")"

    # Check in order: script dir, call dir, parent dir
    for dir in "$SCRIPT_DIR" "$CALL_DIR" "$PARENT_DIR"; do
        if [[ -f "$dir/.env" ]]; then
            ENV_FILE="$dir/.env"
            print_success ".env file found at $ENV_FILE"
            break
        fi
    done

    if [[ -z "$ENV_FILE" ]]; then
        print_error ".env file not found!"
        print_info "Searched in:"
        print_info "  - $SCRIPT_DIR/.env"
        print_info "  - $CALL_DIR/.env"
        print_info "  - $PARENT_DIR/.env"
        print_info ""
        print_info "Please create a .env file in one of these locations or specify the path:"
        print_info "  cp .env.example /path/to/.env"
        print_info "  Then edit it with your configuration."
        exit 1
    fi
}

# Check and create virtual environment
check_venv() {
    VENV_DIR="$SCRIPT_DIR/.venv"
    VENV_PYTHON="$VENV_DIR/bin/python"
    VENV_PIP="$VENV_DIR/bin/pip"

    if [[ ! -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv "$VENV_DIR"
        if [[ $? -eq 0 ]]; then
            print_success "Virtual environment created at $VENV_DIR"
            # Upgrade pip
            print_info "Upgrading pip in new virtual environment..."
            "$VENV_DIR/bin/python" -m pip install --upgrade pip --no-cache-dir 2>/dev/null
            if [[ $? -ne 0 ]]; then
                print_warning "pip upgrade via index failed, trying get-pip.py..."
                curl -s https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
                "$VENV_DIR/bin/python" /tmp/get-pip.py --no-cache-dir
            fi
            print_success "pip upgraded: $($VENV_DIR/bin/pip --version)"
        else
            print_error "Failed to create virtual environment"
            exit 1
        fi
    else
        print_success "Virtual environment found at $VENV_DIR"
        # Check and upgrade pip if needed
        pip_version=$($VENV_PIP --version | awk '{print $2}')
        pip_major=$(echo $pip_version | cut -d. -f1)
        if [[ "$pip_major" -lt 25 ]]; then
            print_warning "pip version $pip_version is old, upgrading..."
            curl -s https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
            $VENV_PYTHON /tmp/get-pip.py --no-cache-dir
            print_success "pip upgraded: $($VENV_PIP --version)"
        else
            print_success "pip version $pip_version is up to date"
        fi
    fi
}

# Check if requirements.txt exists
check_requirements() {
    if [[ ! -f "${SCRIPT_DIR}/requirements.txt" ]]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    print_success "requirements.txt found"
}

# Check if virtual environment Python is available
check_venv_python() {
    VENV_DIR="$SCRIPT_DIR/.venv"
    VENV_PYTHON="$VENV_DIR/bin/python"

    if [[ ! -f "$VENV_PYTHON" ]]; then
        print_error "Virtual environment Python not found at $VENV_PYTHON"
        exit 1
    fi
    print_success "Virtual environment Python found: $($VENV_PYTHON --version)"
}

# Check if virtual environment pip is available
check_venv_pip() {
    VENV_DIR="$SCRIPT_DIR/.venv"
    VENV_PIP="$VENV_DIR/bin/pip"

    if [[ ! -f "$VENV_PIP" ]]; then
        print_error "Virtual environment pip not found at $VENV_PIP"
        exit 1
    fi
    print_success "Virtual environment pip found"
}

# Check if a package is installed in venv
check_package() {
    local package=$1
    VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
    if $VENV_PYTHON -c "import $package" 2>/dev/null; then
        print_success "$package is installed"
        return 0
    else
        print_error "$package is NOT installed"
        return 1
    fi
}

# Check critical packages
check_packages() {
    print_info "Checking required packages..."
    
    missing_packages=0

    # List of packages to check (import names, not pip names)
    declare -a packages=(
        "fastapi"
        "uvicorn"
        "pydantic"
        "psycopg2"
        "fitz"
        "httpx"
    )

    for package in "${packages[@]}"; do
        if ! check_package "$package"; then
            missing_packages=$((missing_packages + 1))
        fi
    done

    # If packages are missing, install them
    if [[ $missing_packages -gt 0 ]]; then
        print_warning "$missing_packages required package(s) are missing"
        print_info "Installing packages from requirements.txt..."
        VENV_PIP="$SCRIPT_DIR/.venv/bin/pip"
        $VENV_PIP install -r "${SCRIPT_DIR}/requirements.txt"
        if [[ $? -eq 0 ]]; then
            print_success "Packages installed successfully"
        else
            print_error "Failed to install packages"
            exit 1
        fi
    else
        print_success "All required packages are installed"
    fi
}

# Check if Ollama is running
check_ollama() {
    print_info "Checking Ollama..."

    if command -v ollama &> /dev/null; then
        print_success "Ollama is installed"
        
        # Check if Ollama is running
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama is running"
            
            # Check if model is available
            if curl -s http://localhost:11434/api/tags | grep -q "nomic-embed-text-v2-moe"; then
                print_success "nomic-embed-text-v2-moe model is available"
            else
                print_warning "nomic-embed-text-v2-moe model is not downloaded"
                print_info "  You can download it with: ollama pull nomic-embed-text-v2-moe:latest"
            fi
        else
            print_warning "Ollama is not running"
            print_info "  Start it with: ollama serve"
        fi
    else
        print_warning "Ollama is not installed"
        print_info "  Install it from: https://ollama.ai"
    fi
}

# Check if PostgreSQL is accessible
check_postgresql() {
    print_info "Checking PostgreSQL..."

    # Read PostgreSQL credentials from .env
    if [[ -f "${SCRIPT_DIR}/.env" ]]; then
        source "${SCRIPT_DIR}/.env"
    fi

    PGUSER="${POSTGRESQL_DB_USER:-generativa}"
    PGPASSWORD="${POSTGRESQL_DB_PASSWD:-}"
    PGDATABASE="${POSTGRESQL_DB_DATABASE:-rapport_biblioteca}"
    PGHOST="${POSTGRESQL_DB_HOST:-localhost}"
    PGPORT="${POSTGRESQL_DB_PORT:-5432}"

    if PGPASSWORD="$PGPASSWORD" psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT 1" > /dev/null 2>&1; then
        print_success "PostgreSQL is accessible"
    else
        print_warning "PostgreSQL is not accessible"
        print_info "  Make sure PostgreSQL is running and credentials are correct in .env"
    fi
}

# Check if Calibre metadata.db exists
check_calibre_db() {
    print_info "Checking Calibre database..."

    # Read Calibre DB path from .env
    if [[ -f "${SCRIPT_DIR}/.env" ]]; then
        source "${SCRIPT_DIR}/.env"
    fi

    CALIBRE_DB_PATH="${CALIBRE_DB_PATH:-/mnt/Backup_2/Biblioteca/metadata.db}"

    if [[ -f "$CALIBRE_DB_PATH" ]]; then
        print_success "Calibre metadata.db found at $CALIBRE_DB_PATH"
    else
        print_error "Calibre metadata.db not found at $CALIBRE_DB_PATH"
        print_info "  Please check the CALIBRE_DB_PATH in .env"
        exit 1
    fi
}

# Run all checks
run_all_checks() {
    print_info "Running pre-installation checks..."
    echo ""
    
    check_venv
    check_env
    check_requirements
    check_venv_python
    check_venv_pip
    check_packages
    check_ollama
    check_postgresql
    check_calibre_db
    
    echo ""
    print_success "All checks passed!"
}

# Create systemd service file
create_service_file() {
    print_info "Creating systemd service file..."
    
    CURRENT_USER=$(whoami)
    CURRENT_HOME=$(getent passwd "$CURRENT_USER" | cut -d: -f6)
    
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Calibre OpenClaw Server
After=network.target postgresql.service

[Service]
Type=simple
User=${CURRENT_USER}
Group=${CURRENT_USER}
WorkingDirectory=${SCRIPT_DIR}
Environment="PATH=${SCRIPT_DIR}/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${SCRIPT_DIR}/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 6180
ExecStop=/bin/kill -SIGTERM \$MAINPID
Restart=always
RestartSec=10
StandardOutput=append:${SCRIPT_DIR}/logs/service.log
StandardError=append:${SCRIPT_DIR}/logs/service_error.log

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Service file created at $SERVICE_FILE"
}

# Install the service
install_service() {
    print_info "Installing ${SERVICE_NAME} service..."
    
    check_root
    
    # Run all pre-installation checks
    run_all_checks
    
    # Create logs directory if it doesn't exist
    mkdir -p "${SCRIPT_DIR}/logs"
    
    # Create service file
    create_service_file
    
    # Reload systemd
    print_info "Reloading systemd daemon..."
    sudo systemctl daemon-reload
    print_success "Systemd daemon reloaded"
    
    # Enable service to start on boot
    print_info "Enabling service to start on boot..."
    sudo systemctl enable "$SERVICE_NAME"
    print_success "Service enabled"
    
    print_success "Service installed successfully!"
    print_info "You can now manage the service using:"
    print_info "  sudo systemctl start ${SERVICE_NAME}"
    print_info "  sudo systemctl stop ${SERVICE_NAME}"
    print_info "  sudo systemctl restart ${SERVICE_NAME}"
    print_info "  sudo systemctl status ${SERVICE_NAME}"
    print_info "  systemctl --user start ${SERVICE_NAME}"
    print_info "  systemctl --user stop ${SERVICE_NAME}"
    print_info "  systemctl --user restart ${SERVICE_NAME}"
    print_info "  systemctl --user status ${SERVICE_NAME}"
}

# Uninstall the service
uninstall_service() {
    print_info "Uninstalling ${SERVICE_NAME} service..."
    
    # Stop service if running
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null || systemctl --user is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        print_info "Stopping service..."
        sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || systemctl --user stop "$SERVICE_NAME" 2>/dev/null
        print_success "Service stopped"
    fi
    
    # Disable service
    print_info "Disabling service..."
    sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || systemctl --user disable "$SERVICE_NAME" 2>/dev/null
    print_success "Service disabled"
    
    # Remove service file
    if [[ -f "$SERVICE_FILE" ]]; then
        print_info "Removing service file..."
        sudo rm -f "$SERVICE_FILE"
        print_success "Service file removed"
    fi
    
    # Reload systemd
    print_info "Reloading systemd daemon..."
    sudo systemctl daemon-reload
    print_success "Systemd daemon reloaded"
    
    print_success "Service uninstalled successfully!"
}

# Start the service
start_service() {
    print_info "Starting ${SERVICE_NAME} service..."
    
    if [[ -f "$SERVICE_FILE" ]]; then
        sudo systemctl start "$SERVICE_NAME"
    else
        systemctl --user start "$SERVICE_NAME"
    fi
    
    print_success "Service started!"
    print_info "Check status with: $0 status"
}

# Stop the service
stop_service() {
    print_info "Stopping ${SERVICE_NAME} service..."
    
    if [[ -f "$SERVICE_FILE" ]]; then
        sudo systemctl stop "$SERVICE_NAME"
    else
        systemctl --user stop "$SERVICE_NAME"
    fi
    
    print_success "Service stopped!"
}

# Restart the service
restart_service() {
    print_info "Restarting ${SERVICE_NAME} service..."
    
    if [[ -f "$SERVICE_FILE" ]]; then
        sudo systemctl restart "$SERVICE_NAME"
    else
        systemctl --user restart "$SERVICE_NAME"
    fi
    
    print_success "Service restarted!"
    print_info "Check status with: $0 status"
}

# Show service status
show_status() {
    print_info "${SERVICE_NAME} service status:"
    echo ""
    
    if [[ -f "$SERVICE_FILE" ]]; then
        sudo systemctl status "$SERVICE_NAME"
    else
        systemctl --user status "$SERVICE_NAME"
    fi
}

# Enable service to start on boot
enable_service() {
    print_info "Enabling ${SERVICE_NAME} service to start on boot..."
    
    if [[ -f "$SERVICE_FILE" ]]; then
        sudo systemctl enable "$SERVICE_NAME"
    else
        systemctl --user enable "$SERVICE_NAME"
    fi
    
    print_success "Service enabled!"
}

# Disable service from starting on boot
disable_service() {
    print_info "Disabling ${SERVICE_NAME} service from starting on boot..."
    
    if [[ -f "$SERVICE_FILE" ]]; then
        sudo systemctl disable "$SERVICE_NAME"
    else
        systemctl --user disable "$SERVICE_NAME"
    fi
    
    print_success "Service disabled!"
}

# Show usage
show_usage() {
    cat <<EOF
Calibre OpenClaw Server - Service Management Script

Usage: $0 <command>

Commands:
  install     Install the service as a systemd service (requires sudo)
  uninstall   Remove the systemd service (requires sudo)
  start       Start the service
  stop        Stop the service
  restart     Restart the service
  status      Show service status
  enable      Enable service to start on boot
  disable     Disable service from starting on boot
  help        Show this help message

Examples:
  $0 install     # Install the service
  $0 start       # Start the service
  $0 status      # Check service status
  $0 stop        # Stop the service
  $0 uninstall   # Remove the service

After installation, you can also use systemctl directly:
  sudo systemctl start ${SERVICE_NAME}
  sudo systemctl stop ${SERVICE_NAME}
  sudo systemctl restart ${SERVICE_NAME}
  sudo systemctl status ${SERVICE_NAME}
  
Or with user systemd (if installed as user service):
  systemctl --user start ${SERVICE_NAME}
  systemctl --user stop ${SERVICE_NAME}
  systemctl --user restart ${SERVICE_NAME}
  systemctl --user status ${SERVICE_NAME}
EOF
}

# Main script logic
case "${1:-}" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_usage
        exit 1
        ;;
esac
