import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ScheduledTweetService } from '../src/services/scheduledTweetService';
import { goobingstonTweets } from '../src/data/goobingstonTweets';
import { postAction } from '@elizaos/plugin-twitter';

vi.mock('@elizaos/plugin-twitter', () => ({
  postAction: { handler: vi.fn(async () => ({})) },
}));

describe('ScheduledTweetService', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    (postAction.handler as any).mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('posts tweets from dataset on interval', async () => {
    const runtime: any = {};
    const service = (await ScheduledTweetService.start(runtime)) as ScheduledTweetService;
    vi.advanceTimersByTime(3600000);
    expect(postAction.handler).toHaveBeenCalledWith(
      runtime,
      { content: { text: goobingstonTweets[0] } },
      {}
    );
    await service.stop();
  });
});
