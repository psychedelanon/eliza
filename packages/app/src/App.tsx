import { useEffect, useState } from 'react';
import { getServerUrl } from './utils';

const SERVER_URL = getServerUrl();

export default function App() {
  const [status, setStatus] = useState<'starting' | 'running' | 'error'>('starting');
  const [error, setError] = useState<string | null>(null);
  const [isServerAccessible, setIsServerAccessible] = useState(false);

  const checkServer = async () => {
    try {
      await fetch(SERVER_URL, { method: 'HEAD', mode: 'no-cors' });
      return true;
    } catch {
      return false;
    }
  };

  useEffect(() => {
    const start = async () => {
      try {
        setStatus('running');
        const interval = setInterval(async () => {
          if (await checkServer()) {
            setIsServerAccessible(true);
            clearInterval(interval);
          }
        }, 1000);
        setTimeout(() => clearInterval(interval), 60000);
      } catch (err) {
        setStatus('error');
        setError(err instanceof Error ? err.message : String(err));
      }
    };
    start();
  }, []);

  if (status === 'running' && isServerAccessible) {
    return (
      <main className="app">
        <h1>Eliza Server Ready</h1>
        <a href={SERVER_URL} className="open-link" aria-label="Open Eliza client">
          Open Client
        </a>
      </main>
    );
  }

  return (
    <main className="app">
      {status === 'error' ? (
        <>
          <h1 className="error">Error</h1>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="btn">
            Retry
          </button>
        </>
      ) : (
        <>
          <h1>Starting Eliza Server…</h1>
          <div className="spinner" role="status" aria-live="polite" aria-label="Loading" />
        </>
      )}
    </main>
  );
}
