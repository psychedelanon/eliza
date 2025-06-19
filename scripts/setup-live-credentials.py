#!/usr/bin/env python3
"""
Secure Twitter Credentials Setup for Live Mode
"""

import os
import getpass
from dotenv import load_dotenv, set_key

def setup_live_credentials():
    """Interactive setup for real Twitter API credentials"""
    print("🔑 ElizaOS Live Credentials Setup")
    print("=" * 50)
    print("⚠️  WARNING: This will enable REAL Twitter posting!")
    print("📝 You'll need Twitter API credentials for each agent")
    print("🔗 Get them from: https://developer.twitter.com/en/portal/dashboard")
    print()
    
    # Confirm intent
    confirm = input("⚡ Are you ready to go LIVE? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("❌ Setup cancelled. Staying in simulation mode.")
        return False
    
    print("\n🎭 Setting up credentials for 4 agents...")
    
    agents = [
        ("Agent1", "LoreMaster - Bitcoin Philosopher"),
        ("Agent2", "HypeBeast - Price Bot"),
        ("Agent3", "MemeLord - Meme Creator"),
        ("Agent4", "AlphaScry - Market Analyst")
    ]
    
    env_file = ".env"
    
    for agent_num, (agent_id, description) in enumerate(agents, 1):
        print(f"\n🤖 {agent_id}: {description}")
        print("-" * 40)
        
        # Get credentials for this agent
        api_key = getpass.getpass(f"Enter API Key for {agent_id}: ")
        api_secret = getpass.getpass(f"Enter API Secret for {agent_id}: ")
        access_token = getpass.getpass(f"Enter Access Token for {agent_id}: ")
        access_secret = getpass.getpass(f"Enter Access Token Secret for {agent_id}: ")
        
        if not all([api_key, api_secret, access_token, access_secret]):
            print(f"❌ Missing credentials for {agent_id}. Skipping...")
            continue
        
        # Update .env file
        set_key(env_file, f"TWITTER_AGENT{agent_num}_API_KEY", api_key)
        set_key(env_file, f"TWITTER_AGENT{agent_num}_API_SECRET", api_secret)
        set_key(env_file, f"TWITTER_AGENT{agent_num}_ACCESS_TOKEN", access_token)
        set_key(env_file, f"TWITTER_AGENT{agent_num}_ACCESS_SECRET", access_secret)
        
        print(f"✅ {agent_id} credentials saved!")
    
    # Disable dry run mode
    set_key(env_file, "DRY_RUN", "false")
    set_key(env_file, "SIMULATION_MODE", "false")
    
    print("\n🎯 Live Mode Configuration Complete!")
    print("✅ DRY_RUN disabled")
    print("✅ SIMULATION_MODE disabled")
    print("🔴 LIVE MODE ENABLED")
    
    print("\n⚠️  FINAL WARNING:")
    print("   • Agents will now post REAL tweets")
    print("   • Rate limits: 2-4 posts/hour per agent")
    print("   • Monitor carefully for the first hour")
    
    final_confirm = input("\n🚨 Start LIVE swarm now? (yes/no): ").lower().strip()
    return final_confirm == 'yes'

def main():
    """Main setup function"""
    try:
        ready_to_start = setup_live_credentials()
        
        if ready_to_start:
            print("\n🚀 Starting LIVE ElizaOS Swarm...")
            print("📊 Monitor with: python scripts/live-swarm-monitor.py")
            print("🛑 Stop with: Get-Process python* | Stop-Process")
            
            # Start the live swarm
            os.system("python run.py --swarm")
        else:
            print("\n🟡 Live mode setup complete but not started")
            print("🔧 Start manually with: python run.py --swarm")
            
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")

if __name__ == "__main__":
    main() 