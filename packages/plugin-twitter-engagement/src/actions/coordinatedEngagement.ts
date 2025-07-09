import { Action, IAgentRuntime, Memory, State, logger } from '@elizaos/core';
import { z } from 'zod';

const CoordinatedEngagementSchema = z.object({
    targetPostId: z.string(),
    engagementType: z.enum(['like', 'retweet', 'reply', 'quote', 'thread']),
    urgency: z.enum(['low', 'medium', 'high']).default('medium'),
    targetAgents: z.array(z.string()).optional(),
    timeWindow: z.number().optional(),
    content: z.string().optional(),
    hashtags: z.array(z.string()).optional(),
    networkBoost: z.boolean().default(false),
});

export const coordinatedEngagementAction: Action = {
    name: 'COORDINATED_ENGAGEMENT',
    similes: [
        'coordinate engagement',
        'network engagement',
        'amplify post',
        'boost engagement',
        'synchronize likes',
        'orchestrate retweets',
        'coordinate replies',
        'network amplification',
    ],
    description: 'Coordinates engagement across multiple agents in the network for maximum impact',

    examples: [
        [
            {
                name: 'user',
                content: {
                    text: 'We need to boost engagement on this trending post about AI. Let the network coordinate likes and retweets.',
                },
            },
            {
                name: 'assistant',
                content: {
                    text: 'Coordinating network engagement for the AI post. I\'ll orchestrate likes, retweets, and replies across available agents with optimal timing.',
                    thought: 'This is a high-potential post about AI that could benefit from coordinated network engagement. I should trigger the network coordination service to organize likes and retweets from other agents.',
                },
            },
        ],
        [
            {
                name: 'user',
                content: {
                    text: 'This breaking news about crypto regulation needs immediate network amplification.',
                },
            },
            {
                name: 'assistant',
                content: {
                    text: 'Initiating high-urgency network amplification for the crypto regulation news. Coordinating immediate engagement across all available agents.',
                    thought: 'Breaking news requires rapid response. I should set this to high urgency and coordinate immediate likes and retweets from the network.',
                },
            },
        ],
    ],

    validate: async (runtime: IAgentRuntime, message: Memory, state?: State) => {
        try {
            // Check if network coordination is enabled
            const networkCoordinationEnabled = runtime.getSetting('NETWORK_COORDINATION_ENABLED');
            if (!networkCoordinationEnabled) {
                return false;
            }

            // Check if we have access to the network coordination service
            const networkService = runtime.getService('network-coordination');
            if (!networkService) {
                return false;
            }

            // Parse the message to see if it contains engagement coordination requests
            const content = message.content.text?.toLowerCase() || '';

            const coordinationKeywords = [
                'coordinate', 'network', 'amplify', 'boost', 'synchronize',
                'orchestrate', 'engagement', 'likes', 'retweets', 'replies',
                'amplification', 'viral', 'trending', 'breaking',
            ];

            const hasCoordinationKeyword = coordinationKeywords.some(keyword =>
                content.includes(keyword)
            );

            if (!hasCoordinationKeyword) {
                return false;
            }

            // Check if there's a specific post ID or URL mentioned
            const hasPostReference = content.includes('post') ||
                content.includes('tweet') ||
                content.includes('twitter.com') ||
                content.includes('x.com') ||
                message.content.url;

            return hasPostReference;
        } catch (error) {
            logger.error('❌ Failed to validate coordinated engagement action:', error);
            return false;
        }
    },

    handler: async (runtime: IAgentRuntime, message: Memory, state?: State) => {
        try {
            logger.info('🎯 Executing coordinated engagement action');

            // Get the network coordination service
            const networkService = runtime.getService('network-coordination');
            if (!networkService) {
                throw new Error('Network coordination service not available');
            }

            // Get the engagement optimization service
            const engagementService = runtime.getService('engagement-optimization');

            // Extract engagement details from message
            const engagementDetails = await extractEngagementDetails(runtime, message);

            // Validate engagement details
            const validatedDetails = CoordinatedEngagementSchema.parse(engagementDetails);

            // Get optimal engagement strategy
            let engagementStrategy = null;
            if (engagementService) {
                engagementStrategy = engagementService.getOptimalEngagementStrategy({
                    contentType: message.content.attachments?.[0]?.contentType || 'text',
                    hashtags: validatedDetails.hashtags,
                    urgency: validatedDetails.urgency,
                    timeWindow: validatedDetails.timeWindow,
                });
            }

            // Create coordination event
            const coordinationEvent = {
                type: 'coordinated_engagement',
                targetPostId: validatedDetails.targetPostId,
                engagementType: validatedDetails.engagementType,
                urgency: validatedDetails.urgency,
                targetAgents: validatedDetails.targetAgents,
                timeWindow: validatedDetails.timeWindow || 300000, // 5 minutes default
                content: validatedDetails.content,
                hashtags: validatedDetails.hashtags,
                networkBoost: validatedDetails.networkBoost,
                strategy: engagementStrategy,
                sourceAgentId: runtime.agentId,
                timestamp: Date.now(),
            };

            // Announce the coordination event to the network
            await networkService.requestEngagement(
                validatedDetails.targetPostId,
                validatedDetails.engagementType,
                validatedDetails.urgency
            );

            // If network boost is enabled, request amplification
            if (validatedDetails.networkBoost) {
                await networkService.coordinateAmplification(
                    validatedDetails.targetPostId,
                    5, // amplification level
                    validatedDetails.timeWindow || 300000
                );
            }

            // Get network status for response
            const networkStatus = await networkService.getNetworkStatus();

            // Generate response
            const response = await generateCoordinationResponse(
                runtime,
                coordinationEvent,
                networkStatus,
                engagementStrategy
            );

            // Log the coordination event
            await runtime.createMemory({
                entityId: runtime.agentId,
                content: {
                    text: `Coordinated engagement event: ${validatedDetails.engagementType} for post ${validatedDetails.targetPostId}`,
                    ...coordinationEvent,
                },
                roomId: message.roomId,
                agentId: runtime.agentId,
                metadata: {
                    type: 'coordination_event',
                    timestamp: Date.now(),
                },
            }, 'coordination_events');

            // Emit event for other services
            await runtime.emitEvent('COORDINATED_ENGAGEMENT_INITIATED', {
                coordinationEvent,
                networkStatus,
                strategy: engagementStrategy,
            });

            return response;
        } catch (error) {
            logger.error('❌ Coordinated engagement action failed:', error);
            return false;
        }
    },
};

async function extractEngagementDetails(runtime: IAgentRuntime, message: Memory): Promise<any> {
    const content = message.content.text || '';

    // Use LLM to extract structured engagement details
    const prompt = `Extract engagement coordination details from this message:
"${content}"

Extract the following information:
- targetPostId: The ID of the post to engage with (if mentioned)
- engagementType: Type of engagement (like, retweet, reply, quote, thread)
- urgency: Urgency level (low, medium, high)
- content: Any specific content for replies or quotes
- hashtags: Any hashtags mentioned
- networkBoost: Whether network-wide amplification is requested

Return as JSON object with these fields. If information is not available, use reasonable defaults.`;

    try {
        const response = await runtime.useModel('TEXT_SMALL', {
            prompt,
            temperature: 0.3,
            maxTokens: 300,
        });

        // Parse the JSON response
        const details = JSON.parse(response);

        // Add fallback values
        details.targetPostId = details.targetPostId ||
            message.content.url ||
            extractPostIdFromUrl(content) ||
            `post_${Date.now()}`;

        details.engagementType = details.engagementType || 'like';
        details.urgency = details.urgency || 'medium';
        details.timeWindow = details.timeWindow || 300000; // 5 minutes
        details.networkBoost = details.networkBoost || false;

        return details;
    } catch (error) {
        logger.error('❌ Failed to extract engagement details:', error);

        // Return default values
        return {
            targetPostId: message.content.url || `post_${Date.now()}`,
            engagementType: 'like',
            urgency: 'medium',
            timeWindow: 300000,
            networkBoost: false,
        };
    }
}

function extractPostIdFromUrl(content: string): string | null {
    // Extract post ID from Twitter/X URLs
    const urlRegex = /(?:twitter\.com|x\.com)\/\w+\/status\/(\d+)/i;
    const match = content.match(urlRegex);
    return match ? match[1] : null;
}

async function generateCoordinationResponse(
    runtime: IAgentRuntime,
    coordinationEvent: any,
    networkStatus: any,
    engagementStrategy: any
): Promise<any> {
    const prompt = `Generate a response for coordinating network engagement:

Coordination Event:
- Type: ${coordinationEvent.engagementType}
- Urgency: ${coordinationEvent.urgency}
- Target Post: ${coordinationEvent.targetPostId}
- Network Boost: ${coordinationEvent.networkBoost ? 'Yes' : 'No'}

Network Status:
- Active Agents: ${networkStatus.activeAgents}
- Network Capacity: ${networkStatus.totalCapacity}
- Current Load: ${networkStatus.currentLoad}

Strategy: ${engagementStrategy ? engagementStrategy.name : 'Default'}

Generate a brief, professional response confirming the coordination and mentioning key details like number of agents involved and expected timeframe.`;

    try {
        const response = await runtime.useModel('TEXT_SMALL', {
            prompt,
            temperature: 0.7,
            maxTokens: 200,
        });

        return {
            text: response,
            thought: `Initiated coordinated engagement with ${networkStatus.activeAgents} agents using ${engagementStrategy?.name || 'default'} strategy`,
        };
    } catch (error) {
        logger.error('❌ Failed to generate coordination response:', error);

        return {
            text: `🎯 Coordinated ${coordinationEvent.engagementType} engagement initiated across ${networkStatus.activeAgents} agents with ${coordinationEvent.urgency} urgency. Expected completion within ${Math.round(coordinationEvent.timeWindow / 60000)} minutes.`,
            thought: 'Coordinated engagement action completed successfully',
        };
    }
}

export default coordinatedEngagementAction;