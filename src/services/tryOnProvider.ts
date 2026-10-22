import { apiCreateTryOnSession, apiGetTryOnSession, getAccessToken } from './api';
import type { TryOnSession } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class TryOnError extends Error {
  constructor(
    message: string,
    public readonly kind: 'not_configured' | 'auth' | 'timeout' | 'runtime' | 'network',
  ) {
    super(message);
    this.name = 'TryOnError';
  }
}

export interface TryOnResult {
  session: TryOnSession;
  resultUrl: string | null;
}

const POLL_INTERVAL_MS = 2000;
const POLL_TIMEOUT_MS = 120_000;

/**
 * Backend-proxied virtual try-on. Uploads the person photo to the backend,
 * which creates a try-on session and processes it (FASHN or mock). We poll
 * the session status until it completes or fails.
 */
export async function performTryOn(
  personImage: File,
  productId: string,
  consent: boolean,
): Promise<TryOnResult> {
  let session: TryOnSession;
  try {
    session = await apiCreateTryOnSession({
      productId,
      consent,
      personImage,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Could not start the try-on.';
    if (msg.includes('401')) throw new TryOnError(msg, 'auth');
    throw new TryOnError(msg, 'runtime');
  }

  const deadline = Date.now() + POLL_TIMEOUT_MS;

  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));

    try {
      session = await apiGetTryOnSession(session.id);
    } catch {
      throw new TryOnError('Lost connection while processing.', 'network');
    }

    if (session.status === 'completed') {
      const resultUrl = session.resultImage
        ? `${API_BASE}${session.resultImage}`
        : null;
      return { session, resultUrl };
    }

    if (session.status === 'failed') {
      throw new TryOnError('The try-on generation failed.', 'runtime');
    }
  }

  throw new TryOnError('The try-on is taking too long. Please try again.', 'timeout');
}

// Prepend API base to relative image URLs returned by the backend
export function resolveImageUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('http')) return url;
  return `${API_BASE}${url}`;
}

// Keep the token available for image loading via a helper
export { getAccessToken };
