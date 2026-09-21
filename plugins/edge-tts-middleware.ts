import type { IncomingMessage, ServerResponse } from 'node:http'
import type { Plugin } from 'vite'
import { EdgeTTS } from 'edge-tts-universal'

function rateToPercent(speed: number): string {
  const pct = Math.round((speed - 1) * 100)
  return pct >= 0 ? `+${pct}%` : `${pct}%`
}

async function readJson(req: IncomingMessage): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = []
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk))
  }
  const raw = Buffer.concat(chunks).toString('utf8')
  if (!raw.trim()) return {}
  return JSON.parse(raw) as Record<string, unknown>
}

/**
 * Local / preview OpenAI-compatible Edge TTS endpoint at /api/tts (and under base).
 * GitHub Pages has no server — production client falls back to a CORS Edge relay.
 */
export function edgeTtsMiddleware(): Plugin {
  const handler = async (
    req: IncomingMessage,
    res: ServerResponse,
    next: () => void,
  ) => {
    const url = req.url || ''
    const path = url.split('?')[0] || ''
    const isTts =
      path === '/api/tts' ||
      path.endsWith('/api/tts') ||
      path === '/vox-lux/api/tts'

    if (!isTts) {
      next()
      return
    }

    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

    if (req.method === 'OPTIONS') {
      res.statusCode = 204
      res.end()
      return
    }

    if (req.method !== 'POST') {
      res.statusCode = 405
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify({ error: 'POST only' }))
      return
    }

    try {
      const body = await readJson(req)
      const text = String(body.input ?? body.text ?? '').trim()
      const voice = String(body.voice ?? 'en-US-ChristopherNeural')
      const speed =
        typeof body.speed === 'number'
          ? body.speed
          : typeof body.rate === 'string'
            ? 1 + Number(String(body.rate).replace('%', '')) / 100
            : 1
      const pitch =
        typeof body.pitch === 'string' && body.pitch.includes('Hz')
          ? body.pitch
          : '-8Hz'

      if (!text) {
        res.statusCode = 400
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ error: 'Missing text/input' }))
        return
      }

      const tts = new EdgeTTS(text, voice, {
        rate: rateToPercent(Number.isFinite(speed) ? speed : 1),
        pitch,
      })
      const result = await tts.synthesize()
      const buf = Buffer.from(await result.audio.arrayBuffer())

      res.statusCode = 200
      res.setHeader('Content-Type', 'audio/mpeg')
      res.setHeader('Cache-Control', 'no-store')
      res.end(buf)
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err)
      console.error('[edge-tts-middleware]', message)
      res.statusCode = 502
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify({ error: message }))
    }
  }

  return {
    name: 'edge-tts-middleware',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        void handler(req, res, next)
      })
    },
    configurePreviewServer(server) {
      server.middlewares.use((req, res, next) => {
        void handler(req, res, next)
      })
    },
  }
}
