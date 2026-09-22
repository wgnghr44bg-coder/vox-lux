export const config = { api: { bodyParser: true, responseLimit: false } }

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

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' })

  const key = process.env.XAI_API_KEY
  if (!key) return res.status(500).json({ error: 'XAI_API_KEY not configured' })

  const text = String(req.body?.text ?? req.body?.input ?? '').trim()
  if (!text) return res.status(400).json({ error: 'Missing text' })

  const upstream = await fetch('https://api.x.ai/v1/tts', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      voice_id: String(req.body?.voice_id || 'lux'),
      language: mapLanguage(req.body?.language),
      speed: clampSpeed(req.body?.speed),
    }),
  })

  if (!upstream.ok) {
    const detail = await upstream.text().catch(() => '')
    return res.status(502).json({ error: `xAI TTS ${upstream.status}`, detail: detail.slice(0, 200) })
  }

  const buf = Buffer.from(await upstream.arrayBuffer())
  res.setHeader('Content-Type', upstream.headers.get('content-type') || 'audio/mpeg')
  res.setHeader('Cache-Control', 'no-store')
  return res.status(200).send(buf)
}
