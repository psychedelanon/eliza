import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MentionReplyService } from '../src/services/mentionReplyService';
import { goobingstonMentions } from '../src/data/goobingstonTweets';
import { postAction } from '@elizaos/plugin-twitter';

vi.mock('@elizaos/plugin-twitter', () => ({
  postAction: { handler: vi.fn(async () => ({})) },
}));

describe('MentionReplyService', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    (postAction.handler as any).mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('replies to mentions from dataset', async () => {
    const runtime: any = {};
    const service = (await MentionReplyService.start(runtime)) as MentionReplyService;
    vi.advanceTimersByTime(60000);
    expect(postAction.handler).toHaveBeenCalled();
    const args = (postAction.handler as any).mock.calls[0][1];
    expect(args.content.text).toContain(`@${goobingstonMentions[0].username}`);
    await service.stop();
  });
});
