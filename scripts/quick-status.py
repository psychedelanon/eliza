#!/usr/bin/env python3
"""
Quick Status Check for ElizaOS Swarm
"""

import subprocess
import os
from datetime import datetime

def check_processes():
    """Check for running Python processes"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Process python* -ErrorAction SilentlyContinue | Format-Table ProcessName, Id, CPU -AutoSize"],
            capture_output=True,
            text=True,
            shell=True
        )
        return result.stdout.strip()
    except:
        return "Unable to check processes"

def check_config():
    """Check environment configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    config = {
        "LLM Provider": os.getenv("ELIZA_LLM_PROVIDER", "not set"),
        "Anthropic API": "✅ Set" if os.getenv("ANTHROPIC_API_KEY") else "❌ Missing",
        "OpenAI API": "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing"
    }
    return config

def main():
    print("🚀 ElizaOS Swarm Quick Status Check")
    print("=" * 50)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check configuration
    print("🔧 Configuration:")
    config = check_config()
    for key, value in config.items():
        print(f"   • {key}: {value}")
    print()
    
    # Check processes
    print("🖥️  Python Processes:")
    processes = check_processes()
    if processes and len(processes) > 50:
        print(processes)
    else:
        print("   • No Python processes detected")
    print()
    
    # Check if swarm should be running
    print("🎯 Expected Status:")
    print("   • Swarm should be running for 30 minutes")
    print("   • 4 agents active (LoreMaster, HypeBeast, MemeLord, AlphaScry)")
    print("   • Using Anthropic Claude-3-Sonnet")
    print("   • Rate: ~4 tweets/minute across all agents")
    print()
    
    print("💡 Commands:")
    print("   • Monitor: python scripts/monitor-live-swarm.py")
    print("   • Restart: python scripts/demo_swarm.py --live --duration 1800")
    print("   • Stop: Get-Process python* | Stop-Process")

if __name__ == "__main__":
    main() 