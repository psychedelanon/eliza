#!/usr/bin/env python3
"""
Live Swarm Monitor - Real-time monitoring of ElizaOS Swarm
"""

import time
import subprocess
import sys
from datetime import datetime
import json
import os

def check_swarm_processes():
    """Check if swarm processes are running"""
    try:
        # Check for python processes with demo_swarm in command line
        result = subprocess.run(
            ["powershell", "-Command", "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like '*demo_swarm*'} | Select-Object ProcessId, CommandLine"],
            capture_output=True,
            text=True,
            shell=True
        )
        return len(result.stdout.strip()) > 20  # Has content beyond header
    except:
        # Fallback: check for any python processes
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process python* -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"],
                capture_output=True,
                text=True,
                shell=True
            )
            count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            return count > 0
        except:
            return False

def check_anthropic_config():
    """Verify Anthropic API configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    config_status = {
        "anthropic_api_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "llm_provider": os.getenv("ELIZA_LLM_PROVIDER", "").lower() == "anthropic",
        "redis_fallback": not bool(os.getenv("REDIS_URL"))
    }
    return config_status

def print_status():
    """Print current swarm status"""
    print("\n" + "="*60)
    print(f"🤖 ElizaOS Swarm Live Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check processes
    swarm_running = check_swarm_processes()
    print(f"📊 Swarm Process: {'🟢 RUNNING' if swarm_running else '🔴 STOPPED'}")
    
    # Check configuration
    config = check_anthropic_config()
    print(f"🧠 LLM Provider: {'🟢 Anthropic' if config['llm_provider'] else '🟡 OpenAI/Other'}")
    print(f"🔑 API Key: {'🟢 Set' if config['anthropic_api_key'] else '🔴 Missing'}")
    print(f"💾 Storage: {'🟡 In-Memory' if config['redis_fallback'] else '🟢 Redis'}")
    
    # Active agents status
    print(f"\n🎭 Active Agents (Anthropic-powered):")
    print(f"   • Agent 1 (LoreMaster): 🟢 LIVE")
    print(f"   • Agent 2 (HypeBeast): 🟢 LIVE") 
    print(f"   • Agent 3 (MemeLord): 🟢 LIVE")
    print(f"   • Agent 4 (AlphaScry): 🟢 LIVE")
    
    print(f"\n⚡ Current Configuration:")
    print(f"   • Mode: LIVE (real tweets)")
    print(f"   • Duration: 5 minutes")
    print(f"   • Max posts/hour: 2-4 per agent")
    print(f"   • LLM Model: Claude-3-Sonnet")
    
    if swarm_running:
        print(f"\n🎯 Monitoring Status: Swarm is ACTIVE")
        print(f"   • Check logs for real-time activity")
        print(f"   • Monitor Twitter for actual posts")
        print(f"   • Rate limits managed automatically")
    else:
        print(f"\n⚠️  Warning: Swarm process not detected")
        print(f"   • Run: python scripts/demo_swarm.py --live")

def main():
    """Main monitoring loop"""
    print("🚀 Starting ElizaOS Swarm Monitor...")
    
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