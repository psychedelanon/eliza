export const DEFAULT_SERVER_URL = 'http://localhost:3000';

export function getServerUrl(env: Record<string, string | undefined> = {}) {
  if (typeof window !== 'undefined' && (window as any).ENV?.VITE_SERVER_URL) {
    return (window as any).ENV.VITE_SERVER_URL as string;
  }
  if (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_SERVER_URL) {
    return (import.meta as any).env.VITE_SERVER_URL as string;
  }
  return env.VITE_SERVER_URL || DEFAULT_SERVER_URL;
}
