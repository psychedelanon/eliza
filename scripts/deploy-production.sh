#!/bin/bash

# ElizaOS Swarm Production Deployment Script
# Based on go-live playbook stages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        error ".env file not found. Please copy env.template to .env and configure it."
        exit 1
    fi
    
    # Check if production config exists
    if [ ! -f "$PROJECT_DIR/config/production/engagement.yaml" ]; then
        error "Production engagement config not found."
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Build and tag image
build_image() {
    log "Building production image..."
    
    cd "$PROJECT_DIR"
    
    # Build the image
    docker build -t ghcr.io/psychedelanon/eliza:0.4.0-alpha2 .
    
    # Tag as latest
    docker tag ghcr.io/psychedelanon/eliza:0.4.0-alpha2 ghcr.io/psychedelanon/eliza:latest
    
    success "Image built successfully"
}

# Run dry-run validation
validate_dry_run() {
    log "Running dry-run validation..."
    
    cd "$PROJECT_DIR"
    
    # Run a 5-minute dry run
    timeout 300s docker-compose -f docker-compose-production.yaml run --rm swarm \
        python -m eliza.cli.run_swarm --dry --duration 300 --verbose || {
        if [ $? -eq 124 ]; then
            success "Dry-run completed successfully (timed out as expected)"
        else
            error "Dry-run failed"
            exit 1
        fi
    }
}

# Deploy with specific stage
deploy_stage() {
    local stage=$1
    
    log "Deploying Stage $stage..."
    
    case $stage in
        "A")
            log "Stage A: Beta - Price bot only"
            # Ensure only agent2 is live
            ;;
        "B")
            log "Stage B: Price bot + one meme agent"
            # Enable agent2 and agent3
            ;;
        "C")
            log "Stage C: Progressive activation (50% live)"
            # Enable agent1, agent2, agent3, agent4
            ;;
        "D")
            log "Stage D: Full swarm activation"
            # Enable all agents
            ;;
        *)
            error "Unknown stage: $stage"
            exit 1
            ;;
    esac
    
    # Deploy using docker-compose
    docker-compose -f docker-compose-production.yaml up -d
    
    success "Stage $stage deployed successfully"
}

# Monitor deployment
monitor_deployment() {
    log "Monitoring deployment for 10 minutes..."
    
    # Monitor logs for errors
    timeout 600s docker-compose -f docker-compose-production.yaml logs -f swarm &
    LOGS_PID=$!
    
    # Monitor health
    for i in {1..10}; do
        sleep 60
        
        # Check if swarm service is healthy
        if ! docker-compose -f docker-compose-production.yaml ps swarm | grep -q "Up"; then
            error "Swarm service is not running"
            kill $LOGS_PID 2>/dev/null || true
            exit 1
        fi
        
        log "Health check $i/10 passed"
    done
    
    kill $LOGS_PID 2>/dev/null || true
    success "Monitoring completed - deployment looks healthy"
}

# Rollback function
rollback() {
    warning "Rolling back deployment..."
    
    docker-compose -f docker-compose-production.yaml down
    
    warning "Deployment rolled back"
}

# Main deployment function
main() {
    local stage=${1:-"A"}
    local skip_build=${2:-false}
    
    log "Starting ElizaOS Swarm production deployment - Stage $stage"
    
    # Trap to handle rollback on failure
    trap rollback ERR
    
    check_prerequisites
    
    if [ "$skip_build" != "true" ]; then
        build_image
    fi
    
    validate_dry_run
    deploy_stage "$stage"
    monitor_deployment
    
    success "🚀 Stage $stage deployment completed successfully!"
    
    case $stage in
        "A")
            log "Next steps: Monitor for 24h, then deploy Stage B with: $0 B"
            ;;
        "B") 
            log "Next steps: Monitor for 48h, then deploy Stage C with: $0 C"
            ;;
        "C")
            log "Next steps: Monitor for 72h, then deploy Stage D with: $0 D"
            ;;
        "D")
            log "🎉 Full swarm deployment complete! Welcome to Crypto Twitter!"
            ;;
    esac
}

# Handle script arguments
case ${1:-""} in
    "A"|"B"|"C"|"D")
        main "$1" "$2"
        ;;
    "rollback")
        rollback
        ;;
    "monitor")
        monitor_deployment
        ;;
    *)
        echo "Usage: $0 {A|B|C|D|rollback|monitor} [skip-build]"
        echo ""
        echo "Stages:"
        echo "  A - Beta: Price bot only"
        echo "  B - Price bot + one meme agent" 
        echo "  C - Progressive activation (50% live)"
        echo "  D - Full swarm activation"
        echo ""
        echo "Commands:"
        echo "  rollback - Stop and rollback deployment"
        echo "  monitor  - Monitor current deployment"
        echo ""
        echo "Options:"
        echo "  skip-build - Skip image building step"
        exit 1
        ;;
esac 