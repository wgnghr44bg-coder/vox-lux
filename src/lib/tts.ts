/** Official Grok Lux TTS via local/xAI proxy. No automatic Web Speech fallback. */

/** Soft old narrator Edge fallbacks (only when Lux server is unavailable). */
export const LUX_EDGE_VOICE_EN = 'en-US-RogerNeural'
export const LUX_EDGE_VOICE_NL = 'nl-NL-MaartenNeural'
export const LUX_EDGE_VOICE_LABEL = 'Edge: Roger'
/** Deep pitch for warm elderly narrator. */
export const LUX_EDGE_PITCH = '-40Hz'

/**
 * Roger is the warmest free Edge US male for “old soft documentary” delivery.
 * Not Grok Lux and not a celebrity clone — best free approximation.
 */
export const LUX_EDGE_VOICE_NOTE =
  'Default en-US-RogerNeural (soft old narrator). Alts: Steffan, Guy, Christopher.'

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

/**
 * Map UI tempo (0.7–1.5) → Edge playback speed.
 * Soft old-narrator pacing: UI 0.7 → Edge 0.72; UI 1.5 → Edge 1.25.
 */
export function uiRateToEdgeSpeed(uiRate: number): number {
  const lo = 0.7
  const hi = 1.5
  const edgeLo = 0.72
  const edgeHi = 1.25
  const t = (Math.min(hi, Math.max(lo, uiRate)) - lo) / (hi - lo)
  return edgeLo + t * (edgeHi - edgeLo)
}

/** Convert UI rate (0.7–1.5) to Edge prosody rate string (after Lux timing remap). */
export function rateToEdgePercent(rate: number): string {
  const edge = uiRateToEdgeSpeed(rate)
  const pct = Math.round((edge - 1) * 100)
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

/** Map UI language codes to xAI TTS language values. */
export function mapLanguageForXai(lang: string): string {
  const value = (lang || '').toLowerCase()
  if (value === 'nl' || value === 'nl-nl' || value.startsWith('nl')) return 'nl'
  if (value === 'auto') return 'auto'
  if (value === 'en' || value === 'en-us' || value === 'en-gb' || value.startsWith('en')) {
    return 'en'
  }
  return 'en'
}

export function clampLuxSpeed(rate: number): number {
  return Math.min(1.5, Math.max(0.7, Number.isFinite(rate) ? rate : 0.7))
}

/** Short toast label when Lux MP3 starts playing. */
export function luxToastLabel(_lang?: string): string {
  return 'Lux (xAI)'
}

/** @deprecated Prefer luxToastLabel — kept for older imports. */
export function edgeToastLabel(lang: string): string {
  return luxToastLabel(lang)
}

/**
 * Prepare script for official xAI Lux — keep speech tags and pause markers.
 * xAI understands <slow>, <soft>, [pause], [long-pause], etc.
 */
export function prepareForXaiSpeech(script: string): string {
  return script
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

/** Strip / transform speech tags for Edge (XML is escaped by the service). */
export function stripForSpeech(script: string): string {
  return script
    // Slower Lux pacing: keep audible gaps without molasses.
    .replace(/\[long[- ]pause\]/gi, '... ... ')
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

export type SpeakStartMeta = {
  engine: 'xai' | 'edge'
  label: string
}

export type SpeakOptions = {
  text: string
  lang: string
  rate: number
  pitch?: number
  onStart?: (meta?: SpeakStartMeta) => void
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
let cachedIsXai = true

function forceXaiOnly(): boolean {
  return String(import.meta.env.VITE_FORCE_XAI || '') === '1'
}

function envTtsUrl(): string {
  return (
    (import.meta.env.VITE_TTS_URL as string | undefined)?.trim() ||
    (import.meta.env.VITE_EDGE_TTS_URL as string | undefined)?.trim() ||
    ''
  )
}

/** Prefer VITE_TTS_URL (Cloudflare Worker) on Pages; same-origin only when it is really our Lux API. */
export async function resolveTtsEndpoint(): Promise<{
  url: string
  xai: boolean
}> {
  if (cachedEndpoint) return { url: cachedEndpoint, xai: cachedIsXai }

  const local = joinBase('api/tts')
  const remote = envTtsUrl()

  // GitHub Pages answers OPTIONS /api/tts with bare 405 — that is NOT our Lux server.
  // When a permanent Worker URL is baked in, use it first.
  if (remote) {
    cachedEndpoint = remote
    cachedIsXai = true
    return { url: remote, xai: true }
  }

  // Local `npm start` / Vite middleware: require CORS headers from our proxy.
  try {
    const ctrl = new AbortController()
    const timer = window.setTimeout(() => ctrl.abort(), 1200)
    const res = await fetch(local, {
      method: 'OPTIONS',
      signal: ctrl.signal,
    })
    window.clearTimeout(timer)
    const acao = res.headers.get('access-control-allow-origin')
    const methods = (res.headers.get('access-control-allow-methods') || '').toUpperCase()
    const looksLikeLuxProxy =
      Boolean(acao) &&
      methods.includes('POST') &&
      (res.ok || res.status === 204 || res.status === 405)
    if (looksLikeLuxProxy) {
      cachedEndpoint = local
      cachedIsXai = true
      return { url: local, xai: true }
    }
  } catch {
    /* same-origin Lux server offline */
  }

  if (forceXaiOnly() || import.meta.env.PROD) {
    throw new Error('Lux-server offline')
  }

  // Dev-only last resort: Vite middleware may still serve Edge without a key.
  cachedEndpoint = local
  cachedIsXai = false
  return { url: local, xai: false }
}

function looksLikeMp3(buf: ArrayBuffer): boolean {
  const u8 = new Uint8Array(buf)
  return (
    (u8[0] === 0xff && (u8[1] & 0xe0) === 0xe0) ||
    (u8[0] === 0x49 && u8[1] === 0x44 && u8[2] === 0x33)
  )
}

async function fetchLuxMp3Chunk(opts: {
  text: string
  lang: string
  rate: number
  endpoint: string
  xai: boolean
}): Promise<Blob> {
  const body = opts.xai
    ? {
        text: opts.text,
        voice_id: 'lux',
        language: mapLanguageForXai(opts.lang),
        speed: clampLuxSpeed(opts.rate),
      }
    : {
        model: 'tts-1',
        input: stripForSpeech(opts.text),
        voice: resolveEdgeVoice(opts.lang),
        speed: uiRateToEdgeSpeed(opts.rate),
        text: stripForSpeech(opts.text),
        rate: rateToEdgePercent(opts.rate),
        pitch: LUX_EDGE_PITCH,
      }

  const res = await fetch(opts.endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    if (res.status === 404) throw new Error('Lux-server offline')
    throw new Error(
      `Lux TTS HTTP ${res.status}${detail ? `: ${detail.slice(0, 120)}` : ''}`,
    )
  }

  const ct = res.headers.get('content-type') || ''
  const buf = await res.arrayBuffer()
  if (!buf.byteLength) throw new Error('Lege audio-respons van Lux TTS')

  if (ct.includes('audio')) {
    return new Blob([buf], { type: ct.includes('mpeg') ? 'audio/mpeg' : ct })
  }
  if (looksLikeMp3(buf)) return new Blob([buf], { type: 'audio/mpeg' })
  throw new Error('Antwoord was geen audio (Lux-server?)')
}

/** Synthesize full script to a single MP3-like Blob via Lux (xAI) server. */
export async function synthesizeLuxAudio(opts: {
  text: string
  lang: string
  rate: number
  signal?: AbortSignal
}): Promise<{ blob: Blob; engine: 'xai' | 'edge' }> {
  const prepared = prepareForXaiSpeech(opts.text)
  if (!prepared) throw new Error('Geen tekst om voor te lezen.')

  let endpoint: string
  let xai: boolean
  try {
    ;({ url: endpoint, xai } = await resolveTtsEndpoint())
  } catch (err) {
    throw err instanceof Error ? err : new Error('Lux-server offline')
  }

  const source = xai ? prepared : stripForSpeech(prepared)
  const chunks = chunkText(source)
  const blobs: Blob[] = []

  for (const chunk of chunks) {
    if (opts.signal?.aborted) throw new DOMException('Aborted', 'AbortError')
    blobs.push(
      await fetchLuxMp3Chunk({
        text: chunk,
        lang: opts.lang,
        rate: opts.rate,
        endpoint,
        xai,
      }),
    )
  }

  const blob =
    blobs.length === 1 ? blobs[0] : new Blob(blobs, { type: 'audio/mpeg' })
  return { blob, engine: xai ? 'xai' : 'edge' }
}

/** @deprecated Prefer synthesizeLuxAudio. */
export async function synthesizeEdgeAudio(opts: {
  text: string
  lang: string
  rate: number
  signal?: AbortSignal
}): Promise<Blob> {
  const { blob } = await synthesizeLuxAudio(opts)
  return blob
}

export type SpeakHandle = {
  stop: () => void
  audioBlob?: Blob
}

// --- iOS / Safari audio unlock ---------------------------------------------

type WebkitWindow = Window & {
  webkitAudioContext?: typeof AudioContext
}

let sharedAudioCtx: AudioContext | null = null
let unlockPrimed = false

/** Tiny silent WAV (data URI) — starts under user gesture so later play() works. */
const SILENT_WAV =
  'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA'

/**
 * Call synchronously from a click/tap handler (Sample / Voorproef / Full)
 * before any await. Resumes AudioContext and primes an HTMLAudioElement so
 * iOS still allows play() after the network TTS round-trip.
 */
export function unlockAudioForPlayback(): void {
  if (typeof window === 'undefined') return

  try {
    const W = window as WebkitWindow
    const AC = window.AudioContext || W.webkitAudioContext
    if (AC) {
      if (!sharedAudioCtx) sharedAudioCtx = new AC()
      if (sharedAudioCtx.state === 'suspended') {
        void sharedAudioCtx.resume()
      }
    }
  } catch {
    /* ignore */
  }

  if (unlockPrimed) return
  try {
    const a = new Audio(SILENT_WAV)
    a.muted = true
    a.setAttribute('playsinline', 'true')
    ;(a as HTMLAudioElement & { playsInline?: boolean }).playsInline = true
    const p = a.play()
    if (p && typeof p.then === 'function') {
      void p
        .then(() => {
          a.pause()
          a.src = ''
          unlockPrimed = true
        })
        .catch(() => {
          /* still try later play on real blob */
        })
    } else {
      unlockPrimed = true
    }
  } catch {
    /* ignore */
  }
}

function armPlaybackElement(): HTMLAudioElement {
  const el = new Audio()
  el.preload = 'auto'
  el.setAttribute('playsinline', 'true')
  ;(el as HTMLAudioElement & { playsInline?: boolean }).playsInline = true
  // Start muted silent clip inside the gesture stack so Safari "unlocks" this element.
  el.muted = true
  el.src = SILENT_WAV
  try {
    void el.play().catch(() => {})
  } catch {
    /* ignore */
  }
  return el
}

function getSharedAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null
  try {
    const W = window as WebkitWindow
    const AC = window.AudioContext || W.webkitAudioContext
    if (!AC) return null
    if (!sharedAudioCtx) sharedAudioCtx = new AC()
    return sharedAudioCtx
  } catch {
    return null
  }
}

/** Play an MP3 blob via Web Audio (best after iOS unlock) or HTMLAudio fallback. */
export async function playAudioBlob(
  blob: Blob,
  opts: {
    signal?: AbortSignal
    onStart?: () => void
    onEnd?: () => void
    onProgress?: (fraction: number, elapsedSec: number) => void
    onError?: (msg: string) => void
  } = {},
): Promise<() => void> {
  const ctx = getSharedAudioContext()
  if (ctx) {
    try {
      if (ctx.state === 'suspended') await ctx.resume()
      const raw = await blob.arrayBuffer()
      if (opts.signal?.aborted) return () => {}
      const buffer = await ctx.decodeAudioData(raw.slice(0))
      if (opts.signal?.aborted) return () => {}

      const source = ctx.createBufferSource()
      source.buffer = buffer
      source.connect(ctx.destination)

      let raf = 0
      const startedAt = ctx.currentTime
      const tick = () => {
        const t = Math.max(0, ctx.currentTime - startedAt)
        const dur = buffer.duration || 1
        opts.onProgress?.(Math.min(1, t / dur), t)
        if (t < dur) raf = window.requestAnimationFrame(tick)
      }

      source.onended = () => {
        window.cancelAnimationFrame(raf)
        opts.onProgress?.(1, buffer.duration)
        opts.onEnd?.()
      }

      source.start(0)
      opts.onStart?.()
      raf = window.requestAnimationFrame(tick)

      return () => {
        window.cancelAnimationFrame(raf)
        try {
          source.stop()
        } catch {
          /* already stopped */
        }
        try {
          source.disconnect()
        } catch {
          /* ignore */
        }
      }
    } catch (err) {
      console.warn('[vox-lux] Web Audio play failed, trying HTMLAudio:', err)
    }
  }

  // HTMLAudio fallback
  const el = new Audio()
  el.preload = 'auto'
  el.setAttribute('playsinline', 'true')
  ;(el as HTMLAudioElement & { playsInline?: boolean }).playsInline = true
  const url = URL.createObjectURL(blob)
  el.src = url
  el.onplay = () => opts.onStart?.()
  el.ontimeupdate = () => {
    if (!el.duration || !Number.isFinite(el.duration)) return
    opts.onProgress?.(Math.min(1, el.currentTime / el.duration), el.currentTime)
  }
  el.onended = () => {
    opts.onProgress?.(1, el.duration || 0)
    opts.onEnd?.()
    URL.revokeObjectURL(url)
  }
  el.onerror = () => {
    opts.onError?.('Afspelen mislukt')
    opts.onEnd?.()
    URL.revokeObjectURL(url)
  }
  try {
    await el.play()
  } catch (playErr) {
    URL.revokeObjectURL(url)
    const detail = playErr instanceof Error ? playErr.message : String(playErr)
    opts.onError?.(`Afspelen geblokkeerd (${detail})`)
    opts.onEnd?.()
    return () => {}
  }
  return () => {
    el.pause()
    el.removeAttribute('src')
    el.load()
    URL.revokeObjectURL(url)
  }
}

/** Play Lux (xAI) audio. On failure: onError + onEnd — never Web Speech. */
export async function speakLux(opts: SpeakOptions): Promise<SpeakHandle> {
  let stopped = false
  let abort: AbortController | null = new AbortController()
  let stopPlayback: (() => void) | null = null

  // Must run before any await — keeps (or re-establishes) iOS user-gesture unlock.
  unlockAudioForPlayback()
  armPlaybackElement()

  const stop = () => {
    stopped = true
    abort?.abort()
    abort = null
    stopPlayback?.()
    stopPlayback = null
  }

  const fail = (msg: string) => {
    opts.onError?.(msg)
    opts.onEnd?.()
  }

  try {
    const { blob, engine } = await synthesizeLuxAudio({
      text: opts.text,
      lang: opts.lang,
      rate: opts.rate,
      signal: abort?.signal,
    })
    if (stopped) return { stop, audioBlob: blob }

    opts.onAudio?.(blob)

    const label = luxToastLabel(opts.lang)
    let playFailed = false

    stopPlayback = await playAudioBlob(blob, {
      signal: abort?.signal,
      onStart: () => opts.onStart?.({ engine, label }),
      onProgress: opts.onProgress,
      onEnd: () => opts.onEnd?.(),
      onError: (msg) => {
        playFailed = true
        // Blob is still valid for Download MP3 / transport replay.
        opts.onError?.(
          `${msg}. Audio staat klaar — tik ▶ of Download MP3.`,
        )
        opts.onEnd?.()
      },
    })

    if (stopped) {
      stopPlayback?.()
      return { stop, audioBlob: blob }
    }

    // If HTML/WebAudio path reported error via onError, still return blob.
    if (playFailed) return { stop, audioBlob: blob }

    return { stop, audioBlob: blob }
  } catch (err) {
    if (stopped || (err instanceof DOMException && err.name === 'AbortError')) {
      return { stop }
    }

    const msg = err instanceof Error ? err.message : String(err)
    console.warn('[vox-lux] Lux TTS failed (no Web Speech fallback):', msg)
    fail(
      msg.includes('Lux-server offline')
        ? 'Lux-server offline'
        : msg.startsWith('Lux TTS HTTP')
          ? msg
          : 'Lux-stem mislukt — geen robot-fallback',
    )
    return { stop }
  }
}

/**
 * Manual Web Speech helper — NOT used by speakLux.
 * Kept for diagnostics only; do not wire as automatic fallback.
 */
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
