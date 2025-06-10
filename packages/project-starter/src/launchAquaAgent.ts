import { AgentRuntime, AgentServer, ModelType, logger } from '@elizaos/core';
import aquaAgentCharacter, { initAquaAgent } from './aquaAgent.character.js';
import plugin from './plugin.js';

/**
 * Start an AgentServer and register AquaAgent.
 * The model is warmed up once the runtime is initialized.
 */
export async function launchAquaAgent() {
  const server = new AgentServer();
  await server.initialize();

  const runtime = new AgentRuntime({
    character: aquaAgentCharacter,
    plugins: [plugin],
    settings: process.env as any,
  });

  await runtime.initialize();
  await initAquaAgent(runtime);
  server.registerAgent(runtime);

  try {
    await runtime.useModel(ModelType.TEXT_SMALL, { prompt: ' ' });
    logger.info('[AquaAgent] Model preloaded');
  } catch (error) {
    logger.warn('[AquaAgent] Model preload failed', error);
  }

  const port = Number(process.env.SERVER_PORT || 3000);
  server.start(port);
  logger.success(`AquaAgent ready on port ${port}`);
  return { server, runtime };
}

if (import.meta.main) {
  launchAquaAgent().catch((err) => {
    logger.error('Failed to launch AquaAgent', err);
    process.exit(1);
  });
}
