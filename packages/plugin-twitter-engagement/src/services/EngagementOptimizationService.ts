import { Service, IAgentRuntime, logger } from '@elizaos/core';
import { z } from 'zod';

interface EngagementMetrics {
    postId: string;
    impressions: number;
    likes: number;
    retweets: number;
    replies: number;
    timestamp: number;
    reach: number;
    engagementRate: number;
}

interface OptimalTiming {
    hourOfDay: number;
    dayOfWeek: number;
    engagementMultiplier: number;
    audienceSize: number;
    competition: number;
}

interface EngagementStrategy {
    id: string;
    name: string;
    description: string;
    conditions: {
        minFollowers?: number;
        maxFollowers?: number;
        timeWindow?: number;
        contentType?: string[];
        hashtags?: string[];
    };
    actions: {
        likeDelay: number;
        retweetDelay: number;
        replyDelay: number;
        quoteTweetDelay: number;
        threadDelay: number;
    };
    priority: number;
    successRate: number;
}

const EngagementMetricsSchema = z.object({
    postId: z.string(),
    impressions: z.number(),
    likes: z.number(),
    retweets: z.number(),
    replies: z.number(),
    timestamp: z.number(),
    reach: z.number(),
    engagementRate: z.number(),
});

export class EngagementOptimizationService extends Service {
    static serviceType = 'engagement-optimization';

    private engagementHistory: EngagementMetrics[] = [];
    private optimalTimings: OptimalTiming[] = [];
    private strategies: EngagementStrategy[] = [];
    private optimizationInterval?: NodeJS.Timeout;

    capabilityDescription = 'Optimizes engagement timing and strategies based on performance analytics';

    constructor(runtime: IAgentRuntime) {
        super(runtime);
        this.initializeDefaultStrategies();
    }

    static async start(runtime: IAgentRuntime): Promise<Service> {
        const service = new EngagementOptimizationService(runtime);
        await service.initialize();
        return service;
    }

    private async initialize(): Promise<void> {
        try {
            await this.loadHistoricalData();
            await this.calculateOptimalTimings();
            this.startOptimizationAnalysis();

            logger.info('✅ Engagement optimization service initialized');
        } catch (error) {
            logger.error('❌ Failed to initialize engagement optimization service:', error);
            throw error;
        }
    }

    private initializeDefaultStrategies(): void {
        this.strategies = [
            {
                id: 'viral_boost',
                name: 'Viral Boost',
                description: 'Aggressive engagement for high-potential viral content',
                conditions: {
                    minFollowers: 1000,
                    timeWindow: 3600000, // 1 hour
                    contentType: ['image', 'video', 'thread'],
                    hashtags: ['trending', 'viral', 'breaking'],
                },
                actions: {
                    likeDelay: 30000,     // 30 seconds
                    retweetDelay: 60000,  // 1 minute
                    replyDelay: 120000,   // 2 minutes
                    quoteTweetDelay: 180000, // 3 minutes
                    threadDelay: 300000,  // 5 minutes
                },
                priority: 9,
                successRate: 0.75,
            },
            {
                id: 'steady_growth',
                name: 'Steady Growth',
                description: 'Consistent engagement for steady audience growth',
                conditions: {
                    minFollowers: 100,
                    maxFollowers: 10000,
                    timeWindow: 7200000, // 2 hours
                },
                actions: {
                    likeDelay: 120000,    // 2 minutes
                    retweetDelay: 300000, // 5 minutes
                    replyDelay: 600000,   // 10 minutes
                    quoteTweetDelay: 900000, // 15 minutes
                    threadDelay: 1200000, // 20 minutes
                },
                priority: 5,
                successRate: 0.65,
            },
            {
                id: 'organic_support',
                name: 'Organic Support',
                description: 'Natural engagement patterns for authentic growth',
                conditions: {
                    maxFollowers: 1000,
                    timeWindow: 14400000, // 4 hours
                },
                actions: {
                    likeDelay: 300000,    // 5 minutes
                    retweetDelay: 900000, // 15 minutes
                    replyDelay: 1800000,  // 30 minutes
                    quoteTweetDelay: 3600000, // 1 hour
                    threadDelay: 7200000, // 2 hours
                },
                priority: 3,
                successRate: 0.55,
            },
            {
                id: 'crisis_response',
                name: 'Crisis Response',
                description: 'Rapid response for trending topics or urgent content',
                conditions: {
                    timeWindow: 900000, // 15 minutes
                    contentType: ['breaking', 'urgent', 'trending'],
                },
                actions: {
                    likeDelay: 15000,     // 15 seconds
                    retweetDelay: 30000,  // 30 seconds
                    replyDelay: 60000,    // 1 minute
                    quoteTweetDelay: 90000, // 1.5 minutes
                    threadDelay: 180000,  // 3 minutes
                },
                priority: 10,
                successRate: 0.80,
            },
        ];
    }

    private async loadHistoricalData(): Promise<void> {
        try {
            // Load engagement metrics from database
            const historicalData = await this.runtime.getMemories({
                tableName: 'engagement_metrics',
                count: 1000,
                unique: false,
            });

            this.engagementHistory = historicalData
                .map(memory => {
                    try {
                        return EngagementMetricsSchema.parse(memory.content);
                    } catch (error) {
                        return null;
                    }
                })
                .filter(Boolean) as EngagementMetrics[];

            logger.info(`📊 Loaded ${this.engagementHistory.length} historical engagement records`);
        } catch (error) {
            logger.error('❌ Failed to load historical engagement data:', error);
            this.engagementHistory = [];
        }
    }

    private async calculateOptimalTimings(): Promise<void> {
        if (this.engagementHistory.length < 100) {
            // Use default timings if insufficient data
            this.optimalTimings = this.getDefaultOptimalTimings();
            return;
        }

        const timingData = new Map<string, { totalEngagement: number; count: number; reach: number }>();

        // Analyze historical data for optimal timing patterns
        for (const metrics of this.engagementHistory) {
            const date = new Date(metrics.timestamp);
            const key = `${date.getDay()}-${date.getHours()}`;

            const existing = timingData.get(key) || { totalEngagement: 0, count: 0, reach: 0 };
            existing.totalEngagement += metrics.engagementRate;
            existing.count++;
            existing.reach += metrics.reach;

            timingData.set(key, existing);
        }

        // Calculate optimal timings
        this.optimalTimings = [];
        for (const [key, data] of timingData.entries()) {
            const [dayOfWeek, hourOfDay] = key.split('-').map(Number);
            const avgEngagement = data.totalEngagement / data.count;
            const avgReach = data.reach / data.count;

            this.optimalTimings.push({
                hourOfDay,
                dayOfWeek,
                engagementMultiplier: avgEngagement,
                audienceSize: avgReach,
                competition: this.calculateCompetitionLevel(hourOfDay, dayOfWeek),
            });
        }

        // Sort by engagement multiplier
        this.optimalTimings.sort((a, b) => b.engagementMultiplier - a.engagementMultiplier);

        logger.info(`🕐 Calculated optimal timings for ${this.optimalTimings.length} time slots`);
    }

    private getDefaultOptimalTimings(): OptimalTiming[] {
        // Default optimal posting times based on general Twitter analytics
        return [
            { hourOfDay: 8, dayOfWeek: 1, engagementMultiplier: 1.2, audienceSize: 1000, competition: 0.7 },
            { hourOfDay: 12, dayOfWeek: 1, engagementMultiplier: 1.4, audienceSize: 1500, competition: 0.8 },
            { hourOfDay: 17, dayOfWeek: 1, engagementMultiplier: 1.3, audienceSize: 1200, competition: 0.9 },
            { hourOfDay: 20, dayOfWeek: 1, engagementMultiplier: 1.1, audienceSize: 800, competition: 0.6 },
            { hourOfDay: 9, dayOfWeek: 2, engagementMultiplier: 1.15, audienceSize: 1100, competition: 0.75 },
            { hourOfDay: 13, dayOfWeek: 2, engagementMultiplier: 1.35, audienceSize: 1400, competition: 0.85 },
            { hourOfDay: 18, dayOfWeek: 2, engagementMultiplier: 1.25, audienceSize: 1300, competition: 0.9 },
            { hourOfDay: 21, dayOfWeek: 2, engagementMultiplier: 1.05, audienceSize: 900, competition: 0.65 },
            // Add more default timings for other days...
        ];
    }

    private calculateCompetitionLevel(hourOfDay: number, dayOfWeek: number): number {
        // Business hours typically have higher competition
        const businessHours = hourOfDay >= 9 && hourOfDay <= 17;
        const weekday = dayOfWeek >= 1 && dayOfWeek <= 5;

        let competition = 0.5; // Base competition

        if (businessHours && weekday) {
            competition += 0.3;
        }

        // Peak hours (lunch time, evening)
        if (hourOfDay === 12 || hourOfDay === 17 || hourOfDay === 20) {
            competition += 0.2;
        }

        return Math.min(competition, 1.0);
    }

    private startOptimizationAnalysis(): void {
        this.optimizationInterval = setInterval(async () => {
            try {
                await this.analyzeRecentPerformance();
                await this.updateStrategies();
                await this.optimizeForCurrentConditions();
            } catch (error) {
                logger.error('❌ Optimization analysis failed:', error);
            }
        }, 1800000); // 30 minutes
    }

    private async analyzeRecentPerformance(): Promise<void> {
        const recentData = this.engagementHistory.filter(
            metrics => Date.now() - metrics.timestamp < 86400000 // Last 24 hours
        );

        if (recentData.length === 0) return;

        // Calculate performance metrics
        const avgEngagementRate = recentData.reduce((sum, m) => sum + m.engagementRate, 0) / recentData.length;
        const avgReach = recentData.reduce((sum, m) => sum + m.reach, 0) / recentData.length;
        const totalEngagements = recentData.reduce((sum, m) => sum + m.likes + m.retweets + m.replies, 0);

        // Update strategy success rates based on recent performance
        await this.updateStrategySuccessRates(recentData);

        logger.info(`📈 Recent performance: ${avgEngagementRate.toFixed(2)}% engagement rate, ${avgReach.toFixed(0)} avg reach`);
    }

    private async updateStrategySuccessRates(recentData: EngagementMetrics[]): Promise<void> {
        // This would analyze which strategies performed best
        // For now, implement basic success rate updates
        for (const strategy of this.strategies) {
            const relevantMetrics = recentData.filter(m => this.isStrategyRelevant(strategy, m));

            if (relevantMetrics.length > 0) {
                const avgPerformance = relevantMetrics.reduce((sum, m) => sum + m.engagementRate, 0) / relevantMetrics.length;

                // Update success rate with exponential moving average
                strategy.successRate = strategy.successRate * 0.8 + (avgPerformance / 100) * 0.2;
                strategy.successRate = Math.min(Math.max(strategy.successRate, 0.1), 0.95);
            }
        }
    }

    private isStrategyRelevant(strategy: EngagementStrategy, metrics: EngagementMetrics): boolean {
        // Simple relevance check - could be enhanced with more sophisticated matching
        const timeWindow = strategy.conditions.timeWindow || 7200000; // 2 hours default
        const timeDiff = Date.now() - metrics.timestamp;

        return timeDiff <= timeWindow;
    }

    private async updateStrategies(): Promise<void> {
        // Sort strategies by success rate and priority
        this.strategies.sort((a, b) => {
            const aScore = a.successRate * 0.7 + (a.priority / 10) * 0.3;
            const bScore = b.successRate * 0.7 + (b.priority / 10) * 0.3;
            return bScore - aScore;
        });

        // Remove underperforming strategies
        this.strategies = this.strategies.filter(s => s.successRate > 0.3);

        logger.info(`🔄 Updated ${this.strategies.length} engagement strategies`);
    }

    private async optimizeForCurrentConditions(): Promise<void> {
        const currentHour = new Date().getHours();
        const currentDay = new Date().getDay();

        // Find optimal timing for current conditions
        const currentTiming = this.optimalTimings.find(
            t => t.hourOfDay === currentHour && t.dayOfWeek === currentDay
        );

        if (currentTiming) {
            // Adjust strategy timings based on current conditions
            for (const strategy of this.strategies) {
                const multiplier = currentTiming.engagementMultiplier;

                // Reduce delays during high-engagement periods
                if (multiplier > 1.2) {
                    strategy.actions.likeDelay = Math.max(strategy.actions.likeDelay * 0.8, 15000);
                    strategy.actions.retweetDelay = Math.max(strategy.actions.retweetDelay * 0.8, 30000);
                    strategy.actions.replyDelay = Math.max(strategy.actions.replyDelay * 0.8, 60000);
                }

                // Increase delays during low-engagement periods
                if (multiplier < 0.8) {
                    strategy.actions.likeDelay = Math.min(strategy.actions.likeDelay * 1.2, 600000);
                    strategy.actions.retweetDelay = Math.min(strategy.actions.retweetDelay * 1.2, 900000);
                    strategy.actions.replyDelay = Math.min(strategy.actions.replyDelay * 1.2, 1800000);
                }
            }
        }
    }

    // Public methods for other services to use
    public getOptimalEngagementStrategy(context: {
        contentType?: string;
        hashtags?: string[];
        followerCount?: number;
        urgency?: 'low' | 'medium' | 'high';
        timeWindow?: number;
    }): EngagementStrategy | null {
        // Find best matching strategy
        const candidates = this.strategies.filter(strategy => {
            const conditions = strategy.conditions;

            // Check follower count
            if (conditions.minFollowers && context.followerCount && context.followerCount < conditions.minFollowers) {
                return false;
            }
            if (conditions.maxFollowers && context.followerCount && context.followerCount > conditions.maxFollowers) {
                return false;
            }

            // Check content type
            if (conditions.contentType && context.contentType && !conditions.contentType.includes(context.contentType)) {
                return false;
            }

            // Check hashtags
            if (conditions.hashtags && context.hashtags) {
                const hasMatchingHashtag = conditions.hashtags.some(tag =>
                    context.hashtags!.some(userTag => userTag.toLowerCase().includes(tag.toLowerCase()))
                );
                if (!hasMatchingHashtag) return false;
            }

            // Check time window
            if (conditions.timeWindow && context.timeWindow && context.timeWindow > conditions.timeWindow) {
                return false;
            }

            return true;
        });

        if (candidates.length === 0) return null;

        // Return best strategy based on success rate and priority
        return candidates.reduce((best, current) => {
            const bestScore = best.successRate * 0.7 + (best.priority / 10) * 0.3;
            const currentScore = current.successRate * 0.7 + (current.priority / 10) * 0.3;
            return currentScore > bestScore ? current : best;
        });
    }

    public getOptimalPostingTime(
        lookAheadHours: number = 24,
        contentType?: string
    ): { timestamp: number; score: number } | null {
        const now = new Date();
        const bestTimes: { timestamp: number; score: number }[] = [];

        for (let i = 0; i < lookAheadHours; i++) {
            const futureTime = new Date(now.getTime() + i * 3600000); // Add i hours
            const timing = this.optimalTimings.find(
                t => t.hourOfDay === futureTime.getHours() && t.dayOfWeek === futureTime.getDay()
            );

            if (timing) {
                let score = timing.engagementMultiplier;

                // Reduce score based on competition
                score *= (1 - timing.competition * 0.3);

                // Boost score for certain content types during optimal times
                if (contentType === 'breaking' && timing.hourOfDay >= 8 && timing.hourOfDay <= 18) {
                    score *= 1.2;
                }

                bestTimes.push({
                    timestamp: futureTime.getTime(),
                    score,
                });
            }
        }

        if (bestTimes.length === 0) return null;

        // Return the best time
        return bestTimes.reduce((best, current) => current.score > best.score ? current : best);
    }

    public async recordEngagementMetrics(metrics: EngagementMetrics): Promise<void> {
        try {
            // Validate metrics
            const validatedMetrics = EngagementMetricsSchema.parse(metrics);

            // Add to history
            this.engagementHistory.push(validatedMetrics);

            // Keep only recent data in memory (last 30 days)
            const thirtyDaysAgo = Date.now() - 30 * 24 * 60 * 60 * 1000;
            this.engagementHistory = this.engagementHistory.filter(m => m.timestamp > thirtyDaysAgo);

            // Store in database
            await this.runtime.createMemory({
                entityId: this.runtime.agentId,
                content: validatedMetrics,
                roomId: this.runtime.agentId, // Use agent ID as room for metrics
                agentId: this.runtime.agentId,
                metadata: {
                    type: 'engagement_metrics',
                    timestamp: metrics.timestamp,
                },
            }, 'engagement_metrics');

            logger.info(`📊 Recorded engagement metrics for post ${metrics.postId}`);
        } catch (error) {
            logger.error('❌ Failed to record engagement metrics:', error);
        }
    }

    public calculateEngagementScore(metrics: EngagementMetrics): number {
        const weights = {
            likes: 0.3,
            retweets: 0.4,
            replies: 0.3,
        };

        const totalEngagements = metrics.likes + metrics.retweets + metrics.replies;
        const weightedScore = (
            metrics.likes * weights.likes +
            metrics.retweets * weights.retweets +
            metrics.replies * weights.replies
        ) / totalEngagements;

        // Normalize by reach
        const normalizedScore = (totalEngagements / Math.max(metrics.reach, 1)) * 100;

        return Math.min(normalizedScore * weightedScore, 100);
    }

    public getEngagementInsights(): {
        totalEngagements: number;
        avgEngagementRate: number;
        bestPerformingTimes: OptimalTiming[];
        topStrategies: EngagementStrategy[];
        recommendations: string[];
    } {
        const totalEngagements = this.engagementHistory.reduce(
            (sum, m) => sum + m.likes + m.retweets + m.replies, 0
        );

        const avgEngagementRate = this.engagementHistory.length > 0 ?
            this.engagementHistory.reduce((sum, m) => sum + m.engagementRate, 0) / this.engagementHistory.length :
            0;

        const bestPerformingTimes = this.optimalTimings.slice(0, 5);
        const topStrategies = this.strategies.slice(0, 3);

        const recommendations = this.generateRecommendations();

        return {
            totalEngagements,
            avgEngagementRate,
            bestPerformingTimes,
            topStrategies,
            recommendations,
        };
    }

    private generateRecommendations(): string[] {
        const recommendations: string[] = [];

        if (this.engagementHistory.length > 0) {
            const recentAvg = this.engagementHistory.slice(-10).reduce((sum, m) => sum + m.engagementRate, 0) / 10;
            const overallAvg = this.engagementHistory.reduce((sum, m) => sum + m.engagementRate, 0) / this.engagementHistory.length;

            if (recentAvg < overallAvg * 0.8) {
                recommendations.push('Recent engagement is declining. Consider adjusting posting times or content strategy.');
            }

            if (this.optimalTimings.length > 0) {
                const bestTime = this.optimalTimings[0];
                recommendations.push(`Best engagement time: ${bestTime.hourOfDay}:00 on ${this.getDayName(bestTime.dayOfWeek)}`);
            }
        }

        if (this.strategies.length > 0) {
            const bestStrategy = this.strategies[0];
            recommendations.push(`Top performing strategy: ${bestStrategy.name} (${(bestStrategy.successRate * 100).toFixed(1)}% success rate)`);
        }

        return recommendations;
    }

    private getDayName(dayOfWeek: number): string {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return days[dayOfWeek] || 'Unknown';
    }

    async stop(): Promise<void> {
        if (this.optimizationInterval) {
            clearInterval(this.optimizationInterval);
        }

        logger.info('🛑 Engagement optimization service stopped');
    }
}