import { describe, it, expect } from 'vitest';
import { aquaAgentCharacter } from '../src/aquaAgent.character';

describe('AquaAgent Character', () => {
  it('should have name AquaAgent', () => {
    expect(aquaAgentCharacter.name).toBe('AquaAgent');
  });

  it('should include twitter plugin when credentials provided', () => {
    const hasUserCreds =
      process.env.TWITTER_USERNAME &&
      process.env.TWITTER_PASSWORD &&
      process.env.TWITTER_EMAIL;
    const hasApiCreds =
      process.env.TWITTER_API_KEY &&
      (process.env.TWITTER_API_SECRET_KEY || process.env.TWITTER_API_SECRET) &&
      process.env.TWITTER_ACCESS_TOKEN &&
      process.env.TWITTER_ACCESS_TOKEN_SECRET;

    if (hasUserCreds || hasApiCreds) {
      expect(aquaAgentCharacter.plugins).toContain('@elizaos/plugin-twitter');
    }
  });

  it('should have example messages', () => {
    expect(Array.isArray(aquaAgentCharacter.messageExamples)).toBe(true);
    expect(aquaAgentCharacter.messageExamples.length).toBeGreaterThan(0);
  });
});
