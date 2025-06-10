import { test, expect } from 'bun:test';

// This test runs the launch script and waits for the ready message

test('launch script initializes AquaAgent', async () => {
  const proc = Bun.spawn({
    cmd: ['bun', 'run', 'src/launchAquaAgent.ts'],
    cwd: import.meta.dir + '/..',
    env: { ...process.env, NODE_ENV: 'test' },
    stdout: 'pipe',
    stderr: 'pipe',
  });

  let ready = false;
  const startTime = Date.now();
  const timeoutMs = 20000;

  for await (const chunk of proc.stdout) {
    const text = chunk.toString();
    if (text.includes('AquaAgent ready')) {
      ready = true;
      break;
    }
    if (Date.now() - startTime > timeoutMs) {
      break;
    }
  }

  proc.kill();
  expect(ready).toBe(true);
});
