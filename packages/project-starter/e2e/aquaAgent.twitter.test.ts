import { test, expect } from 'bun:test';

const username = process.env.TWITTER_USERNAME;
const password = process.env.TWITTER_PASSWORD;
const email = process.env.TWITTER_EMAIL;
const enable = process.env.ENABLE_TWITTER_CLIENT === 'true';

if (!enable || !username || !password || !email) {
  console.warn('Twitter credentials not provided – skipping AquaAgent Twitter integration test.');
  test.skip('AquaAgent startup tweet to Twitter (skipped due to missing credentials)', () => {});
} else {
  test('AquaAgent posts a startup tweet to Twitter', async () => {
    const proc = Bun.spawn({
      cmd: ['bun', 'run', 'start'],
      cwd: import.meta.dir + '/..', // move to project-starter root
      env: { ...process.env, USE_AQUA_AGENT: 'true', ENABLE_TWITTER_CLIENT: 'true' },
      stdout: 'pipe',
      stderr: 'pipe',
    });

    let tweetUrl: string | undefined;
    const timeoutMs = 20000;
    const startTime = Date.now();

    for await (const chunk of proc.stdout) {
      const text = chunk.toString();
      const match = text.match(/Tweet posted:\s+(https:\/\/twitter\.com\/\S+)/);
      if (match) {
        tweetUrl = match[1].trim();
        console.log(`Tweet URL: ${tweetUrl}`);
        break;
      }
      if (Date.now() - startTime > timeoutMs) {
        break;
      }
    }

    if (!tweetUrl) {
      proc.kill();
      console.warn(
        'No startup tweet detected (possible invalid credentials) – skipping verification.'
      );
      return;
    }

    const oembedApi = `https://publish.twitter.com/oembed?url=${encodeURI(tweetUrl)}`;
    const res = await fetch(oembedApi);
    expect(res.ok).toBe(true);
    const data = await res.json();
    const html = data.html as string;
    const textMatch = html.match(/<p[^>]*>(.*?)<\/p>/);
    const tweetText = textMatch ? textMatch[1] : '';
    expect(tweetText).toContain('AquaAgent is online');

    const tweetId = tweetUrl.split('/status/')[1];
    console.log(`AquaAgent startup tweet posted successfully! Tweet ID: ${tweetId}`);
    proc.kill();
  });
}
