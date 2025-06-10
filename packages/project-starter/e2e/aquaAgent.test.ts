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
          const hasTwitter = runtime.character.plugins?.some(
            (p) => typeof p === 'string' && p.includes('twitter')
          );
          if (!hasTwitter) {
            throw new Error('Twitter plugin not configured');
          }
        }
      },
    },
    {
      name: 'AquaAgent responds to a message',
      fn: async (runtime: IAgentRuntime) => {
        let reply = '';
        await runtime.emitEvent(EventType.MESSAGE_RECEIVED, {
          runtime,
          source: 'test',
          message: {
            entityId: runtime.agentId,
            roomId: runtime.agentId,
            content: { text: 'ping', source: 'test' },
          } as any,
          callback: async (content) => {
            reply = content.text || '';
          },
        });
        if (!reply) throw new Error('No reply generated');
      },
    },
  ];
}

export default new AquaAgentTestSuite();
