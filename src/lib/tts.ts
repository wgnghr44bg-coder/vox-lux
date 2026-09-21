/** Prefer older / lower male browser voices for Lux character */

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

export function stripForSpeech(script: string): string {
  return script
    .replace(/\[long pause\]/gi, '... ... ...')
    .replace(/\[pause\]/gi, '... ')
    .replace(/\[laugh\]/gi, ' ha. ')
    .replace(/<\/?(?:emphasis|whisper|slow|fast|soft)>/gi, '')
    .replace(/\s+/g, ' ')
    .trim()
}

export type SpeakOptions = {
  text: string
  lang: string
  rate: number
  pitch?: number
  onStart?: () => void
  onEnd?: () => void
  onError?: (err: string) => void
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
  utter.rate = Math.min(1.5, Math.max(0.7, opts.rate * 0.92)) // Lux: slightly slower
  utter.pitch = opts.pitch ?? 0.78 // lower for old-man character
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

  // Chrome sometimes needs a tick after cancel
  setTimeout(() => synth.speak(utter), 20)

  return () => {
    synth.cancel()
  }
}

export function isSpeechSupported(): boolean {
  return typeof window !== 'undefined' && 'speechSynthesis' in window
}
