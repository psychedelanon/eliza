#!/bin/bash

# Bitcoin Aqua Engagement System Launcher
# This script sets up and launches the Bitcoin Aqua mindshare campaign

set -e

echo "🌊 Bitcoin Aqua Engagement System Launcher"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_success "Node.js $(node --version) is installed"
}

# Check if npm is installed
check_npm() {
    print_status "Checking npm installation..."
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    print_success "npm $(npm --version) is installed"
}

# Check if Redis is running
check_redis() {
    print_status "Checking Redis connection..."
    if ! command -v redis-cli &> /dev/null; then
        print_warning "redis-cli not found. Please ensure Redis is installed and running."
        print_warning "You can install Redis with: sudo apt-get install redis-server"
        print_warning "Or start Redis with: redis-server"
    else
        if redis-cli ping &> /dev/null; then
            print_success "Redis is running"
        else
            print_warning "Redis is not responding. Please start Redis server."
            print_warning "Start Redis with: redis-server"
        fi
    fi
}

# Check environment configuration
check_env() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your Twitter API credentials before continuing."
            print_warning "Required: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET"
            exit 1
        else
            print_error ".env.example not found. Please create .env file manually."
            exit 1
        fi
    fi
    
    # Check for required environment variables
    source .env
    
    if [ -z "$TWITTER_API_KEY" ] || [ "$TWITTER_API_KEY" = "your_twitter_api_key_here" ]; then
        print_error "TWITTER_API_KEY not configured in .env file"
        exit 1
    fi
    
    if [ -z "$TWITTER_API_SECRET" ] || [ "$TWITTER_API_SECRET" = "your_twitter_api_secret_here" ]; then
        print_error "TWITTER_API_SECRET not configured in .env file"
        exit 1
    fi
    
    if [ -z "$TWITTER_ACCESS_TOKEN" ] || [ "$TWITTER_ACCESS_TOKEN" = "your_twitter_access_token_here" ]; then
        print_error "TWITTER_ACCESS_TOKEN not configured in .env file"
        exit 1
    fi
    
    if [ -z "$TWITTER_ACCESS_TOKEN_SECRET" ] || [ "$TWITTER_ACCESS_TOKEN_SECRET" = "your_twitter_access_token_secret_here" ]; then
        print_error "TWITTER_ACCESS_TOKEN_SECRET not configured in .env file"
        exit 1
    fi
    
    print_success "Environment configuration is valid"
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm packages..."
        npm install
        print_success "Dependencies installed"
    else
        print_status "Dependencies already installed"
    fi
}

# Build the project
build_project() {
    print_status "Building project..."
    
    if [ ! -d "dist" ]; then
        print_status "Building TypeScript..."
        npm run build
        print_success "Project built successfully"
    else
        print_status "Project already built"
    fi
}

# Start the system
start_system() {
    print_status "Starting Bitcoin Aqua Engagement System..."
    echo ""
    echo "🚀 Launching Bitcoin Aqua Mindshare Campaign Network..."
    echo "📊 4 specialized agents will coordinate to increase @bitcoinaqua mindshare"
    echo "🌊 Network coordination enabled via Redis"
    echo "⚡ Engagement optimization and trend integration active"
    echo ""
    echo "Press Ctrl+C to stop the system"
    echo ""
    
    # Start the system
    npm start
}

# Main execution
main() {
    echo "🔧 Pre-flight checks..."
    check_node
    check_npm
    check_redis
    check_env
    
    echo ""
    echo "📦 Setup..."
    install_deps
    build_project
    
    echo ""
    echo "🎯 Ready to launch Bitcoin Aqua engagement system!"
    echo ""
    
    # Ask for confirmation
    read -p "Do you want to start the Bitcoin Aqua engagement system? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_system
    else
        print_warning "Launch cancelled. Run this script again when ready."
        exit 0
    fi
}

# Handle script interruption
trap 'echo ""; print_warning "Received interrupt signal. Shutting down gracefully..."; exit 0' INT

# Run main function
main "$@"