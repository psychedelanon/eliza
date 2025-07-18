import express from 'express';
import { AgentRuntime, type Character } from '@elizaos/core';
import { twitterEngagementPlugin } from '@elizaos/plugin-twitter-engagement';
import dotenv from 'dotenv';

export interface CoordinationServices {
  requestEngagement: (
    postId: string,
    type: 'like' | 'retweet' | 'reply' | 'quote',
    urgency?: 'high' | 'medium' | 'low'
  ) => Promise<void>;
  getNetworkStatus: () => Promise<{
    activeAgents: number;
    totalCapacity: number;
    currentLoad: number;
    pendingEvents: number;
  }>;
}

export function createEngagementServer(services: CoordinationServices) {
  const app = express();
  app.use(express.json());

  app.post('/coordinate', async (req, res) => {
    try {
      const {
        targetPostId,
        engagementTypes = ['like'],
        urgency = 'medium',
      } = req.body || {};

      if (!targetPostId) {
        res.status(400).json({ error: 'targetPostId required' });
        return;
      }

      for (const type of engagementTypes as Array<'like' | 'retweet' | 'reply' | 'quote'>) {
        await services.requestEngagement(targetPostId, type, urgency);
      }

      res.json({ success: true });
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.get('/network/status', async (_req, res) => {
    try {
      const status = await services.getNetworkStatus();
      res.json(status);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  return app;
}

export async function startServer(port = 3000) {
  dotenv.config();
  const character: Character = {
    name: 'Coordinator',
    username: 'coordinator',
    plugins: ['@elizaos/plugin-twitter', '@elizaos/plugin-twitter-engagement'],
  };

  const runtime = new AgentRuntime({
    character,
    plugins: [twitterEngagementPlugin],
    settings: process.env,
  });

  await runtime.initialize();

  const networkService = runtime.getService('network-coordination') as CoordinationServices;
  const app = createEngagementServer(networkService);

  app.listen(port, () => {
    console.log(`Engagement server listening on ${port}`);
  });

  return { app, runtime };
}

if (require.main === module) {
  startServer();
}
