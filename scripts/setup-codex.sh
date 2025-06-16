#!/bin/bash

# Codex environment setup script for the eliza project
# Specifically designed for OpenAI Codex environment (Ubuntu 24.04)

# Enable verbose output and error handling
set -x  # Print each command before execution
set -e  # Exit on any error
set -o pipefail  # Exit on pipe failures

# Define some colors for pretty output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m'  # No color / reset

# Function to print colored messages
print_step() {
    echo -e "${PURPLE}🤖 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}✖ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to log errors
log_error() {
    print_error "$1"
    echo "Error details: $2" >&2
}

print_step "Starting Codex setup in $(pwd)..."

# Install system dependencies
print_info "Installing system dependencies..."
apt-get update
apt-get install -y curl git build-essential

# Install Node.js using nvm
print_info "Installing Node.js 23.3.0 using nvm..."
# Ensure nvm is loaded
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install and use Node.js 23.3.0
nvm install 23.3.0
nvm use 23.3.0
nvm alias default 23.3.0

# Verify Node.js installation and version
NODE_VERSION=$(node --version)
if [[ "$NODE_VERSION" != v23.3.0 ]]; then
    print_error "Node.js 23.3.0 installation failed. Current version: $NODE_VERSION"
    exit 1
fi
print_success "Node.js $NODE_VERSION installed"

# Install Bun
print_info "Installing Bun..."
curl -fsSL https://bun.sh/install | bash
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# Verify Bun installation
if command_exists bun; then
    BUN_VERSION=$(bun --version)
    print_success "Bun $BUN_VERSION installed"
else
    print_error "Failed to install Bun"
    exit 1
fi

# Initialize git submodules if .gitmodules exists
if [ -f .gitmodules ]; then
    print_info "Initializing git submodules..."
    git submodule update --init --recursive
fi

# Setup configuration files
print_info "Setting up configuration files..."
cp .env.example .env

# Clean up any existing node_modules and lockfiles
print_info "Cleaning up existing dependencies..."
rm -rf node_modules
rm -f package-lock.json
rm -f bun.lockb
rm -f yarn.lock

# Update package.json to use Node.js 23.3.0
print_info "Updating package.json for Node.js 23.3.0..."
if [ -f package.json ]; then
    # Use sed to update the engines field
    sed -i 's/"node": ".*"/"node": "23.3.0"/' package.json
fi

# Install dependencies
print_info "Installing project dependencies with Bun..."
bun install

# Install missing dependencies
print_info "Installing additional required dependencies..."
bun add -d @elizaos/plugin-twitter

print_success "Dependencies installed successfully"

# Build the project
print_info "Building the project..."
bun run build

print_success "Setup completed successfully!" 