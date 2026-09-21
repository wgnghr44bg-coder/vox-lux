import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Header } from './components/Header'
import { ScriptEditor } from './components/ScriptEditor'
import { ScriptsPanel } from './components/ScriptsPanel'
import { Transport } from './components/Transport'
import { VoicePanel } from './components/VoicePanel'
import {
  DEFAULT_SCRIPT,
  type ExampleScript,
} from './data/examples'
import { downloadText, slugifyTitle } from './lib/download'
import { estimateSeconds, formatDuration } from './lib/stats'
import {
  isSpeechSupported,
  speakWithWebSpeech,
  stripForSpeech,
} from './lib/tts'

type MobileTab = 'script' | 'stem' | 'projecten'

const SAMPLE_LINE =
  'Lux. Oude, kalme documentaire-stem. Alsof hij naast je bed een verhaal voorleest.'

export default function App() {
  const [script, setScript] = useState(DEFAULT_SCRIPT)
  const [lang, setLang] = useState('nl-NL')
  const [rate, setRate] = useState(1)
  const [speaking, setSpeaking] = useState(false)
  const [progress, setProgress] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [activeLabel, setActiveLabel] = useState('Voorbeeld')
  const [mobileTab, setMobileTab] = useState<MobileTab>('script')
  const [toast, setToast] = useState<string | null>(null)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)

  const stopRef = useRef<(() => void) | null>(null)
  const tickRef = useRef<number | null>(null)
  const durationRef = useRef(0)

  const totalSeconds = useMemo(
    () => estimateSeconds(script, rate),
    [script, rate],
  )

  const activeTitle = useMemo(() => {
    const line = script.split('\n').find((l) => l.trim())
    if (!line) return 'Leeg script'
    return stripForSpeech(line).slice(0, 42) || 'Leeg script'
  }, [script])

  const clearTicker = () => {
    if (tickRef.current != null) {
      window.clearInterval(tickRef.current)
      tickRef.current = null
    }
  }

  const stopSpeech = useCallback(() => {
    stopRef.current?.()
    stopRef.current = null
    clearTicker()
    setSpeaking(false)
    setProgress(0)
    setElapsed(0)
  }, [])

  useEffect(() => () => stopSpeech(), [stopSpeech])

  const showToast = (msg: string) => {
    setToast(msg)
    window.setTimeout(() => setToast(null), 3200)
  }

  const startTicker = (seconds: number) => {
    clearTicker()
    durationRef.current = Math.max(1, seconds)
    const start = performance.now()
    tickRef.current = window.setInterval(() => {
      const t = (performance.now() - start) / 1000
      setElapsed(t)
      setProgress(Math.min(1, t / durationRef.current))
    }, 80)
  }

  const speak = useCallback(
    (text: string, full = false) => {
      if (speaking) {
        stopSpeech()
        return
      }

      if (!text.trim()) {
        showToast('Schrijf eerst een script.')
        return
      }

      if (!isSpeechSupported()) {
        showToast('Web Speech API niet beschikbaar — mock preview.')
        setSpeaking(true)
        const secs = Math.min(
          full ? estimateSeconds(text, rate) : 8,
          full ? 120 : 12,
        )
        startTicker(secs)
        window.setTimeout(() => {
          setSpeaking(false)
          clearTicker()
          setProgress(1)
          setElapsed(secs)
        }, secs * 1000)
        return
      }

      const previewText = full
        ? text
        : text.split(/\n\n+/)[0]?.slice(0, 420) || text.slice(0, 420)

      const secs = estimateSeconds(previewText, rate) || 4
      startTicker(secs)

      stopRef.current = speakWithWebSpeech({
        text: previewText,
        lang,
        rate,
        onStart: () => setSpeaking(true),
        onEnd: () => {
          clearTicker()
          setSpeaking(false)
          setProgress(1)
        },
        onError: (err) => {
          showToast(`Spraak: ${err}`)
          stopSpeech()
        },
      })
      setSpeaking(true)
    },
    [speaking, stopSpeech, rate, lang],
  )

  const onNew = () => {
    stopSpeech()
    setScript('')
    setActiveLabel('Nieuw')
    setAudioBlob(null)
    setProgress(0)
    setElapsed(0)
    setMobileTab('script')
  }

  const onSelectExample = (ex: ExampleScript) => {
    stopSpeech()
    setScript(ex.script)
    setActiveLabel(ex.title)
    setAudioBlob(null)
    setProgress(0)
    setElapsed(0)
    setMobileTab('script')
  }

  const onPrepareSpeech = () => {
    // Light cleanup: ensure blank lines between paragraphs, keep tags
    const cleaned = script
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim()
    setScript(cleaned ? cleaned + '\n' : '')
    showToast('Script opgeschoond voor spraak.')
  }

  const onDownloadScript = () => {
    const name = `${slugifyTitle(script) || 'vox-script'}.txt`
    downloadText(name, script)
    showToast(`Script gedownload: ${name}`)
  }

  const onDownloadAudio = () => {
    if (!audioBlob) {
      showToast(
        'Geen audio-bestand. Web Speech kan geen MP3 exporteren — download wel je script.',
      )
      return
    }
    const url = URL.createObjectURL(audioBlob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${slugifyTitle(script) || 'vox-lux'}.webm`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Attempt MediaRecorder capture of system/mic is out of scope;
  // keep audioBlob null so Download MP3 stays clearly disabled unless set.
  useEffect(() => {
    setAudioBlob(null)
  }, [script, lang, rate])

  return (
    <div className="grid h-dvh grid-cols-1 grid-rows-[auto_minmax(0,1fr)_auto_auto] bg-bg text-fg md:grid-cols-[15rem_minmax(0,1fr)_20rem] lg:grid-cols-[16rem_minmax(0,1fr)_24rem]">
      <Header onNew={onNew} onPrepareSpeech={onPrepareSpeech} />

      <div
        className={`min-h-0 overflow-hidden ${
          mobileTab === 'projecten' ? 'block' : 'hidden'
        } md:block`}
      >
        <ScriptsPanel
          activeTitle={activeTitle}
          activeLabel={activeLabel}
          onNew={onNew}
          onSelectExample={onSelectExample}
        />
      </div>

      <div
        className={`min-h-0 min-w-0 overflow-hidden ${
          mobileTab === 'script' ? 'block' : 'hidden'
        } md:block`}
      >
        <ScriptEditor value={script} onChange={setScript} rate={rate} />
      </div>

      <div
        className={`min-h-0 overflow-hidden ${
          mobileTab === 'stem' ? 'block' : 'hidden'
        } md:block`}
      >
        <VoicePanel
          lang={lang}
          rate={rate}
          onLang={setLang}
          onRate={setRate}
          onSample={() => speak(SAMPLE_LINE, true)}
          onPreview={() => speak(script, false)}
          onFull={() => speak(script, true)}
          speaking={speaking}
        />
      </div>

      <div className="md:col-span-3">
        <Transport
          playing={speaking}
          hasAudio={!!audioBlob}
          progress={progress}
          currentLabel={formatDuration(elapsed)}
          totalLabel={formatDuration(totalSeconds)}
          onPlayPause={() => speak(script, true)}
          onStop={stopSpeech}
          onDownloadScript={onDownloadScript}
          onDownloadAudio={onDownloadAudio}
        />
      </div>

      <nav className="grid grid-cols-3 border-t border-line bg-surface md:col-span-3 md:hidden">
        {(
          [
            ['script', 'Script'],
            ['stem', 'Stem'],
            ['projecten', 'Projecten'],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setMobileTab(id)}
            className={`flex h-12 items-center justify-center gap-2 text-sm font-medium transition-colors duration-150 ${
              mobileTab === id ? 'text-fg' : 'text-muted'
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      {toast && (
        <div className="pointer-events-none fixed right-4 bottom-24 z-50 max-w-sm rounded-xl bg-elevated px-4 py-3 text-sm text-fg shadow-border md:bottom-8">
          {toast}
        </div>
      )}
    </div>
  )
}
