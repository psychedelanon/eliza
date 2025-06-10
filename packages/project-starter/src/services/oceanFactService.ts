import { Service, type IAgentRuntime, logger } from '@elizaos/core';
import { postAction } from '@elizaos/plugin-twitter';
import { randomOceanFact } from '../data/oceanFacts.js';

export class OceanFactService extends Service {
  static serviceType = 'ocean-facts';
  private timer: NodeJS.Timeout | null = null;

  static async start(runtime: IAgentRuntime): Promise<Service> {
    const service = new OceanFactService(runtime);
    await service.startScheduler();
    return service;
  }

  private async startScheduler() {
    const interval = Number(process.env.AQUA_FACT_INTERVAL_MS || 24 * 60 * 60 * 1000);
    if (isNaN(interval) || interval <= 0) {
      logger.warn('[AquaAgent] Invalid fact interval; scheduler disabled');
      return;
    }

    this.timer = setInterval(async () => {
      const fact = await this.fetchFact();
      try {
        await postAction.handler(this.runtime, { content: { text: fact } } as any, {} as any);
        logger.info('[AquaAgent] Ocean fact tweeted', { fact });
      } catch (err) {
        logger.error('[AquaAgent] Failed to post ocean fact', err);
      }
    }, interval) as unknown as NodeJS.Timeout;
  }

  private async fetchFact(): Promise<string> {
    const url = process.env.OCEAN_FACT_API_URL;
    if (url) {
      try {
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          const fact = data.fact || data.text;
          if (typeof fact === 'string' && fact.trim()) {
            return fact.trim();
          }
        }
      } catch (err) {
        logger.warn('[AquaAgent] Fact API failed', err);
      }
    }
    return randomOceanFact();
  }

  async stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}
