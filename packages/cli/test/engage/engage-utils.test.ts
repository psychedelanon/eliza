import { describe, it, expect } from 'vitest';
import { tweetIdFrom, parseMessageList } from '../../src/commands/engage';

describe('engage utils', () => {
  it('extracts tweet id from url', () => {
    expect(tweetIdFrom('https://twitter.com/user/status/12345')).toBe('12345');
  });

  it('parses message lists', () => {
    const res = parseMessageList('BotA:"hi",BotB:"yo"');
    expect(res.BotA).toBe('hi');
    expect(res.BotB).toBe('yo');
  });
});
