import { Service, type IAgentRuntime, logger } from '@elizaos/core';
import { postAction } from '@elizaos/plugin-twitter';
import { goobingstonMentions } from '../data/goobingstonTweets.js';
import { randomOceanFact } from '../data/oceanFacts.js';

function classifyMention(text: string): 'question' | 'greeting' | 'compliment' | 'other' {
  const lower = text.toLowerCase();
  if (/[?]$/.test(text) || /(how|what|why|any|please)/i.test(text)) return 'question';
  if (/(hello|hi|hey|greetings)/i.test(lower)) return 'greeting';
  if (/(love|great|awesome|amazing|nice)/i.test(lower)) return 'compliment';
  return 'other';
}

function createReply(username: string, type: string): string {
  const prefix = `@${username} `;
  switch (type) {
    case 'question':
      return `${prefix}Great question! I'll dive right in soon.`;
    case 'greeting':
      return `${prefix}Hello there! 🌊`;
    case 'compliment':
      return `${prefix}Thank you! I'm glad my tides inspire you. 💧`;
    default:
      return `${prefix}Thanks for the mention! Stay hydrated.`;
  }
}

function shouldFollowUp(type: string): boolean {
  return type === 'question' || Math.random() < 0.2;
}

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
      const type = classifyMention(mention.text);
      const replyText = createReply(mention.username, type);
      try {
        const result = await postAction.handler(
          this.runtime,
          { content: { text: replyText, inReplyToId: mention.id } } as any,
          {} as any
        );
        const replyId = result?.tweetId ?? result?.id;
        logger.info('[AquaAgent] Replied to mention', { id: mention.id });

        if (shouldFollowUp(type)) {
          const followUp = `Did you know? ${randomOceanFact()}`;
          await postAction.handler(
            this.runtime,
            { content: { text: followUp, inReplyToId: replyId } } as any,
            {} as any
          );
          logger.info('[AquaAgent] Posted follow-up reply');
        }
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
