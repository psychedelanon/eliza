#!/usr/bin/env python3
"""
Setup script for live swarm engagement.
This script helps configure environment variables for all agents.
"""

import os
import sys
from pathlib import Path

def create_env_template():
    """Create a template .env file with all required variables."""
    
    env_content = """# Eliza Live Swarm Configuration
# Copy this to .env and fill in your actual Twitter API credentials

# Agent2 (Price Analyst) - Posts BTC vs HPO comparisons
TWITTER_AGENT1_API_KEY=your_agent2_api_key_here
TWITTER_AGENT1_API_SECRET=your_agent2_api_secret_here
TWITTER_AGENT1_ACCESS_TOKEN=your_agent2_access_token_here
TWITTER_AGENT1_ACCESS_SECRET=your_agent2_access_secret_here

# LoreMaster - Mythic lore master
TWITTER_AGENT2_API_KEY=your_loremaster_api_key_here
TWITTER_AGENT2_API_SECRET=your_loremaster_api_secret_here
TWITTER_AGENT2_ACCESS_TOKEN=your_loremaster_access_token_here
TWITTER_AGENT2_ACCESS_SECRET=your_loremaster_access_secret_here

# MemeLord - Ultimate meme lord
TWITTER_AGENT3_API_KEY=your_memelord_api_key_here
TWITTER_AGENT3_API_SECRET=your_memelord_api_secret_here
TWITTER_AGENT3_ACCESS_TOKEN=your_memelord_access_token_here
TWITTER_AGENT3_ACCESS_SECRET=your_memelord_access_secret_here

# AlphaScry - Alpha scryer
TWITTER_AGENT4_API_KEY=your_alphascry_api_key_here
TWITTER_AGENT4_API_SECRET=your_alphascry_api_secret_here
TWITTER_AGENT4_ACCESS_TOKEN=your_alphascry_access_token_here
TWITTER_AGENT4_ACCESS_SECRET=your_alphascry_access_secret_here

# GremlinGM - Chaotic game master
TWITTER_AGENT5_API_KEY=your_gremlingm_api_key_here
TWITTER_AGENT5_API_SECRET=your_gremlingm_api_secret_here
TWITTER_AGENT5_ACCESS_TOKEN=your_gremlingm_access_token_here
TWITTER_AGENT5_ACCESS_SECRET=your_gremlingm_access_secret_here

# SwarmCoordinator - Event coordinator (no posting needed)
TWITTER_AGENT6_API_KEY=your_coordinator_api_key_here
TWITTER_AGENT6_API_SECRET=your_coordinator_api_secret_here
TWITTER_AGENT6_ACCESS_TOKEN=your_coordinator_access_token_here
TWITTER_AGENT6_ACCESS_SECRET=your_coordinator_access_secret_here

# OpenAI API Key (for LLM calls)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Redis URL for shared memory (leave empty for in-process)
# REDIS_URL=redis://localhost:6379

# Optional: Enable media generation
# MEDIA_ENABLE=true

# Optional: Dry run mode (set to false for live posting)
# DRY_RUN=false
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print(f"⚠️  .env file already exists. Backing up to .env.backup")
        env_file.rename(".env.backup")
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env template file")
    print("📝 Please edit .env and add your actual Twitter API credentials")
    print("🔑 You'll need Twitter API keys for each agent account")

def check_env_setup():
    """Check if environment variables are properly configured."""
    
    required_vars = [
        "TWITTER_AGENT1_API_KEY",  # Agent2
        "TWITTER_AGENT2_API_KEY",  # LoreMaster
        "TWITTER_AGENT3_API_KEY",  # MemeLord
        "TWITTER_AGENT4_API_KEY",  # AlphaScry
        "TWITTER_AGENT5_API_KEY",  # GremlinGM
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Run: python scripts/setup_live_swarm.py --create-template")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def show_usage_instructions():
    """Show instructions for running the live swarm."""
    
    print("\n🚀 Live Swarm Usage Instructions:")
    print("=" * 50)
    print("1. First, ensure all environment variables are set in .env")
    print("2. Test in dry-run mode:")
    print("   python run.py --swarm --dry-run --demo")
    print("3. Run live swarm (posts every 6 hours):")
    print("   python run.py --swarm")
    print("4. Run live swarm with Agent2 posting now:")
    print("   python run.py --swarm --once")
    print("\n📊 Expected Behavior:")
    print("- Agent2 posts BTC vs HPO price comparison")
    print("- All persona agents react within 30-120 seconds")
    print("- Each agent uses unique personality in replies")
    print("- Cross-engagement metrics are tracked")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--create-template":
        create_env_template()
    elif len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_env_setup()
    else:
        print("🔧 Eliza Live Swarm Setup")
        print("=" * 30)
        print("Commands:")
        print("  --create-template  Create .env template file")
        print("  --check            Check if env vars are configured")
        print("  (no args)          Show this help")
        
        if check_env_setup():
            show_usage_instructions()

if __name__ == "__main__":
    main() 