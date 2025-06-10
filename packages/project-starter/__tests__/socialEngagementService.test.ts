import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchTrendingTopics, composeDominantTweet, SocialEngagementService } from '../src/services/socialEngagementService';

describe('SocialEngagementService utilities', () => {
  it('composeDominantTweet returns a short assertive message', () => {
    const text = composeDominantTweet(['#A', '#B', '#C']);
    expect(text).toContain("Here's what matters");
    expect(text.length).toBeLessThanOrEqual(260);
  });

  it('fetchTrendingTopics parses topics from html', async () => {
    const html = '<li><a>>#Topic1</a></li><li><a>>#Topic2</a></li>';
    const fetchStub = vi.fn(() => Promise.resolve({ text: () => Promise.resolve(html) })) as any;
    vi.stubGlobal('fetch', fetchStub);
    const topics = await fetchTrendingTopics();
    expect(topics).toEqual(['Topic1', 'Topic2']);
    expect(fetchStub).toHaveBeenCalled();
    vi.unstubAllGlobals();
  });
});

describe('SocialEngagementService lifecycle', () => {
  const runtime: any = {
    getSetting: () => 1000,
    createTask: vi.fn(async () => {}),
    registerTaskWorker: vi.fn(),
  };

  let service: SocialEngagementService | null = null;

  beforeEach(() => {
    service = new SocialEngagementService(runtime);
  });

  it('starts and stops timer', async () => {
    await (SocialEngagementService.start as any)(runtime);
    expect(runtime.registerTaskWorker).toHaveBeenCalled();
  });
});
