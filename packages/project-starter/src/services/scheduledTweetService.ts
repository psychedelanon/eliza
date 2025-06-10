import { Service, type IAgentRuntime, logger } from '@elizaos/core';
import { postAction } from '@elizaos/plugin-twitter';
import { goobingstonTweets } from '../data/goobingstonTweets.js';

export class ScheduledTweetService extends Service {
  static serviceType = 'scheduled-tweets';
  private timer: NodeJS.Timeout | null = null;
  private index = 0;

  static async start(runtime: IAgentRuntime): Promise<Service> {
    const service = new ScheduledTweetService(runtime);
    await service.startScheduler();
    return service;
  }

  private async startScheduler() {
    const interval = Number(process.env.AQUA_TWEET_INTERVAL_MS || 3600000);
    if (isNaN(interval) || interval <= 0) {
      logger.warn('[AquaAgent] Invalid tweet interval; scheduler disabled');
      return;
    }

    this.timer = setInterval(async () => {
      const text = goobingstonTweets[this.index % goobingstonTweets.length];
      try {
        await postAction.handler(this.runtime, { content: { text } } as any, {} as any);
        logger.info('[AquaAgent] Scheduled tweet posted', { text });
      } catch (err) {
        logger.error('[AquaAgent] Failed scheduled tweet', err);
      }
      this.index++;
    }, interval) as unknown as NodeJS.Timeout;
  }

  async stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}
