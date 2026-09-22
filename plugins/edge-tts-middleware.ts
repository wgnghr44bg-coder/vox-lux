import type { IncomingMessage, ServerResponse } from 'node:http'
import { readFileSync } from 'node:fs'
import type { Plugin } from 'vite'
import { EdgeTTS } from 'edge-tts-universal'

const SECRETS_CANDIDATES = ['/home/box/sand-data/box-secrets.json','/home/box/agent-data/box-secrets.json']

function loadXaiApiKey(): string {
  if (process.env.XAI_API_KEY?.trim()) return process.env.XAI_API_KEY.trim()
  for (const file of SECRETS_CANDIDATES) {
    try {
      const secrets = JSON.parse(readFileSync(file, 'utf8')) as {
        card?: { XAI_API_KEY?: string }
      }
      const key = secrets?.card?.XAI_API_KEY
      if (typeof key === 'string' && key.trim()) return key.trim()
    } catch {
      /* next */
    }
  }
  return ''
}

function mapLanguage(value: unknown): string {
  const lang = String(value ?? '').toLowerCase()
  if (lang === 'nl' || lang === 'nl-nl') return 'nl'
  if (lang === 'auto') return 'auto'
  return 'en'
}

function clampSpeed(value: unknown, fallback = 0.7): number {
  const speed = Number(value)
  return Number.isFinite(speed) ? Math.min(1.5, Math.max(0.7, speed)) : fallback
}

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

async function synthesizeXai(
  text: string,
  language: string,
  speed: number,
  apiKey: string,
): Promise<Buffer> {
  const upstream = await fetch('https://api.x.ai/v1/tts', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      voice_id: 'lux',
      language,
      speed,
    }),
  })
  const audio = Buffer.from(await upstream.arrayBuffer())
  if (!upstream.ok) {
    throw new Error(`xAI TTS HTTP ${upstream.status}`)
  }
  return audio
}

/**
 * Local / preview TTS endpoint at /api/tts (and under base).
 * Prefers official xAI Lux when a key is available; otherwise Edge.
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
      if (!text) {
        res.statusCode = 400
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ error: 'Missing text/input' }))
        return
      }

      const voiceId = String(body.voice_id ?? body.voice ?? '').toLowerCase()
      const preferLux = !voiceId || voiceId === 'lux' || voiceId.includes('lux')
      const apiKey = preferLux ? loadXaiApiKey() : ''

      if (apiKey) {
        const language = mapLanguage(body.language ?? body.lang)
        const speed = clampSpeed(body.speed, 0.7)
        const buf = await synthesizeXai(text, language, speed, apiKey)
        res.statusCode = 200
        res.setHeader('Content-Type', 'audio/mpeg')
        res.setHeader('Cache-Control', 'no-store')
        res.end(buf)
        return
      }

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
