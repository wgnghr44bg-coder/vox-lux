/**
 * Optional Cloudflare Worker — deploy and set VITE_EDGE_TTS_URL to its /v1/audio/speech.
 * OpenAI-compatible Edge TTS proxy (no API key). Browser cannot talk to Edge WS directly.
 *
 * Deploy: paste into Workers dashboard, or `npx wrangler deploy` with a wrangler.toml.
 *
 * Based on the public Edge Read Aloud WebSocket protocol (same as edge-tts / DIYgod).
 */

const TRUSTED_CLIENT_TOKEN = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
const SYNTH_URL =
  `wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=${TRUSTED_CLIENT_TOKEN}`

function uuid() {
  return crypto.randomUUID().replace(/-/g, '')
}

function escapeXml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

function rateToPercent(speed) {
  const pct = Math.round((Number(speed) - 1) * 100)
  return pct >= 0 ? `+${pct}%` : `${pct}%`
}

function cors(res, origin = '*') {
  const headers = new Headers(res.headers)
  headers.set('Access-Control-Allow-Origin', origin)
  headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  return new Response(res.body, { status: res.status, headers })
}

async function synthesize(text, voice, rate, pitch) {
  const url = `${SYNTH_URL}&ConnectionId=${uuid()}`
  const resp = await fetch(url, {
    headers: {
      Upgrade: 'websocket',
      'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
      Origin: 'chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold',
    },
  })
  const ws = resp.webSocket
  if (!ws) throw new Error('WebSocket upgrade failed')
  ws.accept()

  const chunks = []
  const done = new Promise((resolve, reject) => {
    ws.addEventListener('message', (event) => {
      if (typeof event.data === 'string') {
        if (event.data.includes('Path:turn.end')) {
          resolve()
        }
        return
      }
      const data = new Uint8Array(event.data)
      // header length is first 2 bytes big-endian
      const headerLen = (data[0] << 8) | data[1]
      chunks.push(data.slice(headerLen + 2))
    })
    ws.addEventListener('error', () => reject(new Error('WS error')))
    ws.addEventListener('close', () => resolve())
  })

  const configMsg =
    `X-Timestamp:${new Date().toString()}\r\n` +
    `Content-Type:application/json; charset=utf-8\r\n` +
    `Path:speech.config\r\n\r\n` +
    `{"context":{"synthesis":{"audio":{"metadataoptions":{"sentenceBoundaryEnabled":"false","wordBoundaryEnabled":"false"},"outputFormat":"audio-24khz-48kbitrate-mono-mp3"}}}}\r\n`

  const ssml =
    `<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>` +
    `<voice name='${voice}'>` +
    `<prosody pitch='${pitch}' rate='${rate}' volume='+0%'>${escapeXml(text)}</prosody>` +
    `</voice></speak>`

  const ssmlMsg =
    `X-RequestId:${uuid()}\r\n` +
    `Content-Type:application/ssml+xml\r\n` +
    `X-Timestamp:${new Date().toString()}\r\n` +
    `Path:ssml\r\n\r\n` +
    ssml

  ws.send(configMsg)
  ws.send(ssmlMsg)
  await done
  ws.close()

  const total = chunks.reduce((n, c) => n + c.length, 0)
  const out = new Uint8Array(total)
  let off = 0
  for (const c of chunks) {
    out.set(c, off)
    off += c.length
  }
  if (!out.length) throw new Error('No audio received')
  return out
}

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return cors(new Response(null, { status: 204 }))
    }

    const url = new URL(request.url)
    if (url.pathname === '/health') {
      return cors(Response.json({ ok: true }))
    }

    const isSpeech =
      url.pathname === '/v1/audio/speech' ||
      url.pathname === '/tts' ||
      url.pathname.endsWith('/v1/audio/speech')

    if (request.method === 'POST' && isSpeech) {
      try {
        const body = await request.json()
        const text = String(body.input ?? body.text ?? '').trim()
        const voice = String(body.voice || 'en-US-ChristopherNeural')
        const speed = typeof body.speed === 'number' ? body.speed : 1
        const rate =
          typeof body.rate === 'string' ? body.rate : rateToPercent(speed)
        const pitch =
          typeof body.pitch === 'string' && body.pitch.includes('Hz')
            ? body.pitch
            : '-8Hz'
        if (!text) {
          return cors(Response.json({ error: 'Missing text' }, { status: 400 }))
        }
        const audio = await synthesize(text, voice, rate, pitch)
        return cors(
          new Response(audio, {
            headers: { 'Content-Type': 'audio/mpeg', 'Cache-Control': 'no-store' },
          }),
        )
      } catch (err) {
        return cors(
          Response.json(
            { error: err instanceof Error ? err.message : String(err) },
            { status: 502 },
          ),
        )
      }
    }

    return cors(new Response('Not found', { status: 404 }))
  },
}
