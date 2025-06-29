import { describe, it, expect } from 'vitest';
import { getServerUrl, DEFAULT_SERVER_URL } from './utils';

describe('getServerUrl', () => {
  it('returns env url when provided', () => {
    const url = getServerUrl({ VITE_SERVER_URL: 'https://example.com' });
    expect(url).toBe('https://example.com');
  });

  it('falls back to default when env missing', () => {
    const url = getServerUrl({});
    expect(url).toBe(DEFAULT_SERVER_URL);
  });
});
