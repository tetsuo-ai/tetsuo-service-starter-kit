#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3.11; then
        version=$(python3.11 -V 2>&1 | awk '{print $2}')
        print_success "Python $version is installed"
        return 0
    else
        print_error "Python 3.11 is required but not installed"
        return 1
    fi
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

echo -e "\n${GREEN}=== Tetsuo Service Starter Kit Setup ===${NC}\n"

# Update package list
print_status "Updating package list..."
apt-get update || {
    print_error "Failed to update package list"
    exit 1
}

# Install required packages
print_status "Installing required packages..."
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    redis-server \
    build-essential \
    curl \
    git \
    || {
        print_error "Failed to install required packages"
        exit 1
    }
print_success "Required packages installed"

# Setup Redis
print_status "Configuring Redis..."
systemctl enable redis-server
systemctl start redis-server
if systemctl is-active --quiet redis-server; then
    print_success "Redis is running"
else
    print_error "Failed to start Redis"
    exit 1
fi

# Verify Python installation
print_status "Checking Python installation..."
check_python_version || {
    print_error "Python 3.11 installation check failed"
    exit 1
}

# Create project directory if it doesn't exist
PROJECT_DIR="/opt/tetsuo-service-starter-kit"
print_status "Setting up project directory at ${PROJECT_DIR}..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR" || {
    print_error "Failed to create/access project directory"
    exit 1
}

# Set proper ownership
print_status "Setting proper ownership..."
chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR"

# Switch to the user context for Python operations
su - "$SUDO_USER" << 'EOF'
cd /opt/tetsuo-service-starter-kit

# Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

EOF

# Create environment file if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_status "Creating default .env file..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    print_success "Created .env file (please update with your settings)"
fi

# Create service user
print_status "Creating service user..."
useradd -r -s /bin/false tetsuo-service || {
    if [ $? -eq 9 ]; then
        print_status "Service user already exists"
    else
        print_error "Failed to create service user"
        exit 1
    fi
}

# Create systemd service
print_status "Creating systemd service..."
cat > /etc/systemd/system/tetsuo-service-starter-kit.service << 'EOL'
[Unit]
Description=Tetsuo Core Services
After=network.target redis-server.service

[Service]
Type=simple
User=tetsuo-service
Group=tetsuo-service
WorkingDirectory=/opt/tetsuo-service-starter-kit
Environment=PATH=/opt/tetsuo-service-starter-kit/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
ExecStart=/opt/tetsuo-service-starter-kit/.venv/bin/python -m app.main
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Set proper permissions
chown -R tetsuo-service:tetsuo-service "$PROJECT_DIR"
chmod -R 750 "$PROJECT_DIR"

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable tetsuo-service-starter-kit.service

print_status "Running final checks..."

# Test Redis connection
print_status "Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    print_success "Redis connection successful"
else
    print_error "Redis connection failed"
    exit 1
fi

# Create convenience scripts
print_status "Creating convenience scripts..."

# Start script
cat > "$PROJECT_DIR/start.sh" << 'EOL'
#!/bin/bash
sudo systemctl start tetsuo-service-starter-kit
EOL

# Stop script
cat > "$PROJECT_DIR/stop.sh" << 'EOL'
#!/bin/bash
sudo systemctl stop tetsuo-service-starter-kit
EOL

# Status script
cat > "$PROJECT_DIR/status.sh" << 'EOL'
#!/bin/bash
sudo systemctl status tetsuo-service-starter-kit
EOL

# Make scripts executable
chmod +x "$PROJECT_DIR"/*.sh
chown "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR"/*.sh

echo -e "\n${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "You can now:"
echo -e "1. Edit ${YELLOW}/opt/tetsuo-service-starter-kit/.env${NC} with your settings"
echo -e "2. Start the service: ${YELLOW}sudo systemctl start tetsuo-service-starter-kit${NC}"
echo -e "3. Check status: ${YELLOW}sudo systemctl status tetsuo-service-starter-kit${NC}"
echo -e "\nOr use the convenience scripts:"
echo -e "- ${YELLOW}./start.sh${NC} to start the service"
echo -e "- ${YELLOW}./stop.sh${NC} to stop the service"
echo -e "- ${YELLOW}./status.sh${NC} to check service status"
echo -e "\nService logs can be viewed with: ${YELLOW}sudo journalctl -u tetsuo-service-starter-kit -f${NC}"
