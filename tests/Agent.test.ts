import Agent, { AgentAdapters } from '../src/agents/Agent';

class DummyAgent extends Agent {
  async think(): Promise<void> {}
  async plan(): Promise<void> {}
  async act(): Promise<void> {}
}

describe('Agent', () => {
  it('stores provided initialization data', () => {
    const adapters: AgentAdapters = {
      twitter: {},
      telegram: {},
      quickfire: {},
      memory: {},
      strategy: {},
    };
    const agent = new DummyAgent('1', 'persona', {}, adapters);
    expect(agent.id).toBe('1');
    expect(agent.persona).toBe('persona');
    expect(agent.state).toEqual({});
  });
});
