import { describe, it, expect, afterEach, vi } from 'vitest';

// Helper to dynamically import the character module
async function loadAqua() {
  vi.resetModules();
  return await import('../src/aquaAgent.character');
}

afterEach(() => {
  delete process.env.TWITTER_USERNAME;
  delete process.env.TWITTER_PASSWORD;
  delete process.env.TWITTER_EMAIL;
  delete process.env.ENABLE_TWITTER_CLIENT;
});

describe('AquaAgent Character', () => {
  it('should have name AquaAgent', async () => {
    const { aquaAgentCharacter } = await loadAqua();
    expect(aquaAgentCharacter.name).toBe('AquaAgent');
  });

  it('should include twitter plugin when flag and credentials provided', async () => {
    process.env.ENABLE_TWITTER_CLIENT = 'true';
    process.env.TWITTER_USERNAME = 'user';
    process.env.TWITTER_PASSWORD = 'pw';
    process.env.TWITTER_EMAIL = 'e@x.com';

    const { aquaAgentCharacter } = await loadAqua();
    expect(aquaAgentCharacter.plugins).toContain('@elizaos/plugin-twitter');
  });

  it('should not include twitter plugin when flag disabled', async () => {
    process.env.TWITTER_USERNAME = 'user';
    process.env.TWITTER_PASSWORD = 'pw';
    process.env.TWITTER_EMAIL = 'e@x.com';

    const { aquaAgentCharacter } = await loadAqua();
    expect(aquaAgentCharacter.plugins).not.toContain('@elizaos/plugin-twitter');
  });

  it('should have example messages', async () => {
    const { aquaAgentCharacter } = await loadAqua();
    expect(Array.isArray(aquaAgentCharacter.messageExamples)).toBe(true);
    expect(aquaAgentCharacter.messageExamples.length).toBeGreaterThan(0);
  });

  it('initAquaAgent posts startup tweet when twitter service available', async () => {
    process.env.ENABLE_TWITTER_CLIENT = 'true';
    process.env.TWITTER_USERNAME = 'test';
    process.env.TWITTER_PASSWORD = 'pw';
    process.env.TWITTER_EMAIL = 'e@x.com';
    const { initAquaAgent } = await loadAqua();
    let posted: string | undefined;
    const runtime: any = {
      getService: () => ({
        sendTweet: async ({ content }: { content: string }) => {
          posted = content;
          return { tweetId: '123' };
        },
      }),
    };

    await initAquaAgent(runtime);

    expect(posted).toBe(
      '🌊 AquaAgent is online! Ready to flow with facts and inspiration. #AquaAgent'
    );
  });
});
