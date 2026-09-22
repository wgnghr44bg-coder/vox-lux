/**
 * Cloudflare Worker: xAI Lux TTS proxy.
 * Secret: XAI_API_KEY (wrangler secret put XAI_API_KEY)
 * POST JSON { text|input, language?, speed?, voice_id? } -> audio/mpeg
 */

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  }
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

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() })
    }
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'POST only' }), {
        status: 405,
        headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
      })
    }

    const key = env.XAI_API_KEY
    if (!key) {
      return new Response(JSON.stringify({ error: 'XAI_API_KEY not configured' }), {
        status: 500,
        headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
      })
    }

    let body
    try {
      body = await request.json()
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
        status: 400,
        headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
      })
    }

    const text = String(body.text ?? body.input ?? '').trim()
    if (!text) {
      return new Response(JSON.stringify({ error: 'Missing text' }), {
        status: 400,
        headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
      })
    }

    const payload = {
      text,
      voice_id: String(body.voice_id || 'lux'),
      language: mapLanguage(body.language),
      speed: clampSpeed(body.speed),
    }

    const upstream = await fetch('https://api.x.ai/v1/tts', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!upstream.ok) {
      const detail = await upstream.text().catch(() => '')
      return new Response(
        JSON.stringify({
          error: `xAI TTS ${upstream.status}`,
          detail: detail.slice(0, 200),
        }),
        {
          status: 502,
          headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
        },
      )
    }

    const audio = await upstream.arrayBuffer()
    return new Response(audio, {
      status: 200,
      headers: {
        ...corsHeaders(),
        'Content-Type': upstream.headers.get('content-type') || 'audio/mpeg',
        'Cache-Control': 'no-store',
      },
    })
  },
}
