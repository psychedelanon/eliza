export interface AgentAdapters<TTwitter = unknown, TTelegram = unknown, TQuickfire = unknown, TMemory = unknown, TStrategy = unknown> {
  twitter: TTwitter;
  telegram: TTelegram;
  quickfire: TQuickfire;
  memory: TMemory;
  strategy: TStrategy;
}

/**
 * Base abstract Agent class defining lifecycle hooks and dependencies.
 */
export default abstract class Agent<A extends AgentAdapters = AgentAdapters> {
  /** Unique identifier for the agent */
  public readonly id: string;
  /** Descriptive persona */
  public readonly persona: string;
  /** Mutable internal state */
  public readonly state: Record<string, unknown>;

  protected readonly adapters: A;

  constructor(id: string, persona: string, state: Record<string, unknown>, adapters: A) {
    this.id = id;
    this.persona = persona;
    this.state = state;
    this.adapters = adapters;
  }

  /**
   * Perform internal reasoning steps.
   */
  abstract think(): Promise<void>;

  /**
   * Determine actions based on current state.
   */
  abstract plan(): Promise<void>;

  /**
   * Execute the previously determined plan.
   */
  abstract act(): Promise<void>;
}
