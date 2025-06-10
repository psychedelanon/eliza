import { Service, type IAgentRuntime, logger } from '@elizaos/core';
import { postAction } from '@elizaos/plugin-twitter';

/**
 * Fetch trending hashtags from trends24.in
 */
export async function fetchTrendingTopics(location = ''): Promise<string[]> {
  const url = `https://trends24.in/${location}`;
  const res = await fetch(url);
  const html = await res.text();
  const matches = [...html.matchAll(/>#([^<]+)/g)].map((m) => m[1]);
  // return unique first 10 topics
  return Array.from(new Set(matches)).slice(0, 10);
}

/** Compose an assertive tweet using trending topics */
export function composeDominantTweet(topics: string[]): string {
  const statement = `Here\'s what matters: ${topics.slice(0, 2).join(' ')}.`;
  return `${statement} Stay sharp.`.slice(0, 260);
}

export class SocialEngagementService extends Service {
  static serviceType = 'social-engagement';
  capabilityDescription = 'Automatically posts assertive tweets based on trending topics';

  private timer: NodeJS.Timeout | null = null;
  private postIntervalMs: number;

  constructor(runtime: IAgentRuntime) {
    super(runtime);
    const interval = Number(runtime.getSetting('proactivePostIntervalMs'));
    this.postIntervalMs = isNaN(interval) ? 4 * 60 * 60 * 1000 : interval;
  }

  static async start(runtime: IAgentRuntime): Promise<Service> {
    const service = new SocialEngagementService(runtime);
    await service.startScheduler();
    return service;
  }

  private async startScheduler() {
    this.timer = setInterval(async () => {
      try {
        await this.runtime.createTask({
          name: 'AQUA_PROACTIVE_POST',
          description: 'Post about trending topics',
          tags: ['queue', 'repeat'],
          metadata: {
            updateInterval: this.postIntervalMs,
            updatedAt: Date.now(),
          },
        });
      } catch (err) {
        logger.error('[AquaAgent] Failed to create post task', err);
      }
    }, this.postIntervalMs) as unknown as NodeJS.Timeout;

    // register worker
    this.runtime.registerTaskWorker({
      name: 'AQUA_PROACTIVE_POST',
      validate: async () => true,
      execute: async () => {
        try {
          const topics = await fetchTrendingTopics();
          const text = composeDominantTweet(topics);
          await postAction.handler(this.runtime, { content: { text } } as any, {} as any);
        } catch (err) {
          logger.error('[AquaAgent] Failed to post trending tweet', err);
        }
      },
    });
  }

  async stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}
