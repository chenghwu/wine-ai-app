import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const auth = request.headers.get('Authorization');
  const expected = `Bearer ${process.env.CRON_SECRET}`;

  if (auth !== expected) {
    return new Response('Unauthorized', { status: 401 });
  }

  
  // Ping Render backend
  const backendUrl = 'https://wine-ai-app.onrender.com/api/db-test';
  const maxRetries = 5;
  const baseDelayMs = 2000; // 2 seconds
    
  async function pingBackend(attempt = 1): Promise<Response> {
    // Setup timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 seconds timeout

    try {
      const res = await fetch(backendUrl, { method: 'GET', signal: controller.signal });
      clearTimeout(timeoutId);

      if (!res.ok) {
        throw new Error(`Backend responded with status ${res.status}`);
      }

      return res;
    } catch (error) {
      clearTimeout(timeoutId);

      if (attempt < maxRetries) {
        const backoffTime = baseDelayMs * Math.pow(2, attempt - 1); // Exponential backoff: 2s, 4s, 8s
        console.warn(`Ping attempt ${attempt} failed. Retrying in ${backoffTime / 1000}s...`, error);
        await new Promise((resolve) => setTimeout(resolve, backoffTime));
        return pingBackend(attempt + 1);
      } else {
        console.error('All ping attempts failed.', error);
        throw error;
      }
    }
  }

  try {
    await pingBackend();
    return NextResponse.json({ ok: true });
  } catch {
    return new Response('Failed to ping backend after retries.', { status: 500 });
  }
}