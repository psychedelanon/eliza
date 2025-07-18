import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import fetch from 'node-fetch';
import { createEngagementServer, CoordinationServices } from './networkServer';
import http from 'http';

let server: http.Server;
let baseUrl: string;
let requests: any[];

beforeEach(async () => {
  requests = [];
  const services: CoordinationServices = {
    requestEngagement: async (postId, type, urgency) => {
      requests.push({ postId, type, urgency });
    },
    getNetworkStatus: async () => ({
      activeAgents: 2,
      totalCapacity: 200,
      currentLoad: 20,
      pendingEvents: 1,
    }),
  };
  const app = createEngagementServer(services);
  server = app.listen(0);
  const { port } = server.address() as any;
  baseUrl = `http://localhost:${port}`;
});

afterEach(async () => {
  await new Promise((resolve) => server.close(resolve));
});

describe('engagement server', () => {
  it('returns network status', async () => {
    const res = await fetch(`${baseUrl}/network/status`);
    const data = await res.json();
    expect(res.status).toBe(200);
    expect(data.activeAgents).toBe(2);
  });

  it('handles coordinate request', async () => {
    const res = await fetch(`${baseUrl}/coordinate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ targetPostId: '123', engagementTypes: ['like', 'retweet'], urgency: 'high' }),
    });
    const data = await res.json();
    expect(res.status).toBe(200);
    expect(data.success).toBe(true);
    expect(requests.length).toBe(2);
    expect(requests[0]).toEqual({ postId: '123', type: 'like', urgency: 'high' });
  });
});
