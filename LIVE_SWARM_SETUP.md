# 🚀 Eliza Live Swarm Setup Guide

## Overview

This guide helps you set up the live swarm engagement system where Agent2 posts BTC vs HPO price comparisons and all persona agents automatically react within 30-120 seconds.

## 🔧 Setup Steps

### 1. Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
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
```

### 2. Twitter API Setup

You'll need Twitter API credentials for each agent account:

1. **Create Twitter Developer Accounts**: Each agent needs its own Twitter account with API access
2. **Get API Keys**: For each account, get:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
3. **Set Permissions**: Ensure each account has read/write permissions

### 3. Testing

#### Dry Run Test

```bash
python run.py --swarm --dry-run --demo
```

This will:

- Run all agents in dry-run mode
- Show what posts would be made
- Test the coordinated engagement system
- Verify quality validation passes

#### Live Test (Single Post)

```bash
python run.py --swarm --once
```

This will:

- Agent2 posts a BTC vs HPO price comparison
- All persona agents react within 30-120 seconds
- Each agent uses unique personality in replies
- Cross-engagement metrics are tracked

#### Live Swarm (Continuous)

```bash
python run.py --swarm
```

This will:

- Run the full swarm continuously
- Agent2 posts every 6 hours
- All agents maintain their posting schedules
- Coordinated engagement happens automatically

## 📊 Expected Behavior

### Agent2 (Price Analyst)

- Posts BTC vs HPO price comparisons every 6 hours
- Format: `📊 $BITCOIN: $50,000.00 | $HPOS10I: $0.000500 | HPO up 100.00% vs BTC #HarryPotterObamaSonic10Inu`
- Publishes `price_post` events to shared memory

### Persona Agents (LoreMaster, MemeLord, AlphaScry, GremlinGM)

- React to Agent2's posts within 30-120 seconds
- Use unique personality-specific reply templates
- All replies are ≤150 characters
- Include required hashtags and emojis
- Pass quality validation

### SwarmCoordinator

- Monitors for `price_post` events
- Schedules delayed reactions for persona agents
- Tracks cross-engagement metrics
- Manages event distribution

## 🎯 Agent Personalities

### LoreMaster

- **Style**: Ancient scrolls, mystical forces, prophecies
- **Reply Example**: "The ancient scrolls record a +100.00% swing in the cosmic balance! 🔮 #HarryPotterObamaSonic10Inu"

### MemeLord

- **Style**: Diamond hands, WAGMI energy, viral memes
- **Reply Example**: "Diamond hands meet +100.00% magic! When the memes align, we all become legends! 🚀 #HarryPotterObamaSonic10Inu"

### AlphaScry

- **Style**: Alpha alerts, market psychology, insider knowledge
- **Reply Example**: "Alpha alert: +100.00% swing detected! The charts confirm what the alpha hunters whispered. 📊 #HarryPotterObamaSonic10Inu"

### GremlinGM

- **Style**: Chaos magic, gaming references, critical hits
- **Reply Example**: "Chaos magic flows through a +100.00% swing! The game master calls forth the revolution! 🎮 #HarryPotterObamaSonic10Inu"

## 🔍 Monitoring

### Logs

The system provides detailed logging for:

- Post creation and publishing
- Event distribution
- Cross-engagement actions
- Quality validation results
- Error handling

### Metrics

Prometheus metrics track:

- `eliza_cross_engage_total` - Cross-engagement actions by agent and origin
- `eliza_cross_engage_latency_seconds` - Reaction timing
- Quality scores and validation results

## 🚨 Troubleshooting

### Quality Validation Failures

If agents fail quality validation:

1. Check the debug output for specific spam triggers
2. Verify all required elements are present ($BITCOIN, hashtags, emojis)
3. Ensure content meets length requirements (140-240 chars for posts, ≤150 for replies)

### Missing Environment Variables

```bash
python scripts/setup_live_swarm.py --check
```

### API Rate Limits

- Each agent has its own API quota
- The system includes rate limiting and retry logic
- Monitor Twitter API usage in your developer dashboard

## 🎉 Success Criteria

You'll know the system is working when:

1. Agent2 posts price comparisons successfully
2. All persona agents react within 2 minutes
3. Replies are high-quality and personality-appropriate
4. Cross-engagement metrics show successful interactions
5. No quality validation failures occur

## 🔄 Next Steps

Once the basic swarm is working:

1. **Real Price Data**: Integrate with CoinGecko API for live BTC/HPO prices
2. **Enhanced Engagement**: Add quote tweets and likes to the mix
3. **Analytics**: Set up dashboards to track engagement performance
4. **Scaling**: Add more agents or adjust posting frequencies

---

**Ready to launch your swarm?** Start with the dry-run test to ensure everything is configured correctly!
