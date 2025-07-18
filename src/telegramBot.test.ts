import { describe, it, expect } from 'vitest';
import { extractTweetId } from './telegramBot';

describe('extractTweetId', () => {
  it('extracts id from url', () => {
    expect(extractTweetId('https://twitter.com/user/status/12345')).toBe('12345');
  });
  it('returns null if missing', () => {
    expect(extractTweetId('hello')).toBeNull();
  });
});
