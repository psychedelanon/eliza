#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1"
}

# Check if bun is installed
check_bun() {
    if ! command -v bun &> /dev/null; then
        print_error "Bun is not installed. Please install it first:"
        echo "curl -fsSL https://bun.sh/install | bash"
        exit 1
    fi
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    bun install
}

# Initialize git submodules
init_submodules() {
    print_step "Initializing git submodules..."
    git submodule update --init --recursive
}

# Setup environment variables
setup_env() {
    print_step "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env 2>/dev/null || touch .env
        print_warning "Created .env file. Please configure your environment variables."
    fi
}

# Build packages
build_packages() {
    print_step "Building packages..."
    bun run build
}

# Run tests
run_tests() {
    print_step "Running tests..."
    bun run test
}

# Main setup process
main() {
    print_step "Starting Codex environment setup..."
    
    # Check prerequisites
    check_bun
    check_docker
    
    # Run setup steps
    install_dependencies
    init_submodules
    setup_env
    build_packages
    run_tests
    
    print_step "Setup completed successfully!"
    echo -e "\nNext steps:"
    echo "1. Configure your .env file with necessary credentials"
    echo "2. Start the development server with 'bun run dev'"
    echo "3. Access the application at http://localhost:3000"
}

# Run main function
main 