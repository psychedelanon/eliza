# Twitter Engagement Optimization Plugin for ElizaOS

A comprehensive plugin for optimizing Twitter engagement through network coordination, intelligent timing, and strategic amplification.

## 🚀 Features

### Network Coordination
- **Multi-Agent Coordination**: Synchronize engagement across multiple agents in your network
- **Real-time Communication**: Redis-based coordination system for instant agent communication
- **Smart Load Balancing**: Distributes engagement tasks based on agent capacity and specialization
- **Staggered Timing**: Prevents obvious bot-like behavior with natural engagement patterns

### Engagement Optimization
- **Performance Analytics**: Tracks engagement metrics and success rates
- **Optimal Timing**: Learns the best times to post and engage based on historical data
- **Dynamic Strategies**: Adapts engagement strategies based on performance feedback
- **Content-Aware Matching**: Matches agents to content based on their specializations

### Advanced Features
- **Trend Analysis**: Detects and capitalizes on trending topics
- **Cross-Amplification**: Coordinates amplification campaigns across the network
- **Performance Monitoring**: Real-time metrics and analytics
- **Smart Content Strategy**: AI-driven content optimization

## 📦 Installation

```bash
# Install the plugin
npm install @elizaos/plugin-twitter-engagement

# Install dependencies
npm install ioredis zod node-cron
```

## ⚙️ Configuration

### Environment Variables

```env
# Redis Configuration (required for network coordination)
REDIS_URL=redis://localhost:6379

# Network Coordination Settings
NETWORK_COORDINATION_ENABLED=true
MAX_NETWORK_AGENTS=10
COORDINATION_WINDOW_MS=300000

# Engagement Optimization
ENGAGEMENT_DELAY_MIN_MS=30000
ENGAGEMENT_DELAY_MAX_MS=300000
AMPLIFICATION_PROBABILITY=0.7

# Content Strategy
TRENDING_TOPICS_REFRESH_MS=600000
CONTENT_QUALITY_THRESHOLD=0.7

# Performance Monitoring
METRICS_RETENTION_HOURS=168
ANALYTICS_BATCH_SIZE=100

# Smart Timing
OPTIMAL_POSTING_HOURS=8,12,17,20
TIMEZONE_OFFSET=0

# Network Analytics
INFLUENCE_SCORE_WEIGHT=0.3
ENGAGEMENT_RATE_WEIGHT=0.4
REACH_WEIGHT=0.3
```

### Plugin Registration

```typescript
import { twitterEngagementPlugin } from '@elizaos/plugin-twitter-engagement';

export const character = {
  name: 'YourAgent',
  plugins: [
    '@elizaos/plugin-twitter',
    '@elizaos/plugin-twitter-engagement',
  ],
  // ... other configuration
};
```

## 🎯 Usage

### Basic Network Coordination

```typescript
// Request coordinated engagement
await runtime.processActions(
  {
    content: {
      text: 'Coordinate likes and retweets for this viral AI post',
      url: 'https://twitter.com/user/status/1234567890',
    },
  },
  [],
  state
);
```

### Advanced Engagement Strategies

```typescript
// High-urgency amplification
await runtime.processActions(
  {
    content: {
      text: 'Breaking: Major crypto regulation news needs immediate network amplification',
      url: 'https://twitter.com/news/status/1234567890',
    },
  },
  [],
  state
);
```

### Strategic Content Posting

```typescript
// Optimal timing for maximum engagement
await runtime.processActions(
  {
    content: {
      text: 'Schedule this important announcement at optimal engagement time',
    },
  },
  [],
  state
);
```

## 🔧 Services

### NetworkCoordinationService

Handles multi-agent coordination and communication:

```typescript
const networkService = runtime.getService('network-coordination');

// Announce a new post to the network
await networkService.announcePost(postId, content, hashtags);

// Request engagement from other agents
await networkService.requestEngagement(postId, 'like', 'high');

// Get network status
const status = await networkService.getNetworkStatus();
```

### EngagementOptimizationService

Optimizes engagement timing and strategies:

```typescript
const engagementService = runtime.getService('engagement-optimization');

// Get optimal engagement strategy
const strategy = engagementService.getOptimalEngagementStrategy({
  contentType: 'video',
  hashtags: ['AI', 'tech'],
  urgency: 'high',
});

// Find best posting time
const optimalTime = engagementService.getOptimalPostingTime(24, 'breaking');

// Record engagement metrics
await engagementService.recordEngagementMetrics({
  postId: '1234567890',
  impressions: 5000,
  likes: 250,
  retweets: 75,
  replies: 50,
  timestamp: Date.now(),
  reach: 3000,
  engagementRate: 7.5,
});
```

## 📊 Analytics and Monitoring

### Performance Metrics

The plugin tracks comprehensive engagement metrics:

- **Engagement Rate**: Likes, retweets, replies per impression
- **Reach**: Total unique users reached
- **Influence Score**: Network influence based on engagement quality
- **Conversion Rate**: Actions taken per engagement
- **Timing Effectiveness**: Performance by time of day and day of week

### Network Status

Monitor your agent network in real-time:

```typescript
const networkStatus = await networkService.getNetworkStatus();
console.log(`Active agents: ${networkStatus.activeAgents}`);
console.log(`Network capacity: ${networkStatus.totalCapacity}`);
console.log(`Current load: ${networkStatus.currentLoad}`);
```

### Engagement Insights

Get actionable insights from your engagement data:

```typescript
const insights = engagementService.getEngagementInsights();
console.log('Recommendations:', insights.recommendations);
console.log('Best performing times:', insights.bestPerformingTimes);
console.log('Top strategies:', insights.topStrategies);
```

## 🎛️ Actions

### COORDINATED_ENGAGEMENT

Coordinates engagement across multiple agents:

**Triggers:**
- "Coordinate engagement on this post"
- "Network amplification needed"
- "Boost this trending topic"

**Parameters:**
- `targetPostId`: Post to engage with
- `engagementType`: like, retweet, reply, quote, thread
- `urgency`: low, medium, high
- `networkBoost`: Enable network-wide amplification

### STRATEGIC_POST

Posts content at optimal times with coordinated engagement:

**Triggers:**
- "Post this at optimal time"
- "Schedule strategic announcement"
- "Coordinate content launch"

### AMPLIFY_POST

Amplifies existing posts through the network:

**Triggers:**
- "Amplify this post"
- "Viral boost needed"
- "Network amplification"

### NETWORK_REPLY

Coordinates contextual replies across agents:

**Triggers:**
- "Coordinate replies"
- "Network response needed"
- "Engage with discussion"

## 🔮 Providers

### trendingTopicsProvider

Provides real-time trending topics:

```typescript
// Access trending topics in templates
{{trendingTopics}} // Returns current trending hashtags and topics
```

### networkMetricsProvider

Provides network performance metrics:

```typescript
// Network status in context
{{networkMetrics}} // Returns active agents, capacity, load
```

### engagementOpportunitiesProvider

Identifies high-potential engagement opportunities:

```typescript
// Engagement opportunities
{{engagementOpportunities}} // Returns posts with high engagement potential
```

### optimalTimingProvider

Provides optimal posting and engagement times:

```typescript
// Optimal timing data
{{optimalTiming}} // Returns best times for current conditions
```

## 🧪 Evaluators

### engagementQualityEvaluator

Evaluates the quality of engagement activities:

- Measures engagement authenticity
- Tracks engagement effectiveness
- Identifies improvement opportunities

### networkCoordinationEvaluator

Evaluates network coordination effectiveness:

- Measures coordination success rate
- Identifies coordination bottlenecks
- Optimizes network performance

### contentRelevanceEvaluator

Evaluates content relevance for engagement:

- Measures content-agent alignment
- Identifies relevant engagement opportunities
- Optimizes content targeting

## 📈 Performance Optimization

### Best Practices

1. **Redis Configuration**: Use Redis Cluster for high-volume deployments
2. **Agent Specialization**: Configure agents with specific topics and expertise
3. **Load Balancing**: Monitor agent capacity and distribute load evenly
4. **Timing Optimization**: Use historical data to optimize posting times
5. **Content Quality**: Maintain high content quality thresholds

### Scaling Considerations

- **Redis Memory**: Monitor Redis memory usage for large networks
- **Agent Capacity**: Configure appropriate engagement capacity per agent
- **Network Latency**: Consider geographic distribution of agents
- **Rate Limiting**: Respect Twitter API rate limits across all agents

## 🛠️ Development

### Adding Custom Strategies

```typescript
// Custom engagement strategy
const customStrategy = {
  id: 'custom_viral',
  name: 'Custom Viral Strategy',
  conditions: {
    minFollowers: 5000,
    hashtags: ['viral', 'trending'],
  },
  actions: {
    likeDelay: 15000,
    retweetDelay: 45000,
    replyDelay: 90000,
  },
  priority: 8,
  successRate: 0.85,
};

// Register strategy
engagementService.registerCustomStrategy(customStrategy);
```

### Custom Metrics

```typescript
// Track custom metrics
await engagementService.recordCustomMetric({
  name: 'conversion_rate',
  value: 0.15,
  timestamp: Date.now(),
  context: { campaign: 'product_launch' },
});
```

## 🔒 Security

### Network Security

- **Redis Security**: Use Redis AUTH and TLS for production
- **Agent Authentication**: Implement agent authentication tokens
- **Rate Limiting**: Implement proper rate limiting to prevent abuse
- **Content Validation**: Validate all content before engagement

### Privacy Considerations

- **Data Retention**: Configure appropriate data retention policies
- **User Privacy**: Respect user privacy in engagement activities
- **Compliance**: Ensure compliance with relevant regulations

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Errors**
   ```
   Error: Redis connection failed
   Solution: Check Redis URL and ensure Redis is running
   ```

2. **Network Coordination Failures**
   ```
   Error: No agents available for coordination
   Solution: Ensure multiple agents are running and registered
   ```

3. **Engagement Delays**
   ```
   Error: Engagement delays too long
   Solution: Adjust delay settings in configuration
   ```

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=debug
```

### Health Checks

Monitor service health:

```typescript
// Check service health
const health = await runtime.getService('network-coordination').getHealth();
console.log('Service health:', health);
```

## 📄 License

This plugin is part of the ElizaOS project and follows the same license terms.

## 🤝 Contributing

We welcome contributions! Please see the main ElizaOS repository for contribution guidelines.

## 📞 Support

For support and questions:
- Open an issue in the ElizaOS repository
- Join the ElizaOS community discord
- Check the documentation at docs.eliza.ai

---

**Note**: This plugin requires Redis for network coordination. Make sure to have Redis installed and configured before using network coordination features.