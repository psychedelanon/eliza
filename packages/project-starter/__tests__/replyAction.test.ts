import { describe, it, expect, vi } from 'vitest';
import { createMockRuntime, createMockMessage } from './test-utils';
import { EventType } from '@elizaos/core';
import { initAquaAgent } from '../src/aquaAgent.character.js';

describe('AquaAgent fallback handler', () => {
  it('sends fallback reply when REPLY action missing', async () => {
    const runtime = createMockRuntime({ actions: [] as any[] });
    let sentText = '';
    runtime.sendMessageToTarget = vi.fn(async (_target, content) => {
      sentText = (content as any).text || '';
    });

    await initAquaAgent(runtime);

    const handler = (runtime.registerEvent as any).mock.calls.find((c: any[]) => c[0] === EventType.MESSAGE_RECEIVED)?.[1];
    expect(handler).toBeTypeOf('function');

    const message = createMockMessage('hi');
    await handler({ runtime, message, source: 'test', callback: async () => {} });
    expect(sentText).toBe('Still initializing...');
  });
});
