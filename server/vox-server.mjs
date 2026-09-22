import { createServer } from 'node:http'
import { readFile, stat } from 'node:fs/promises'
import { readFileSync } from 'node:fs'
import { dirname, extname, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const HOST = '127.0.0.1'
const PORT = 8788
const DIST_DIR = resolve(dirname(fileURLToPath(import.meta.url)), '../dist')
const SECRETS_CANDIDATES = [
  '/home/box/sand-data/box-secrets.json',
  '/home/box/agent-data/box-secrets.json',
]
const MAX_BODY_BYTES = 1_000_000

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.txt': 'text/plain; charset=utf-8',
}

function loadXaiApiKey() {
  if (process.env.XAI_API_KEY?.trim()) return process.env.XAI_API_KEY.trim()
  for (const file of SECRETS_CANDIDATES) {
    try {
      const secrets = JSON.parse(readFileSync(file, 'utf8'))
      const key = secrets?.card?.XAI_API_KEY
      if (typeof key === 'string' && key.trim()) return key.trim()
    } catch {
      /* try next */
    }
  }
  return ''
}

function mapLanguage(value) {
  const lang = String(value ?? '').toLowerCase()
  if (lang === 'nl' || lang === 'nl-nl') return 'nl'
  if (lang === 'auto') return 'auto'
  return 'en'
}

function clampSpeed(value) {
  const speed = Number(value)
  return Number.isFinite(speed) ? Math.min(1.5, Math.max(0.7, speed)) : 0.7
}

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
}

function sendJson(res, status, body) {
  const data = Buffer.from(JSON.stringify(body))
  res.statusCode = status
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.setHeader('Content-Length', data.length)
  res.end(data)
}

async function readJsonBody(req) {
  const chunks = []
  let length = 0
  for await (const chunk of req) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)
    length += buffer.length
    if (length > MAX_BODY_BYTES) throw new Error('BODY_TOO_LARGE')
    chunks.push(buffer)
  }
  const raw = Buffer.concat(chunks).toString('utf8')
  return raw.trim() ? JSON.parse(raw) : {}
}

async function handleTts(req, res) {
  setCors(res)
  if (req.method === 'OPTIONS') {
    res.statusCode = 204
    res.end()
    return
  }
  if (req.method !== 'POST') {
    sendJson(res, 405, { error: 'POST only' })
    console.log('[tts] status=405 bytes=0')
    return
  }

  let body
  try {
    body = await readJsonBody(req)
  } catch {
    sendJson(res, 400, { error: 'Invalid JSON body' })
    console.log('[tts] status=400 bytes=0')
    return
  }

  const text = String(body.text ?? body.input ?? '').trim()
  if (!text) {
    sendJson(res, 400, { error: 'Missing text/input' })
    console.log('[tts] status=400 bytes=0')
    return
  }

  const apiKey = loadXaiApiKey()
  if (!apiKey) {
    sendJson(res, 503, { error: 'Lux server is not configured' })
    console.log('[tts] status=503 bytes=0')
    return
  }

  try {
    const upstream = await fetch('https://api.x.ai/v1/tts', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice_id: 'lux',
        language: mapLanguage(body.language),
        speed: clampSpeed(body.speed),
      }),
    })
    const audio = Buffer.from(await upstream.arrayBuffer())

    if (!upstream.ok) {
      sendJson(res, 502, { error: 'xAI TTS request failed', upstream_status: upstream.status })
      console.log(`[tts] status=${upstream.status} bytes=${audio.length}`)
      return
    }

    res.statusCode = 200
    res.setHeader('Content-Type', 'audio/mpeg')
    res.setHeader('Content-Length', audio.length)
    res.setHeader('Cache-Control', 'no-store')
    res.end(audio)
    console.log(`[tts] status=200 bytes=${audio.length}`)
  } catch {
    sendJson(res, 502, { error: 'xAI TTS unavailable' })
    console.log('[tts] status=502 bytes=0')
  }
}

async function serveStatic(pathname, res) {
  if (!pathname.startsWith('/vox-lux/')) return false

  let relative
  try {
    relative = decodeURIComponent(pathname.slice('/vox-lux/'.length))
  } catch {
    sendJson(res, 400, { error: 'Invalid URL' })
    return true
  }
  if (!relative || relative.endsWith('/')) relative += 'index.html'

  const filePath = resolve(DIST_DIR, relative)
  if (filePath !== DIST_DIR && !filePath.startsWith(`${DIST_DIR}${sep}`)) {
    sendJson(res, 403, { error: 'Forbidden' })
    return true
  }

  try {
    const info = await stat(filePath)
    if (!info.isFile()) throw new Error('NOT_FILE')
    const data = await readFile(filePath)
    res.statusCode = 200
    res.setHeader('Content-Type', MIME_TYPES[extname(filePath).toLowerCase()] || 'application/octet-stream')
    res.setHeader('Content-Length', data.length)
    res.end(data)
  } catch {
    sendJson(res, 404, { error: 'Not found' })
  }
  return true
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url || '/', `http://${HOST}:${PORT}`)
  const pathname = url.pathname

  if (pathname === '/') {
    res.statusCode = 302
    res.setHeader('Location', '/vox-lux/')
    res.end()
    return
  }

  if (pathname === '/api/tts' || pathname === '/vox-lux/api/tts') {
    await handleTts(req, res)
    return
  }

  if (req.method === 'GET' || req.method === 'HEAD') {
    if (await serveStatic(pathname, res)) return
  }

  sendJson(res, 404, { error: 'Not found' })
})

server.listen(PORT, HOST, () => {
  console.log(`[vox-server] status=ready port=${PORT}`)
})
