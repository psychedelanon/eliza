#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -Eeuo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to check Node.js version
check_node_version() {
    local required_version=20
    local node_version
    node_version=$(node -v | cut -d'v' -f2)
    local major_version=${node_version%%.*}
    
    if [ "$major_version" -lt "$required_version" ]; then
        print_message "$RED" "Error: Node.js version $required_version or later is required. Current version: $node_version"
        exit 1
    fi
}

# Function to check Docker status
check_docker() {
    if ! command_exists docker; then
        print_message "$YELLOW" "Warning: Docker is not installed. Some features may be limited."
        print_message "$YELLOW" "You can continue with local development, but some features will require Docker."
        print_message "$BLUE" "To install Docker later, visit: https://docs.docker.com/get-docker/"
        return 1
    fi

    if ! docker info &> /dev/null; then
        print_message "$YELLOW" "Warning: Docker is not running. Some features may be limited."
        print_message "$YELLOW" "You can continue with local development, but some features will require Docker."
        return 1
    fi

    return 0
}

# Function to install Bun
install_bun() {
    if ! command_exists bun; then
        print_message "$YELLOW" "Installing Bun..."
        curl -fsSL https://bun.sh/install | bash
        # Add Bun to PATH for current session
        export BUN_INSTALL="$HOME/.bun"
        export PATH="$BUN_INSTALL/bin:$PATH"
    fi
}

# Function to initialize git submodules
init_submodules() {
    print_message "$YELLOW" "Initializing git submodules..."
    git submodule update --init --recursive
}

# Function to create necessary configuration files
create_config_files() {
    # Create .env if it doesn't exist
    if [ ! -f .env ]; then
        print_message "$YELLOW" "Creating .env file..."
        cp .env.example .env 2>/dev/null || touch .env
    fi

    # Create pnpm-workspace.yaml if it doesn't exist
    if [ ! -f pnpm-workspace.yaml ]; then
        print_message "$YELLOW" "Creating pnpm-workspace.yaml..."
        cat > pnpm-workspace.yaml << EOF
packages:
  - 'packages/*'
  - 'plugin-specification/*'
EOF
    fi
}

# Function to clean and install dependencies
install_dependencies() {
    print_message "$YELLOW" "Cleaning previous installations..."
    rm -rf node_modules packages/*/node_modules .turbo dist .eliza .elizadb bun.lock*

    print_message "$YELLOW" "Installing dependencies with Bun..."
    bun install
}

# Function to build the project
build_project() {
    print_message "$YELLOW" "Building project..."
    bun run build
}

# Function to run tests
run_tests() {
    print_message "$YELLOW" "Running tests..."
    bun run test
}

# Function to setup Docker environment (if available)
setup_docker() {
    if check_docker; then
        print_message "$YELLOW" "Setting up Docker environment..."
        # Build Docker images if needed
        if [ -f "docker-compose.yaml" ]; then
            print_message "$YELLOW" "Building Docker images..."
            docker-compose build
        fi
    fi
}

# Main setup process
print_message "$GREEN" "🚀 Starting ElizaOS development environment setup..."

# Check for Node.js
if ! command_exists node; then
    print_message "$RED" "Error: Node.js is not installed. Please install Node.js 20 or later."
    exit 1
fi

# Check Node.js version
check_node_version

# Install Bun
install_bun

# Initialize git submodules
init_submodules

# Create configuration files
create_config_files

# Install dependencies
install_dependencies

# Build the project
build_project

# Run tests
run_tests

# Setup Docker environment (if available)
setup_docker

print_message "$GREEN" "✅ ElizaOS development environment setup completed successfully!"
print_message "$GREEN" "To start the application, run: bun start"
print_message "$YELLOW" "Note: Make sure to configure your .env file with the necessary API keys and settings."

# Show Docker status
if ! check_docker; then
    print_message "$BLUE" "Some features may require Docker. You can install it later and run 'docker-compose up' to enable those features." 