import { describe, it, expect } from 'vitest';
import { aquaAgentCharacter } from '../src/aquaAgent.character';

describe('AquaAgent Character', () => {
  it('should have name AquaAgent', () => {
    expect(aquaAgentCharacter.name).toBe('AquaAgent');
  });

  it('should include twitter plugin when credentials provided', () => {
    if (process.env.TWITTER_USERNAME) {
      expect(aquaAgentCharacter.plugins).toContain('@elizaos/plugin-twitter');
    }
  });

  it('should have example messages', () => {
    expect(Array.isArray(aquaAgentCharacter.messageExamples)).toBe(true);
    expect(aquaAgentCharacter.messageExamples.length).toBeGreaterThan(0);
  });
});
