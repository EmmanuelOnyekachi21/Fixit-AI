import { useState, useEffect } from 'react';

/**
 * Hook to detect if the app is running in demo mode
 * Demo mode is enabled when there's no backend connection
 */
export function useDemoMode() {
  const [isDemoMode, setIsDemoMode] = useState(true);

  useEffect(() => {
    // Try to ping the backend API
    const checkBackend = async () => {
      try {
        const response = await fetch('/api/health', { 
          method: 'GET',
          signal: AbortSignal.timeout(2000)
        });
        setIsDemoMode(!response.ok);
      } catch {
        setIsDemoMode(true);
      }
    };

    checkBackend();
  }, []);

  return isDemoMode;
}

/**
 * Hook for simulating API delays in demo mode
 */
export function useSimulatedDelay(minMs: number = 500, maxMs: number = 1500) {
  return () => {
    const delay = Math.random() * (maxMs - minMs) + minMs;
    return new Promise(resolve => setTimeout(resolve, delay));
  };
}
