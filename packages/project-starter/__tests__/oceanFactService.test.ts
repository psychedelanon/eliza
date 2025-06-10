import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { OceanFactService } from '../src/services/oceanFactService';
import { postAction } from '@elizaos/plugin-twitter';
import { randomOceanFact } from '../src/data/oceanFacts';

vi.mock('@elizaos/plugin-twitter', () => ({
  postAction: { handler: vi.fn(async () => ({})) },
}));

vi.mock('../src/data/oceanFacts', () => ({
  randomOceanFact: vi.fn(() => 'Test fact'),
}));

describe('OceanFactService', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    (postAction.handler as any).mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('posts ocean facts on interval', async () => {
    const runtime: any = {};
    const service = (await OceanFactService.start(runtime)) as OceanFactService;
    vi.advanceTimersByTime(24 * 60 * 60 * 1000);
    expect(postAction.handler).toHaveBeenCalledWith(
      runtime,
      { content: { text: 'Test fact' } },
      {}
    );
    await service.stop();
  });
});
