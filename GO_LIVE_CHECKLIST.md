# ElizaOS Swarm Go-Live Checklist

This checklist implements the production deployment playbook for taking the swarm from development to live 24/7 operation.

## Prerequisites (Before Starting)

### ✅ Step 0: Local CI Cleanup

- [ ] Fixed `make test` target in Makefile
- [ ] Run `python -m pytest tests/ -q -m "not slow" --disable-warnings`
- [ ] Verify 121+ tests passing with minimal failures
- [ ] Basic linting checks completed

### ✅ Environment Setup

- [ ] Copy `env.template` to `.env`
- [ ] Configure Twitter API credentials for all agents
- [ ] Set OpenAI API key
- [ ] Configure Redis URL
- [ ] Set secure Grafana password
- [ ] Review all environment variables

### ✅ Configuration

- [ ] Production engagement config in `config/production/engagement.yaml`
- [ ] Persona YAML files in place
- [ ] Docker Compose production file ready
- [ ] Monitoring configuration (Loki/Grafana) prepared

## Stage A: Beta Deployment (24 hours)

### Infrastructure

- [ ] Docker and Docker Compose installed
- [ ] Redis service healthy
- [ ] Loki/Grafana stack optional but recommended

### Deployment

- [ ] Run: `bash scripts/deploy-production.sh A`
- [ ] Verify only Agent2 (HypeBeast) is in live mode
- [ ] Confirm 5-minute startup delay working
- [ ] Check health endpoints responding

### Monitoring (24 hours)

- [ ] Monitor logs for rate-limit errors
- [ ] Track tweet volume (should be ~2 per hour max)
- [ ] Verify Redis memory usage stable
- [ ] No error bursts or crashes
- [ ] Tweet content quality appropriate

### Success Criteria for Stage A

- [ ] Zero 403 errors (account lockdowns)
- [ ] Rate limits staying well under 300 tweets/3h cap
- [ ] System runs stably for 24 hours
- [ ] Memory usage stable (Redis < 80%)
- [ ] All tweets pass content moderation

## Stage B: Add Meme Agent (48 hours)

### Deployment

- [ ] Update `config/production/engagement.yaml` - set `agent3.live_mode: true`
- [ ] Run: `bash scripts/deploy-production.sh B`
- [ ] Verify Agent2 + Agent3 both active
- [ ] Total posting rate ~5 tweets per hour maximum

### Monitoring (48 hours)

- [ ] Cross-engagement between agents working
- [ ] No argument spam or loops
- [ ] Combined rate limits still safe
- [ ] Distinct persona voices maintained

### Success Criteria for Stage B

- [ ] All Stage A criteria maintained
- [ ] Agent interactions natural and diverse
- [ ] No duplicate or near-duplicate content
- [ ] Combined error rate < 5%

## Stage C: Progressive Activation (72 hours)

### Deployment

- [ ] Enable Agent1 and Agent4 in engagement config
- [ ] Run: `bash scripts/deploy-production.sh C`
- [ ] 4 agents active (50% of full swarm)
- [ ] Monitor for interaction complexity

### Monitoring (72 hours)

- [ ] Cross-agent reply chains working
- [ ] Fake argument system triggering appropriately
- [ ] Price reaction events distributed correctly
- [ ] No spam detection triggers

### Success Criteria for Stage C

- [ ] All previous criteria maintained
- [ ] Swarm behavior emergent but controlled
- [ ] Twitter engagement metrics healthy
- [ ] No community complaints or flags

## Stage D: Full Swarm (Permanent)

### Final Deployment

- [ ] Enable Agent5 (all agents live)
- [ ] Run: `bash scripts/deploy-production.sh D`
- [ ] Full swarm operational
- [ ] All personas active and distinctive

### Production Operations

- [ ] Monitor continuously for first week
- [ ] Set up alerting on error rates
- [ ] Schedule regular config backups
- [ ] Document any manual interventions needed

## Operational Procedures

### Daily Operations

- [ ] Check service health: `bash scripts/operational-runbook.sh status`
- [ ] Review error logs: `bash scripts/operational-runbook.sh inspect-logs`
- [ ] Monitor Redis usage: `bash scripts/operational-runbook.sh inspect-redis`
- [ ] Backup configurations: `bash scripts/operational-runbook.sh backup-config`

### Emergency Procedures

- [ ] **Rate limit burst**: Run `bash scripts/operational-runbook.sh scale-engagement <agent> down`
- [ ] **Account 403 error**: Rotate credentials in `.env`, restart affected agent
- [ ] **Redis crash**: Restart Redis service, system will recover automatically
- [ ] **Complete failure**: Run `bash scripts/operational-runbook.sh emergency-stop`

### Rollback Procedures

- [ ] **Stage rollback**: Run `bash scripts/deploy-production.sh rollback`
- [ ] **Configuration rollback**: Restore from `backups/` directory
- [ ] **Emergency stop**: All services stop, manual restart required

## Compliance & Safety

### Twitter Automation Rules

- [ ] No identical tweets across accounts ✅ (persona system ensures diversity)
- [ ] 1+ second gap between posts ✅ (scheduler jitter implemented)
- [ ] Rate limits well under official caps ✅ (50 tweets/hour vs 300/3h limit)
- [ ] No spam indicators ✅ (quality validation system)

### Security

- [ ] Private keys in environment variables only (not code)
- [ ] `.env` file in `.gitignore` and never committed
- [ ] API keys rotated if any exposure suspected
- [ ] Container runs as non-root user

### Monitoring & Alerting

- [ ] Log aggregation working (Loki)
- [ ] Error rate alerting configured
- [ ] Memory usage monitoring
- [ ] Tweet volume tracking dashboard

## Final Go Checklist

- [ ] **Tests green locally**: pytest passing
- [ ] **Image built and tagged**: `ghcr.io/psychedelanon/eliza:0.4.0-alpha2`
- [ ] **Environment configured**: Real Twitter API keys in `.env`
- [ ] **Redis accessible**: From swarm containers
- [ ] **Dry-run successful**: 10+ minutes without errors
- [ ] **Stage A deployed**: Only Agent2 live for 24h
- [ ] **Backups created**: Config and deployment snapshots
- [ ] **Monitoring active**: Logs flowing to Loki/Grafana

## Post-Deployment

### Success Metrics

- [ ] **Uptime**: > 99% after first week
- [ ] **Error rate**: < 1% of all operations
- [ ] **Rate limit compliance**: Never exceed 80% of Twitter limits
- [ ] **Content quality**: No community strikes or warnings
- [ ] **Engagement**: Natural Twitter community interaction

### Next Steps

- [ ] Monitor for 1 week intensively
- [ ] Gather community feedback
- [ ] Optimize posting schedules based on engagement
- [ ] Consider adding new personas or features
- [ ] Scale to additional regions/languages if successful

---

**🚀 Ready for launch! "Hello, Crypto Twitter" - The ElizaOS Swarm is live!**
