import { Service, type IAgentRuntime, logger } from '@elizaos/core';
import { postAction } from '@elizaos/plugin-twitter';
import { goobingstonMentions } from '../data/goobingstonTweets.js';

export class MentionReplyService extends Service {
  static serviceType = 'mention-replies';
  private timer: NodeJS.Timeout | null = null;
  private index = 0;

  static async start(runtime: IAgentRuntime): Promise<Service> {
    const service = new MentionReplyService(runtime);
    await service.startProcessing();
    return service;
  }

  private async startProcessing() {
    const interval = Number(process.env.AQUA_MENTION_INTERVAL_MS || 60000);
    if (isNaN(interval) || interval <= 0) {
      logger.warn('[AquaAgent] Invalid mention interval; mention replies disabled');
      return;
    }

    this.timer = setInterval(async () => {
      const mention = goobingstonMentions[this.index % goobingstonMentions.length];
      const replyText = `@${mention.username} Thanks for the mention! Stay hydrated.`;
      try {
        await postAction.handler(this.runtime, { content: { text: replyText, inReplyToId: mention.id } } as any, {} as any);
        logger.info('[AquaAgent] Replied to mention', { id: mention.id });
      } catch (err) {
        logger.error('[AquaAgent] Failed to reply to mention', err);
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
