import { Service, IAgentRuntime, logger } from '@elizaos/core';
import Redis from 'ioredis';
import { z } from 'zod';

// Types for network coordination
interface NetworkAgent {
    id: string;
    name: string;
    lastSeen: number;
    persona: string;
    engagementCapacity: number;
    currentLoad: number;
    specializations: string[];
}

interface CoordinationEvent {
    id: string;
    type: 'post_created' | 'engagement_request' | 'trend_detected' | 'amplification_needed';
    sourceAgentId: string;
    payload: any;
    timestamp: number;
    priority: number;
    targetAgents?: string[];
}

interface EngagementPlan {
    eventId: string;
    assignments: {
        agentId: string;
        action: 'like' | 'retweet' | 'reply' | 'quote' | 'thread';
        delay: number;
        content?: string;
    }[];
    totalEngagementTarget: number;
    timeWindow: number;
}

const NetworkAgentSchema = z.object({
    id: z.string(),
    name: z.string(),
    lastSeen: z.number(),
    persona: z.string(),
    engagementCapacity: z.number(),
    currentLoad: z.number(),
    specializations: z.array(z.string()),
});

const CoordinationEventSchema = z.object({
    id: z.string(),
    type: z.enum(['post_created', 'engagement_request', 'trend_detected', 'amplification_needed']),
    sourceAgentId: z.string(),
    payload: z.any(),
    timestamp: z.number(),
    priority: z.number(),
    targetAgents: z.array(z.string()).optional(),
});

export class NetworkCoordinationService extends Service {
    static serviceType = 'network-coordination';

    private redis: Redis;
    private networkAgents = new Map<string, NetworkAgent>();
    private coordinationEvents = new Map<string, CoordinationEvent>();
    private heartbeatInterval?: NodeJS.Timeout;
    private coordinationInterval?: NodeJS.Timeout;

    capabilityDescription = 'Coordinates engagement activities across multiple Twitter agents in the network';

    constructor(runtime: IAgentRuntime) {
        super(runtime);

        const redisUrl = runtime.getSetting('REDIS_URL') || 'redis://localhost:6379';
        this.redis = new Redis(redisUrl);

        this.setupEventHandlers();
    }

    static async start(runtime: IAgentRuntime): Promise<Service> {
        const service = new NetworkCoordinationService(runtime);
        await service.initialize();
        return service;
    }

    private async initialize(): Promise<void> {
        try {
            await this.redis.ping();
            logger.info('✅ Network coordination service connected to Redis');

            // Register this agent in the network
            await this.registerAgent();

            // Start heartbeat to maintain presence
            this.startHeartbeat();

            // Start coordination processing
            this.startCoordinationProcessing();

            logger.info('🚀 Network coordination service initialized');
        } catch (error) {
            logger.error('❌ Failed to initialize network coordination service:', error);
            throw error;
        }
    }

    private async registerAgent(): Promise<void> {
        const agentData: NetworkAgent = {
            id: this.runtime.agentId,
            name: this.runtime.character.name,
            lastSeen: Date.now(),
            persona: this.runtime.character.bio?.[0] || 'default',
            engagementCapacity: 100, // Configurable based on agent capabilities
            currentLoad: 0,
            specializations: this.runtime.character.topics || [],
        };

        this.networkAgents.set(this.runtime.agentId, agentData);

        // Store in Redis for network-wide visibility
        await this.redis.hset(
            'network:agents',
            this.runtime.agentId,
            JSON.stringify(agentData)
        );

        logger.info(`🔗 Agent ${agentData.name} registered in network`);
    }

    private startHeartbeat(): void {
        this.heartbeatInterval = setInterval(async () => {
            try {
                const agent = this.networkAgents.get(this.runtime.agentId);
                if (agent) {
                    agent.lastSeen = Date.now();
                    await this.redis.hset(
                        'network:agents',
                        this.runtime.agentId,
                        JSON.stringify(agent)
                    );
                }
            } catch (error) {
                logger.error('❌ Heartbeat failed:', error);
            }
        }, 30000); // 30 seconds
    }

    private startCoordinationProcessing(): void {
        this.coordinationInterval = setInterval(async () => {
            try {
                await this.processCoordinationEvents();
                await this.cleanupStaleAgents();
            } catch (error) {
                logger.error('❌ Coordination processing failed:', error);
            }
        }, 10000); // 10 seconds
    }

    private async processCoordinationEvents(): Promise<void> {
        // Get pending events from Redis
        const events = await this.redis.lrange('coordination:events', 0, -1);

        for (const eventStr of events) {
            try {
                const event = JSON.parse(eventStr) as CoordinationEvent;

                // Skip if event is too old
                if (Date.now() - event.timestamp > 300000) { // 5 minutes
                    await this.redis.lrem('coordination:events', 1, eventStr);
                    continue;
                }

                await this.handleCoordinationEvent(event);

                // Remove processed event
                await this.redis.lrem('coordination:events', 1, eventStr);
            } catch (error) {
                logger.error('❌ Failed to process coordination event:', error);
            }
        }
    }

    private async handleCoordinationEvent(event: CoordinationEvent): Promise<void> {
        logger.info(`📡 Processing coordination event: ${event.type} from ${event.sourceAgentId}`);

        switch (event.type) {
            case 'post_created':
                await this.handlePostCreated(event);
                break;
            case 'engagement_request':
                await this.handleEngagementRequest(event);
                break;
            case 'trend_detected':
                await this.handleTrendDetected(event);
                break;
            case 'amplification_needed':
                await this.handleAmplificationNeeded(event);
                break;
        }
    }

    private async handlePostCreated(event: CoordinationEvent): Promise<void> {
        const { postId, content, hashtags, isHighPriority } = event.payload;

        // Get available agents for engagement
        const availableAgents = await this.getAvailableAgents();

        // Create engagement plan
        const engagementPlan = await this.createEngagementPlan(
            event.id,
            availableAgents,
            {
                postId,
                content,
                hashtags,
                priority: isHighPriority ? 'high' : 'medium',
                targetEngagements: Math.min(5, availableAgents.length),
            }
        );

        // Execute engagement plan
        await this.executeEngagementPlan(engagementPlan);
    }

    private async handleEngagementRequest(event: CoordinationEvent): Promise<void> {
        const { targetPostId, engagementType, urgency } = event.payload;

        // Check if this agent should respond
        if (await this.shouldEngageWithPost(targetPostId, engagementType)) {
            const delay = this.calculateEngagementDelay(urgency);

            // Schedule engagement
            setTimeout(async () => {
                await this.executeEngagement(targetPostId, engagementType);
            }, delay);
        }
    }

    private async handleTrendDetected(event: CoordinationEvent): Promise<void> {
        const { trend, momentum, relevanceScore } = event.payload;

        // Check if this agent should participate in trend
        if (relevanceScore > 0.7 && this.isRelevantToAgent(trend)) {
            await this.scheduleContentForTrend(trend, momentum);
        }
    }

    private async handleAmplificationNeeded(event: CoordinationEvent): Promise<void> {
        const { targetPostId, amplificationLevel, timeWindow } = event.payload;

        // Coordinate amplification efforts
        await this.coordinateAmplification(targetPostId, amplificationLevel, timeWindow);
    }

    private async getAvailableAgents(): Promise<NetworkAgent[]> {
        const agentData = await this.redis.hgetall('network:agents');
        const availableAgents: NetworkAgent[] = [];

        for (const [agentId, agentDataStr] of Object.entries(agentData)) {
            try {
                const agent = JSON.parse(agentDataStr) as NetworkAgent;

                // Check if agent is still active (within last 2 minutes)
                if (Date.now() - agent.lastSeen < 120000 && agent.currentLoad < agent.engagementCapacity) {
                    availableAgents.push(agent);
                }
            } catch (error) {
                logger.error(`❌ Failed to parse agent data for ${agentId}:`, error);
            }
        }

        return availableAgents;
    }

    private async createEngagementPlan(
        eventId: string,
        availableAgents: NetworkAgent[],
        options: {
            postId: string;
            content: string;
            hashtags: string[];
            priority: 'high' | 'medium' | 'low';
            targetEngagements: number;
        }
    ): Promise<EngagementPlan> {
        const plan: EngagementPlan = {
            eventId,
            assignments: [],
            totalEngagementTarget: options.targetEngagements,
            timeWindow: 300000, // 5 minutes
        };

        // Sort agents by relevance and capacity
        const sortedAgents = availableAgents
            .filter(agent => agent.id !== this.runtime.agentId) // Exclude self
            .sort((a, b) => {
                const aRelevance = this.calculateAgentRelevance(a, options.content, options.hashtags);
                const bRelevance = this.calculateAgentRelevance(b, options.content, options.hashtags);
                return bRelevance - aRelevance;
            });

        // Assign engagement actions
        const engagementTypes = ['like', 'retweet', 'reply', 'quote'] as const;
        const selectedAgents = sortedAgents.slice(0, options.targetEngagements);

        for (let i = 0; i < selectedAgents.length; i++) {
            const agent = selectedAgents[i];
            const engagementType = engagementTypes[i % engagementTypes.length];
            const delay = this.calculateStaggeredDelay(i, options.priority);

            plan.assignments.push({
                agentId: agent.id,
                action: engagementType,
                delay,
                content: engagementType === 'reply' ? await this.generateReplyContent(options.content, agent.persona) : undefined,
            });
        }

        return plan;
    }

    private calculateAgentRelevance(agent: NetworkAgent, content: string, hashtags: string[]): number {
        let relevance = 0;

        // Check specialization overlap
        for (const specialization of agent.specializations) {
            if (content.toLowerCase().includes(specialization.toLowerCase()) ||
                hashtags.some(tag => tag.toLowerCase().includes(specialization.toLowerCase()))) {
                relevance += 0.3;
            }
        }

        // Factor in current load (prefer less loaded agents)
        relevance += (1 - agent.currentLoad / agent.engagementCapacity) * 0.4;

        // Add persona matching bonus
        relevance += this.calculatePersonaMatch(agent.persona, content) * 0.3;

        return Math.min(relevance, 1.0);
    }

    private calculatePersonaMatch(persona: string, content: string): number {
        // Simple keyword matching - could be enhanced with ML
        const contentLower = content.toLowerCase();
        const personaLower = persona.toLowerCase();

        if (contentLower.includes(personaLower)) return 1.0;

        // Add specific persona matching logic
        const personaKeywords = {
            'crypto': ['bitcoin', 'ethereum', 'defi', 'nft', 'blockchain'],
            'tech': ['ai', 'ml', 'development', 'coding', 'software'],
            'finance': ['trading', 'investment', 'market', 'price'],
            'meme': ['meme', 'funny', 'lol', 'joke'],
        };

        for (const [type, keywords] of Object.entries(personaKeywords)) {
            if (personaLower.includes(type)) {
                const matches = keywords.filter(keyword => contentLower.includes(keyword)).length;
                return Math.min(matches * 0.2, 1.0);
            }
        }

        return 0.1; // Base relevance
    }

    private calculateStaggeredDelay(index: number, priority: 'high' | 'medium' | 'low'): number {
        const baseDelay = {
            high: 10000,    // 10 seconds
            medium: 30000,  // 30 seconds
            low: 60000,     // 1 minute
        }[priority];

        const staggerMultiplier = 1 + (index * 0.5); // Stagger by 50% per agent
        return baseDelay * staggerMultiplier;
    }

    private async generateReplyContent(originalContent: string, persona: string): Promise<string> {
        // Use the agent's text generation model to create contextual replies
        try {
            const prompt = `Generate a brief, engaging reply to this tweet from a ${persona} perspective:\n\n"${originalContent}"\n\nReply:`;

            const response = await this.runtime.useModel('TEXT_SMALL', {
                prompt,
                temperature: 0.8,
                maxTokens: 100,
            });

            return response.length > 200 ? response.substring(0, 200) + '...' : response;
        } catch (error) {
            logger.error('❌ Failed to generate reply content:', error);
            return `Interesting perspective! 🤔`;
        }
    }

    private async executeEngagementPlan(plan: EngagementPlan): Promise<void> {
        logger.info(`🎯 Executing engagement plan for event ${plan.eventId} with ${plan.assignments.length} assignments`);

        for (const assignment of plan.assignments) {
            // Send engagement request to specific agent
            await this.sendEngagementRequest(assignment.agentId, assignment);
        }
    }

    private async sendEngagementRequest(
        targetAgentId: string,
        assignment: EngagementPlan['assignments'][0]
    ): Promise<void> {
        const request = {
            type: 'engagement_request',
            targetAgentId,
            assignment,
            timestamp: Date.now(),
        };

        await this.redis.lpush(`agent:${targetAgentId}:requests`, JSON.stringify(request));
    }

    private async shouldEngageWithPost(postId: string, engagementType: string): Promise<boolean> {
        // Check if we've already engaged with this post
        const engagementKey = `engagement:${this.runtime.agentId}:${postId}`;
        const hasEngaged = await this.redis.get(engagementKey);

        if (hasEngaged) return false;

        // Check current load
        const agent = this.networkAgents.get(this.runtime.agentId);
        if (agent && agent.currentLoad >= agent.engagementCapacity) {
            return false;
        }

        // Mark as engaged to prevent duplicate engagements
        await this.redis.setex(engagementKey, 3600, engagementType); // 1 hour

        return true;
    }

    private calculateEngagementDelay(urgency: 'high' | 'medium' | 'low'): number {
        const delays = {
            high: 5000 + Math.random() * 15000,    // 5-20 seconds
            medium: 30000 + Math.random() * 60000,  // 30-90 seconds
            low: 60000 + Math.random() * 120000,   // 1-3 minutes
        };

        return delays[urgency] || delays.medium;
    }

    private async executeEngagement(postId: string, engagementType: string): Promise<void> {
        // This would call the appropriate Twitter action
        logger.info(`📱 Executing ${engagementType} engagement on post ${postId}`);

        // Update agent load
        const agent = this.networkAgents.get(this.runtime.agentId);
        if (agent) {
            agent.currentLoad = Math.min(agent.currentLoad + 10, agent.engagementCapacity);
            await this.redis.hset('network:agents', this.runtime.agentId, JSON.stringify(agent));
        }
    }

    private isRelevantToAgent(trend: string): boolean {
        const agentTopics = this.runtime.character.topics || [];
        const trendLower = trend.toLowerCase();

        return agentTopics.some(topic =>
            trendLower.includes(topic.toLowerCase()) ||
            topic.toLowerCase().includes(trendLower)
        );
    }

    private async scheduleContentForTrend(trend: string, momentum: number): Promise<void> {
        logger.info(`📈 Scheduling content for trend: ${trend} (momentum: ${momentum})`);

        // Schedule content creation task
        await this.runtime.createTask({
            name: 'TREND_CONTENT_CREATION',
            description: `Create content for trending topic: ${trend}`,
            tags: ['trend', 'content', 'high-priority'],
            metadata: {
                trend,
                momentum,
                scheduledAt: Date.now(),
            },
        });
    }

    private async coordinateAmplification(
        postId: string,
        amplificationLevel: number,
        timeWindow: number
    ): Promise<void> {
        const availableAgents = await this.getAvailableAgents();
        const targetAgents = Math.min(amplificationLevel, availableAgents.length);

        logger.info(`📢 Coordinating amplification of post ${postId} with ${targetAgents} agents`);

        // Create amplification event
        const amplificationEvent: CoordinationEvent = {
            id: `amp_${postId}_${Date.now()}`,
            type: 'amplification_needed',
            sourceAgentId: this.runtime.agentId,
            payload: {
                postId,
                amplificationLevel,
                timeWindow,
            },
            timestamp: Date.now(),
            priority: 8,
        };

        await this.redis.lpush('coordination:events', JSON.stringify(amplificationEvent));
    }

    private async cleanupStaleAgents(): Promise<void> {
        const agentData = await this.redis.hgetall('network:agents');
        const staleThreshold = Date.now() - 300000; // 5 minutes

        for (const [agentId, agentDataStr] of Object.entries(agentData)) {
            try {
                const agent = JSON.parse(agentDataStr) as NetworkAgent;

                if (agent.lastSeen < staleThreshold) {
                    await this.redis.hdel('network:agents', agentId);
                    logger.info(`🧹 Removed stale agent: ${agent.name}`);
                }
            } catch (error) {
                // Remove corrupted agent data
                await this.redis.hdel('network:agents', agentId);
            }
        }
    }

    // Public methods for other services to use
    public async announcePost(postId: string, content: string, hashtags: string[] = []): Promise<void> {
        const event: CoordinationEvent = {
            id: `post_${postId}_${Date.now()}`,
            type: 'post_created',
            sourceAgentId: this.runtime.agentId,
            payload: {
                postId,
                content,
                hashtags,
                isHighPriority: hashtags.some(tag => tag.toLowerCase().includes('breaking')),
            },
            timestamp: Date.now(),
            priority: 5,
        };

        await this.redis.lpush('coordination:events', JSON.stringify(event));
        logger.info(`📢 Announced new post ${postId} to network`);
    }

    public async requestEngagement(
        postId: string,
        engagementType: 'like' | 'retweet' | 'reply' | 'quote',
        urgency: 'high' | 'medium' | 'low' = 'medium'
    ): Promise<void> {
        const event: CoordinationEvent = {
            id: `engagement_${postId}_${Date.now()}`,
            type: 'engagement_request',
            sourceAgentId: this.runtime.agentId,
            payload: {
                targetPostId: postId,
                engagementType,
                urgency,
            },
            timestamp: Date.now(),
            priority: urgency === 'high' ? 9 : urgency === 'medium' ? 5 : 2,
        };

        await this.redis.lpush('coordination:events', JSON.stringify(event));
    }

    public async getNetworkStatus(): Promise<{
        activeAgents: number;
        totalCapacity: number;
        currentLoad: number;
        pendingEvents: number;
    }> {
        const agentData = await this.redis.hgetall('network:agents');
        const pendingEvents = await this.redis.llen('coordination:events');

        let activeAgents = 0;
        let totalCapacity = 0;
        let currentLoad = 0;

        for (const agentDataStr of Object.values(agentData)) {
            try {
                const agent = JSON.parse(agentDataStr) as NetworkAgent;
                if (Date.now() - agent.lastSeen < 120000) { // Active in last 2 minutes
                    activeAgents++;
                    totalCapacity += agent.engagementCapacity;
                    currentLoad += agent.currentLoad;
                }
            } catch (error) {
                // Skip corrupted data
            }
        }

        return {
            activeAgents,
            totalCapacity,
            currentLoad,
            pendingEvents,
        };
    }

    private setupEventHandlers(): void {
        // Register event handlers for agent communication
        this.runtime.registerEvent('POST_CREATED', async (params: any) => {
            await this.announcePost(params.postId, params.content, params.hashtags);
        });

        this.runtime.registerEvent('ENGAGEMENT_NEEDED', async (params: any) => {
            await this.requestEngagement(params.postId, params.engagementType, params.urgency);
        });
    }

    async stop(): Promise<void> {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }

        if (this.coordinationInterval) {
            clearInterval(this.coordinationInterval);
        }

        // Remove agent from network
        await this.redis.hdel('network:agents', this.runtime.agentId);

        // Close Redis connection
        await this.redis.quit();

        logger.info('🛑 Network coordination service stopped');
    }
}