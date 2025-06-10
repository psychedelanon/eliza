import { type TestSuite, type IAgentRuntime } from '@elizaos/core';
import { aquaAgentCharacter } from '../src/aquaAgent.character.js';

export class AquaAgentTestSuite implements TestSuite {
  name = 'aqua-agent';
  description = 'E2E tests for AquaAgent configuration';

  tests = [
    {
      name: 'AquaAgent runtime environment test',
      fn: async (runtime: IAgentRuntime) => {
        if (!runtime.character) {
          throw new Error('Character not loaded in runtime');
        }
        if (runtime.character.name !== aquaAgentCharacter.name) {
          throw new Error(`Expected character name to be ${aquaAgentCharacter.name}, got ${runtime.character.name}`);
        }
        if (process.env.TWITTER_USERNAME) {
          const hasTwitter = runtime.character.plugins?.some((p) => typeof p === 'string' && p.includes('twitter'));
          if (!hasTwitter) {
            throw new Error('Twitter plugin not configured');
          }
        }
      },
    },
  ];
}

export default new AquaAgentTestSuite();
