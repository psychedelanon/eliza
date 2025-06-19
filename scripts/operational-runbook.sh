#!/bin/bash

# ElizaOS Swarm Operational Runbook
# Commands for managing production deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

# Manual dry-run
dry_run() {
    local duration=${1:-300}
    log "Running manual dry-run for ${duration} seconds..."
    
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose-production.yaml run --rm swarm \
        python -m eliza.cli.run_swarm --dry --duration $duration --verbose
    
    success "Dry-run completed"
}

# Hot-reload personas
reload_personas() {
    log "Hot-reloading personas..."
    
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose-production.yaml restart swarm
    
    success "Personas reloaded - swarm service restarted"
}

# Force-stop swarm
force_stop() {
    log "Force-stopping swarm..."
    
    cd "$PROJECT_DIR" 
    docker-compose -f docker-compose-production.yaml stop swarm
    
    warning "Swarm service stopped"
}

# Inspect Redis memory
inspect_redis() {
    log "Inspecting Redis memory usage..."
    
    cd "$PROJECT_DIR"
    
    echo "=== Redis Memory Stats ==="
    docker-compose -f docker-compose-production.yaml exec redis redis-cli info memory
    
    echo -e "\n=== Redis Keys ==="
    docker-compose -f docker-compose-production.yaml exec redis redis-cli --scan | head -20
    
    echo -e "\n=== Redis Connected Clients ==="
    docker-compose -f docker-compose-production.yaml exec redis redis-cli info clients
}

# Inspect logs with filtering
inspect_logs() {
    local service=${1:-swarm}
    local lines=${2:-100}
    local filter=${3:-""}
    
    log "Inspecting logs for service: $service (last $lines lines)"
    
    cd "$PROJECT_DIR"
    
    if [ -n "$filter" ]; then
        docker-compose -f docker-compose-production.yaml logs --tail=$lines $service | grep "$filter"
    else
        docker-compose -f docker-compose-production.yaml logs --tail=$lines $service
    fi
}

# Get service status
get_status() {
    log "Getting service status..."
    
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose-production.yaml ps
    
    echo -e "\n=== Health Checks ==="
    docker-compose -f docker-compose-production.yaml exec swarm python -c "
import requests
try:
    resp = requests.get('http://localhost:8080/health', timeout=5)
    print(f'Health endpoint: {resp.status_code}')
except Exception as e:
    print(f'Health check failed: {e}')
" 2>/dev/null || echo "Health check service not available"
}

# Monitor real-time logs
monitor_logs() {
    local service=${1:-swarm}
    log "Monitoring real-time logs for service: $service (Press Ctrl+C to stop)"
    
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose-production.yaml logs -f $service
}

# Get metrics
get_metrics() {
    log "Getting application metrics..."
    
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose-production.yaml exec swarm python -c "
import json
from agents.EventSystem import event_router

# Get event router stats
stats = event_router.get_stats()
print('Event Router Stats:', json.dumps(stats, indent=2))

# Try to get other metrics if available
try:
    from eliza.shared_memory import get_shared_memory
    mem = get_shared_memory()
    if hasattr(mem, 'get_stats'):
        print('Shared Memory Stats:', json.dumps(mem.get_stats(), indent=2))
except Exception as e:
    print(f'Shared memory stats not available: {e}')
" 2>/dev/null || echo "Metrics not available"
}

# Backup configuration
backup_config() {
    local backup_dir="backups/$(date +'%Y%m%d_%H%M%S')"
    
    log "Creating configuration backup in $backup_dir..."
    
    cd "$PROJECT_DIR"
    mkdir -p "$backup_dir"
    
    # Backup configs (without secrets)
    cp -r config/ "$backup_dir/"
    cp docker-compose-production.yaml "$backup_dir/"
    cp env.template "$backup_dir/"
    
    # Create deployment snapshot
    docker-compose -f docker-compose-production.yaml config > "$backup_dir/resolved-compose.yaml"
    
    success "Configuration backed up to $backup_dir"
}

# Scale engagement
scale_engagement() {
    local agent=$1
    local action=$2  # "up" or "down"
    
    if [ -z "$agent" ] || [ -z "$action" ]; then
        error "Usage: scale_engagement <agent> <up|down>"
        return 1
    fi
    
    log "Scaling engagement $action for $agent..."
    
    case $action in
        "up")
            warning "Increasing posting frequency for $agent"
            # This would typically modify the engagement config and restart
            ;;
        "down") 
            warning "Decreasing posting frequency for $agent"
            # This would typically modify the engagement config and restart
            ;;
        *)
            error "Invalid action: $action. Use 'up' or 'down'"
            return 1
            ;;
    esac
    
    warning "Manual configuration update required in config/production/engagement.yaml"
    warning "Then run: $0 reload-personas"
}

# Emergency stop
emergency_stop() {
    error "EMERGENCY STOP initiated"
    
    cd "$PROJECT_DIR"
    
    # Stop all services immediately
    docker-compose -f docker-compose-production.yaml down
    
    error "All services stopped. System is offline."
    log "To restart: cd $PROJECT_DIR && docker-compose -f docker-compose-production.yaml up -d"
}

# Show help
show_help() {
    echo "ElizaOS Swarm Operational Runbook"
    echo "================================="
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  dry-run [duration]     - Manual dry-run (default: 300s)"
    echo "  reload-personas        - Hot-reload personas (restart swarm)"  
    echo "  force-stop            - Force-stop swarm service"
    echo "  inspect-redis         - Inspect Redis memory and keys"
    echo "  inspect-logs [service] [lines] [filter] - Inspect logs"
    echo "  status                - Get service status and health"
    echo "  monitor-logs [service] - Monitor real-time logs"
    echo "  metrics               - Get application metrics"
    echo "  backup-config         - Backup configuration"
    echo "  scale-engagement <agent> <up|down> - Scale engagement"
    echo "  emergency-stop        - EMERGENCY: Stop all services"
    echo ""
    echo "Examples:"
    echo "  $0 dry-run 600        - Run 10-minute dry test"
    echo "  $0 inspect-logs swarm 50 ERROR - Show last 50 lines with ERROR"
    echo "  $0 scale-engagement agent2 down - Reduce agent2 posting"
    echo ""
}

# Main command handler
case ${1:-""} in
    "dry-run")
        dry_run "$2"
        ;;
    "reload-personas")
        reload_personas
        ;;
    "force-stop")
        force_stop
        ;;
    "inspect-redis")
        inspect_redis
        ;;
    "inspect-logs")
        inspect_logs "$2" "$3" "$4"
        ;;
    "status")
        get_status
        ;;
    "monitor-logs")
        monitor_logs "$2"
        ;;
    "metrics")
        get_metrics
        ;;
    "backup-config")
        backup_config
        ;;
    "scale-engagement")
        scale_engagement "$2" "$3"
        ;;
    "emergency-stop")
        emergency_stop
        ;;
    "help"|"")
        show_help
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 