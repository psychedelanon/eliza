#!/usr/bin/env python3
"""
Real Live Swarm Monitor - Monitor the actual swarm running via run.py
"""

import time
import subprocess
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

def check_swarm_status():
    """Check if real swarm processes are running"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Process python* | Measure-Object | Select-Object -ExpandProperty Count"],
            capture_output=True,
            text=True,
            shell=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        return count
    except:
        return 0

def check_configuration():
    """Check environment configuration"""
    load_dotenv()
    
    config = {
        "llm_provider": os.getenv("ELIZA_LLM_PROVIDER", "openai"),
        "anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",
        "simulation": os.getenv("SIMULATION_MODE", "false").lower() == "true",
        "agent1_creds": bool(os.getenv("TWITTER_AGENT1_API_KEY")),
        "agent2_creds": bool(os.getenv("TWITTER_AGENT2_API_KEY")),
        "agent3_creds": bool(os.getenv("TWITTER_AGENT3_API_KEY")),
        "agent4_creds": bool(os.getenv("TWITTER_AGENT4_API_KEY"))
    }
    return config

def print_status():
    """Print current real swarm status"""
    print("\n" + "="*70)
    print(f"🤖 REAL ElizaOS Swarm Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Check processes
    process_count = check_swarm_status()
    if process_count > 1:
        print(f"📊 Swarm Processes: 🟢 {process_count} RUNNING")
    else:
        print(f"📊 Swarm Processes: 🔴 {process_count} (may be stopped)")
    
    # Check configuration
    config = check_configuration()
    print(f"🧠 LLM Provider: {'🟢 Anthropic' if config['llm_provider'] == 'anthropic' else '🟡 OpenAI'}")
    print(f"🔑 Anthropic API: {'🟢 Set' if config['anthropic_key'] else '🔴 Missing'}")
    print(f"🔑 OpenAI API: {'🟢 Set' if config['openai_key'] else '🔴 Missing'}")
    print(f"🎭 Mode: {'🟡 DRY RUN' if config['dry_run'] else '🔴 LIVE'}")
    print(f"🎲 Simulation: {'🟢 Enabled' if config['simulation'] else '🔴 Disabled'}")
    
    # Agent credentials status
    print(f"\n🎭 Agent Credentials:")
    agents = [
        ("Agent1 (LoreMaster)", config['agent1_creds']),
        ("Agent2 (HypeBeast)", config['agent2_creds']),
        ("Agent3 (MemeLord)", config['agent3_creds']),
        ("Agent4 (AlphaScry)", config['agent4_creds'])
    ]
    
    for agent_name, has_creds in agents:
        status = "🟢 Ready" if has_creds else "🔴 Missing Creds"
        print(f"   • {agent_name}: {status}")
    
    # Current expected behavior
    print(f"\n⚡ Expected Behavior:")
    if config['dry_run']:
        print(f"   • Mode: DRY RUN (simulated tweets)")
        print(f"   • Output: Console logs only")
        print(f"   • Safety: No real Twitter posts")
    else:
        print(f"   • Mode: LIVE (real tweets)")
        print(f"   • Output: Actual Twitter posts")
        print(f"   • Rate: 2-4 posts/hour per agent")
    
    print(f"   • LLM: Claude-3-Sonnet (Anthropic)")
    print(f"   • Duration: Continuous (until stopped)")
    
    # Show process details
    if process_count > 1:
        print(f"\n🎯 System Status: ACTIVE")
        print(f"   • Real swarm architecture running")
        print(f"   • All agents should be initialized")
        print(f"   • Check console output for activity")
    else:
        print(f"\n⚠️  Warning: Few/No processes detected")
        print(f"   • Run: python run.py --swarm --dry-run")

def main():
    """Main monitoring loop"""
    print("🚀 Starting Real ElizaOS Swarm Monitor...")
    
    try:
        while True:
            print_status()
            print(f"\n⏱️  Next update in 30 seconds... (Ctrl+C to exit)")
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"\n\n👋 Monitor stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 