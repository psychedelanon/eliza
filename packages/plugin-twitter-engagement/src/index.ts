import { Plugin } from '@elizaos/core';
import { NetworkCoordinationService } from './services/NetworkCoordinationService';
import { EngagementOptimizationService } from './services/EngagementOptimizationService';
import { TrendAnalysisService } from './services/TrendAnalysisService';
import { CrossAmplificationService } from './services/CrossAmplificationService';
import { PerformanceMonitoringService } from './services/PerformanceMonitoringService';
import { SmartTimingService } from './services/SmartTimingService';
import { ContentStrategyService } from './services/ContentStrategyService';
import { NetworkAnalyticsService } from './services/NetworkAnalyticsService';

// Actions
import { amplifyPostAction } from './actions/amplifyPost';
import { coordinatedEngagementAction } from './actions/coordinatedEngagement';
import { strategicPostAction } from './actions/strategicPost';
import { networkReplyAction } from './actions/networkReply';

// Providers
import { trendingTopicsProvider } from './providers/trendingTopics';
import { networkMetricsProvider } from './providers/networkMetrics';
import { engagementOpportunitiesProvider } from './providers/engagementOpportunities';
import { optimalTimingProvider } from './providers/optimalTiming';

// Evaluators
import { engagementQualityEvaluator } from './evaluators/engagementQuality';
import { networkCoordinationEvaluator } from './evaluators/networkCoordination';
import { contentRelevanceEvaluator } from './evaluators/contentRelevance';

export const twitterEngagementPlugin: Plugin = {
    name: '@elizaos/plugin-twitter-engagement',
    description: 'Advanced Twitter engagement optimization with network coordination capabilities',

    services: [
        NetworkCoordinationService,
        EngagementOptimizationService,
        TrendAnalysisService,
        CrossAmplificationService,
        PerformanceMonitoringService,
        SmartTimingService,
        ContentStrategyService,
        NetworkAnalyticsService,
    ],

    actions: [
        amplifyPostAction,
        coordinatedEngagementAction,
        strategicPostAction,
        networkReplyAction,
    ],

    providers: [
        trendingTopicsProvider,
        networkMetricsProvider,
        engagementOpportunitiesProvider,
        optimalTimingProvider,
    ],

    evaluators: [
        engagementQualityEvaluator,
        networkCoordinationEvaluator,
        contentRelevanceEvaluator,
    ],

    config: {
        // Redis connection for network coordination
        REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379',

        // Network coordination settings
        NETWORK_COORDINATION_ENABLED: process.env.NETWORK_COORDINATION_ENABLED === 'true',
        MAX_NETWORK_AGENTS: parseInt(process.env.MAX_NETWORK_AGENTS || '10'),
        COORDINATION_WINDOW_MS: parseInt(process.env.COORDINATION_WINDOW_MS || '300000'), // 5 minutes

        // Engagement optimization settings
        ENGAGEMENT_DELAY_MIN_MS: parseInt(process.env.ENGAGEMENT_DELAY_MIN_MS || '30000'), // 30 seconds
        ENGAGEMENT_DELAY_MAX_MS: parseInt(process.env.ENGAGEMENT_DELAY_MAX_MS || '300000'), // 5 minutes
        AMPLIFICATION_PROBABILITY: parseFloat(process.env.AMPLIFICATION_PROBABILITY || '0.7'),

        // Content strategy settings
        TRENDING_TOPICS_REFRESH_MS: parseInt(process.env.TRENDING_TOPICS_REFRESH_MS || '600000'), // 10 minutes
        CONTENT_QUALITY_THRESHOLD: parseFloat(process.env.CONTENT_QUALITY_THRESHOLD || '0.7'),

        // Performance monitoring
        METRICS_RETENTION_HOURS: parseInt(process.env.METRICS_RETENTION_HOURS || '168'), // 7 days
        ANALYTICS_BATCH_SIZE: parseInt(process.env.ANALYTICS_BATCH_SIZE || '100'),

        // Smart timing
        OPTIMAL_POSTING_HOURS: process.env.OPTIMAL_POSTING_HOURS || '8,12,17,20', // UTC hours
        TIMEZONE_OFFSET: parseInt(process.env.TIMEZONE_OFFSET || '0'),

        // Network analytics
        INFLUENCE_SCORE_WEIGHT: parseFloat(process.env.INFLUENCE_SCORE_WEIGHT || '0.3'),
        ENGAGEMENT_RATE_WEIGHT: parseFloat(process.env.ENGAGEMENT_RATE_WEIGHT || '0.4'),
        REACH_WEIGHT: parseFloat(process.env.REACH_WEIGHT || '0.3'),
    },

    async init(config: Record<string, any>) {
        console.log('🚀 Twitter Engagement Plugin initialized with network coordination');
        console.log(`Network coordination: ${config.NETWORK_COORDINATION_ENABLED ? 'ENABLED' : 'DISABLED'}`);
        console.log(`Max network agents: ${config.MAX_NETWORK_AGENTS}`);
        console.log(`Coordination window: ${config.COORDINATION_WINDOW_MS}ms`);
    },
};

export default twitterEngagementPlugin;

// Re-export key components for direct import
export {
    NetworkCoordinationService,
    EngagementOptimizationService,
    TrendAnalysisService,
    CrossAmplificationService,
    PerformanceMonitoringService,
    SmartTimingService,
    ContentStrategyService,
    NetworkAnalyticsService,

    amplifyPostAction,
    coordinatedEngagementAction,
    strategicPostAction,
    networkReplyAction,

    trendingTopicsProvider,
    networkMetricsProvider,
    engagementOpportunitiesProvider,
    optimalTimingProvider,

    engagementQualityEvaluator,
    networkCoordinationEvaluator,
    contentRelevanceEvaluator,
};