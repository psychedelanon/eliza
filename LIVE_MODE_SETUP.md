# 🚀 ElizaOS Swarm - LIVE MODE Setup Guide

## ⚠️ WARNING: LIVE MODE = REAL TWITTER POSTS

This guide will help you transition from simulation to **LIVE Twitter posting** with real API credentials.

## 🔑 Method 1: Interactive Setup (Recommended)

Run the secure credential setup script:

```bash
python scripts/setup-live-credentials.py
```

This will:

- ✅ Securely prompt for Twitter API credentials
- ✅ Update your .env file automatically
- ✅ Disable simulation mode
- ✅ Start the live swarm

## 🔑 Method 2: Manual Setup

### Step 1: Get Twitter API Credentials

For **each agent**, get these from https://developer.twitter.com/en/portal/dashboard:

- API Key (Consumer Key)
- API Secret (Consumer Secret)
- Access Token
- Access Token Secret

### Step 2: Update .env File

Replace the dummy credentials with real ones:

```env
# Agent 1 (LoreMaster - Bitcoin Philosopher)
TWITTER_AGENT1_API_KEY=your_real_api_key_here
TWITTER_AGENT1_API_SECRET=your_real_api_secret_here
TWITTER_AGENT1_ACCESS_TOKEN=your_real_access_token_here
TWITTER_AGENT1_ACCESS_SECRET=your_real_access_secret_here

# Agent 2 (HypeBeast - Price Bot)
TWITTER_AGENT2_API_KEY=your_real_api_key_here
TWITTER_AGENT2_API_SECRET=your_real_api_secret_here
TWITTER_AGENT2_ACCESS_TOKEN=your_real_access_token_here
TWITTER_AGENT2_ACCESS_SECRET=your_real_access_secret_here

# Agent 3 (MemeLord - Meme Creator)
TWITTER_AGENT3_API_KEY=your_real_api_key_here
TWITTER_AGENT3_API_SECRET=your_real_api_secret_here
TWITTER_AGENT3_ACCESS_TOKEN=your_real_access_token_here
TWITTER_AGENT3_ACCESS_SECRET=your_real_access_secret_here

# Agent 4 (AlphaScry - Market Analyst)
TWITTER_AGENT4_API_KEY=your_real_api_key_here
TWITTER_AGENT4_API_SECRET=your_real_api_secret_here
TWITTER_AGENT4_ACCESS_TOKEN=your_real_access_token_here
TWITTER_AGENT4_ACCESS_SECRET=your_real_access_secret_here

# Disable simulation mode
DRY_RUN=false
SIMULATION_MODE=false
```

### Step 3: Start Live Swarm

```bash
python run.py --swarm
```

## 📊 Live Mode Monitoring

### Real-time Status Monitor

```bash
python scripts/live-swarm-monitor.py
```

### Quick Status Check

```bash
python scripts/quick-status.py
```

### Stop the Swarm

```bash
Get-Process python* | Stop-Process
```

## ⚡ Expected Live Behavior

| Agent      | Role       | Posting Rate | Focus                             |
| ---------- | ---------- | ------------ | --------------------------------- |
| **Agent1** | LoreMaster | 2 posts/hour | Bitcoin philosophy, deep thoughts |
| **Agent2** | HypeBeast  | 2 posts/hour | Price updates, market hype        |
| **Agent3** | MemeLord   | 3 posts/hour | Memes, viral content              |
| **Agent4** | AlphaScry  | 4 posts/hour | Market analysis, predictions      |

**Total Expected Activity:** ~11 real tweets per hour across all agents

## 🛡️ Safety Features

- **Rate Limiting:** Built-in Twitter API rate limit handling
- **Backoff Logic:** Automatic delays when hitting limits
- **Error Recovery:** Graceful handling of API errors
- **Monitoring:** Real-time status and health checks

## 🚨 Emergency Procedures

### Immediate Stop

```bash
Get-Process python* | Stop-Process -Force
```

### Return to Simulation Mode

```bash
# Edit .env file:
DRY_RUN=true
SIMULATION_MODE=true
```

### Check Current Status

```bash
python scripts/live-swarm-monitor.py
```

## 📈 First Hour Checklist

- [ ] ✅ All 4 agents initialized successfully
- [ ] ✅ First tweets posted within 15 minutes
- [ ] ✅ No rate limit errors in first 30 minutes
- [ ] ✅ Agent personalities are distinct and appropriate
- [ ] ✅ No duplicate or spam-like content
- [ ] ✅ Price updates are accurate (Agent2)
- [ ] ✅ Memes are appropriate and engaging (Agent3)

## 🎯 Success Metrics

**Hour 1:**

- 8-12 total tweets posted
- 0-1 rate limit backoffs (acceptable)
- All agents active and posting
- Distinct personality voices

**Day 1:**

- 200-300 total tweets
- Healthy engagement rates
- No Twitter account restrictions
- Stable system operation

---

## 🚀 Ready to Go Live?

Choose your setup method:

**Option 1 (Recommended):**

```bash
python scripts/setup-live-credentials.py
```

**Option 2 (Manual):**

1. Edit `.env` file with real credentials
2. Set `DRY_RUN=false` and `SIMULATION_MODE=false`
3. Run `python run.py --swarm`

**Good luck! Your ElizaOS Swarm is ready for the real world! 🤖🚀**
