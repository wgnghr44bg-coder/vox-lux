/** Edge neural TTS (Lux stand-in) with Web Speech fallback */

export const LUX_EDGE_VOICE_EN = 'en-US-ChristopherNeural'
export const LUX_EDGE_VOICE_NL = 'nl-NL-MaartenNeural'
export const LUX_EDGE_VOICE_LABEL = 'Christopher (Edge)'

const FALLBACK_VOICES: Record<string, string> = {
  'en-US': LUX_EDGE_VOICE_EN,
  'en-GB': 'en-GB-RyanNeural',
  'nl-NL': LUX_EDGE_VOICE_NL,
  'nl-BE': 'nl-BE-ArnaudNeural',
  'de-DE': 'de-DE-ConradNeural',
  'fr-FR': 'fr-FR-HenriNeural',
  'es-ES': 'es-ES-AlvaroNeural',
}

const PREFERRED_NAME_PARTS = [
  'daniel',
  'thomas',
  'fred',
  'alex',
  'david',
  'mark',
  'james',
  'george',
  'reed',
  'rishi',
  'arthur',
  'aaron',
  'bruce',
  'ralph',
  'microsoft david',
  'microsoft mark',
  'microsoft guy',
  'google uk english male',
  'nl-nl',
  'dutch',
  'xander',
]

/** Convert UI rate (0.7–1.5) to Edge prosody rate string */
export function rateToEdgePercent(rate: number): string {
  const pct = Math.round((rate - 1) * 100)
  return pct >= 0 ? `+${pct}%` : `${pct}%`
}

export function resolveEdgeVoice(lang: string): string {
  if (!lang || lang === 'auto') return LUX_EDGE_VOICE_EN
  if (FALLBACK_VOICES[lang]) return FALLBACK_VOICES[lang]
  const prefix = lang.slice(0, 2).toLowerCase()
  const hit = Object.entries(FALLBACK_VOICES).find(([k]) =>
    k.toLowerCase().startsWith(prefix),
  )
  return hit?.[1] ?? LUX_EDGE_VOICE_EN
}

/** Strip / transform speech tags for Edge (XML is escaped by the service). */
export function stripForSpeech(script: string): string {
  return script
    .replace(/\[long pause\]/gi, '... ... ...')
    .replace(/\[pause\]/gi, '... ')
    .replace(/\[laugh\]/gi, ' ha. ')
    .replace(/<\/?(?:emphasis|whisper|slow|fast|soft)>/gi, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function scoreVoice(v: SpeechSynthesisVoice, lang: string): number {
  const name = v.name.toLowerCase()
  const vlang = v.lang.toLowerCase()
  let score = 0

  if (lang.startsWith('nl') && vlang.startsWith('nl')) score += 40
  else if (lang.startsWith('en') && vlang.startsWith('en')) score += 20
  else if (vlang.startsWith(lang.slice(0, 2))) score += 15

  for (const part of PREFERRED_NAME_PARTS) {
    if (name.includes(part)) score += 25
  }

  if (/(male|man|guy|bass|baritone)/i.test(name)) score += 15
  if (/(female|woman|zira|samantha|karen|moira|fiona)/i.test(name)) score -= 30
  if (v.localService) score += 5

  return score
}

export function pickLuxVoice(
  voices: SpeechSynthesisVoice[],
  lang: string,
): SpeechSynthesisVoice | null {
  if (!voices.length) return null
  const ranked = [...voices].sort(
    (a, b) => scoreVoice(b, lang) - scoreVoice(a, lang),
  )
  return ranked[0] ?? null
}

export function isSpeechSupported(): boolean {
  return typeof window !== 'undefined' && 'speechSynthesis' in window
}

export type SpeakOptions = {
  text: string
  lang: string
  rate: number
  pitch?: number
  onStart?: () => void
  onEnd?: () => void
  onError?: (err: string) => void
  onAudio?: (blob: Blob) => void
  onProgress?: (fraction: number, elapsedSec: number) => void
}

const CHUNK_TARGET = 2200

function chunkText(text: string): string[] {
  const cleaned = text.trim()
  if (!cleaned) return []
  if (cleaned.length <= CHUNK_TARGET) return [cleaned]

  const parts: string[] = []
  let rest = cleaned
  while (rest.length > CHUNK_TARGET) {
    const window = rest.slice(0, CHUNK_TARGET)
    let cut = window.lastIndexOf('\n\n')
    if (cut < CHUNK_TARGET * 0.4) cut = window.lastIndexOf('. ')
    if (cut < CHUNK_TARGET * 0.4) cut = window.lastIndexOf(' ')
    if (cut < CHUNK_TARGET * 0.4) cut = CHUNK_TARGET
    else if (rest.slice(cut, cut + 2) === '. ') cut += 2
    else if (rest.slice(cut, cut + 2) === '\n\n') cut += 2
    else cut += 1
    parts.push(rest.slice(0, cut).trim())
    rest = rest.slice(cut).trim()
  }
  if (rest) parts.push(rest)
  return parts.filter(Boolean)
}

function joinBase(path: string): string {
  const base = import.meta.env.BASE_URL || '/'
  const b = base.endsWith('/') ? base : `${base}/`
  const p = path.replace(/^\//, '')
  return `${b}${p}`
}

let cachedEndpoint: string | null = null

/** Public Edge TTS relay (OpenAI-compatible, CORS *) used when no local /api/tts. */
export const DEFAULT_EDGE_TTS_PROXY =
  'https://tts.reincarnatey.net/v1/audio/speech'

async function resolveTtsEndpoint(): Promise<string> {
  if (cachedEndpoint) return cachedEndpoint

  const envUrl = (import.meta.env.VITE_EDGE_TTS_URL as string | undefined)?.trim()
  if (envUrl) {
    cachedEndpoint = envUrl
    return envUrl
  }

  // Vite dev server always mounts the Edge middleware.
  if (import.meta.env.DEV) {
    cachedEndpoint = joinBase('api/tts')
    return cachedEndpoint
  }

  // Production static hosts (GitHub Pages): no /api/tts — use CORS relay.
  // Override with VITE_EDGE_TTS_URL (e.g. your Cloudflare Worker).
  if (import.meta.env.PROD) {
    cachedEndpoint = DEFAULT_EDGE_TTS_PROXY
    return cachedEndpoint
  }

  // vite preview / other: prefer local middleware if present
  const local = joinBase('api/tts')
  try {
    const ctrl = new AbortController()
    const timer = window.setTimeout(() => ctrl.abort(), 900)
    const res = await fetch(local, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'tts-1',
        input: 'ok',
        voice: LUX_EDGE_VOICE_EN,
        speed: 1,
      }),
      signal: ctrl.signal,
    })
    window.clearTimeout(timer)
    const ct = res.headers.get('content-type') || ''
    if (res.ok && ct.includes('audio')) {
      cachedEndpoint = local
      return local
    }
  } catch {
    /* no local middleware */
  }

  cachedEndpoint = DEFAULT_EDGE_TTS_PROXY
  return cachedEndpoint
}

async function fetchEdgeMp3Chunk(opts: {
  text: string
  voice: string
  rate: number
  endpoint: string
}): Promise<Blob> {
  const res = await fetch(opts.endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'tts-1',
      input: opts.text,
      voice: opts.voice,
      speed: opts.rate,
      // also accepted by our Vite middleware / DIY-style workers
      text: opts.text,
      rate: rateToEdgePercent(opts.rate),
      pitch: '-8Hz',
    }),
  })

  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new Error(
      `Edge TTS HTTP ${res.status}${detail ? `: ${detail.slice(0, 120)}` : ''}`,
    )
  }

  const ct = res.headers.get('content-type') || ''
  const buf = await res.arrayBuffer()
  if (!buf.byteLength) throw new Error('Lege audio-respons van Edge TTS')

  if (ct.includes('audio')) {
    return new Blob([buf], { type: ct.includes('mpeg') ? 'audio/mpeg' : ct })
  }
  // Some relays omit content-type; sniff MPEG frame sync
  const u8 = new Uint8Array(buf)
  const looksMp3 =
    (u8[0] === 0xff && (u8[1] & 0xe0) === 0xe0) ||
    (u8[0] === 0x49 && u8[1] === 0x44 && u8[2] === 0x33) // ID3
  if (looksMp3) return new Blob([buf], { type: 'audio/mpeg' })
  throw new Error('Antwoord was geen audio (CORS/proxy?)')
}

/** Synthesize full script to a single MP3-like Blob via Edge TTS. */
export async function synthesizeEdgeAudio(opts: {
  text: string
  lang: string
  rate: number
  signal?: AbortSignal
}): Promise<Blob> {
  const plain = stripForSpeech(opts.text)
  if (!plain) throw new Error('Geen tekst om voor te lezen.')

  const voice = resolveEdgeVoice(opts.lang)
  const endpoint = await resolveTtsEndpoint()
  const chunks = chunkText(plain)
  const blobs: Blob[] = []

  for (const chunk of chunks) {
    if (opts.signal?.aborted) throw new DOMException('Aborted', 'AbortError')
    blobs.push(
      await fetchEdgeMp3Chunk({
        text: chunk,
        voice,
        rate: opts.rate,
        endpoint,
      }),
    )
  }

  if (blobs.length === 1) return blobs[0]
  return new Blob(blobs, { type: 'audio/mpeg' })
}

export type SpeakHandle = {
  stop: () => void
  audioBlob?: Blob
}

/** Play Edge TTS audio; falls back to Web Speech on failure. */
export async function speakLux(opts: SpeakOptions): Promise<SpeakHandle> {
  let stopped = false
  let audioEl: HTMLAudioElement | null = null
  let objectUrl: string | null = null
  let abort: AbortController | null = new AbortController()
  let fallbackStop: (() => void) | null = null

  const cleanupAudio = () => {
    if (audioEl) {
      audioEl.onplay = null
      audioEl.onended = null
      audioEl.onerror = null
      audioEl.ontimeupdate = null
      audioEl.pause()
      audioEl.src = ''
      audioEl = null
    }
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl)
      objectUrl = null
    }
  }

  const stop = () => {
    stopped = true
    abort?.abort()
    abort = null
    fallbackStop?.()
    fallbackStop = null
    cleanupAudio()
  }

  try {
    const blob = await synthesizeEdgeAudio({
      text: opts.text,
      lang: opts.lang,
      rate: opts.rate,
      signal: abort.signal,
    })
    if (stopped) return { stop, audioBlob: blob }

    opts.onAudio?.(blob)

    objectUrl = URL.createObjectURL(blob)
    audioEl = new Audio(objectUrl)
    audioEl.preload = 'auto'

    audioEl.onplay = () => opts.onStart?.()
    audioEl.ontimeupdate = () => {
      if (!audioEl?.duration || !Number.isFinite(audioEl.duration)) return
      opts.onProgress?.(
        Math.min(1, audioEl.currentTime / audioEl.duration),
        audioEl.currentTime,
      )
    }
    audioEl.onended = () => {
      if (audioEl?.duration) {
        opts.onProgress?.(1, audioEl.duration)
      }
      opts.onEnd?.()
    }
    audioEl.onerror = () => {
      opts.onError?.('Afspelen van Edge-audio mislukt')
      opts.onEnd?.()
    }

    await audioEl.play()
    return { stop, audioBlob: blob }
  } catch (err) {
    if (stopped || (err instanceof DOMException && err.name === 'AbortError')) {
      return { stop }
    }

    const msg = err instanceof Error ? err.message : String(err)
    console.warn('[vox-lux] Edge TTS failed, falling back to Web Speech:', msg)

    fallbackStop = speakWithWebSpeech({
      ...opts,
      onError: (e) => opts.onError?.(e || msg),
    })
    return { stop }
  }
}

export function speakWithWebSpeech(opts: SpeakOptions): () => void {
  if (typeof window === 'undefined' || !window.speechSynthesis) {
    opts.onError?.('Web Speech API niet beschikbaar in deze browser.')
    return () => {}
  }

  const synth = window.speechSynthesis
  synth.cancel()

  const utter = new SpeechSynthesisUtterance(stripForSpeech(opts.text))
  utter.lang = opts.lang === 'auto' ? 'nl-NL' : opts.lang
  utter.rate = Math.min(1.5, Math.max(0.7, opts.rate * 0.92))
  utter.pitch = opts.pitch ?? 0.78
  utter.volume = 1

  const applyVoice = () => {
    const voices = synth.getVoices()
    const voice = pickLuxVoice(voices, utter.lang)
    if (voice) {
      utter.voice = voice
      if (!opts.lang || opts.lang === 'auto') utter.lang = voice.lang
    }
  }

  applyVoice()
  if (synth.getVoices().length === 0) {
    synth.addEventListener('voiceschanged', applyVoice, { once: true })
  }

  utter.onstart = () => opts.onStart?.()
  utter.onend = () => opts.onEnd?.()
  utter.onerror = (e) => {
    if (e.error === 'canceled' || e.error === 'interrupted') {
      opts.onEnd?.()
      return
    }
    opts.onError?.(e.error || 'Spraakfout')
    opts.onEnd?.()
  }

  setTimeout(() => synth.speak(utter), 20)

  return () => {
    synth.cancel()
  }
}
