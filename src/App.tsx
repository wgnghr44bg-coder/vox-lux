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
import { downloadText, slugifyTitle, triggerDownload } from './lib/download'
import { estimateSeconds, formatDuration } from './lib/stats'
import { luxToastLabel, playAudioBlob, speakLux, stripForSpeech, unlockAudioForPlayback } from './lib/tts'

type MobileTab = 'script' | 'stem' | 'projecten'

const SAMPLE_LINE =
  'Lux. Oude, kalme documentaire-stem. Alsof hij naast je bed een verhaal voorleest.'

export default function App() {
  const [script, setScript] = useState(DEFAULT_SCRIPT)
  const [lang, setLang] = useState('nl-NL')
  const [rate, setRate] = useState(0.7)
  const [speaking, setSpeaking] = useState(false)
  const [busy, setBusy] = useState(false)
  const [progress, setProgress] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [activeLabel, setActiveLabel] = useState('Voorbeeld')
  const [mobileTab, setMobileTab] = useState<MobileTab>('script')
  const [toast, setToast] = useState<string | null>(null)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)

  const stopRef = useRef<(() => void) | null>(null)
  const tickRef = useRef<number | null>(null)
  const durationRef = useRef(0)
  const genIdRef = useRef(0)

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
    genIdRef.current += 1
    stopRef.current?.()
    stopRef.current = null
    clearTicker()
    setSpeaking(false)
    setBusy(false)
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
      setProgress(Math.min(0.95, t / durationRef.current))
    }, 80)
  }

  const speak = useCallback(
    async (text: string, full = false) => {
      if (speaking || busy) {
        stopSpeech()
        return
      }

      if (!text.trim()) {
        showToast('Schrijf eerst een script.')
        return
      }

      const previewText = full
        ? text
        : text.split(/\n\n+/)[0]?.slice(0, 420) || text.slice(0, 420)

      const secs = estimateSeconds(previewText, rate) || 4
      const myId = ++genIdRef.current
      // Kick audio unlock before network TTS (real play happens on ▶).
      void unlockAudioForPlayback()
      setBusy(true)
      setProgress(0)
      setElapsed(0)
      startTicker(secs)
      showToast('Lux-stem genereren…')

      try {
        const handle = await speakLux({
          text: previewText,
          lang,
          rate,
          onAudio: (blob) => {
            if (myId !== genIdRef.current) return
            setAudioBlob(blob)
          },
          onStart: (meta) => {
            if (myId !== genIdRef.current) return
            clearTicker()
            setBusy(false)
            setSpeaking(true)
            showToast(meta?.label ?? luxToastLabel(lang))
          },
          onProgress: (fraction, elapsedSec) => {
            if (myId !== genIdRef.current) return
            setProgress(fraction)
            setElapsed(elapsedSec)
          },
          onEnd: () => {
            if (myId !== genIdRef.current) return
            clearTicker()
            setSpeaking(false)
            setBusy(false)
            setProgress(1)
            stopRef.current = null
          },
          onError: (err) => {
            if (myId !== genIdRef.current) return
            showToast(`Spraak: ${err}`)
            stopSpeech()
          },
        })

        if (myId !== genIdRef.current) {
          handle.stop()
          return
        }
        if (handle.audioBlob) setAudioBlob(handle.audioBlob)
        if (!handle.played) {
          clearTicker()
          setBusy(false)
          setSpeaking(false)
          setProgress(1)
          stopRef.current = null
          showToast('MP3 klaar — tik ▶ om te beluisteren (of Download MP3)')
        } else {
          stopRef.current = handle.stop
        }
      } catch (err) {
        if (myId !== genIdRef.current) return
        clearTicker()
        setBusy(false)
        setSpeaking(false)
        showToast(
          `Audio genereren mislukt: ${err instanceof Error ? err.message : String(err)}`,
        )
      }
    },
    [speaking, busy, stopSpeech, rate, lang],
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
    const cleaned = script
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim()
    setScript(cleaned ? cleaned + '\n' : '')
    showToast('Script opgeschoond voor spraak.')
  }

  const replayBlob = useCallback(
    async (blob: Blob) => {
      if (speaking || busy) {
        stopSpeech()
        return
      }
      const myId = ++genIdRef.current
      await unlockAudioForPlayback()
      setBusy(false)
      setSpeaking(true)
      setProgress(0)
      setElapsed(0)
      showToast(luxToastLabel(lang))
      const stop = await playAudioBlob(blob, {
        onProgress: (fraction, elapsedSec) => {
          if (myId !== genIdRef.current) return
          setProgress(fraction)
          setElapsed(elapsedSec)
        },
        onEnd: () => {
          if (myId !== genIdRef.current) return
          setSpeaking(false)
          setProgress(1)
          stopRef.current = null
        },
        onError: (msg) => {
          if (myId !== genIdRef.current) return
          showToast(msg)
          setSpeaking(false)
          stopRef.current = null
        },
      })
      if (myId !== genIdRef.current) {
        stop()
        return
      }
      stopRef.current = stop
    },
    [speaking, busy, stopSpeech, lang],
  )

  const onDownloadScript = () => {
    const name = `${slugifyTitle(script) || 'vox-script'}.txt`
    downloadText(name, script)
    showToast(`Script gedownload: ${name}`)
  }

  const onDownloadAudio = async () => {
    if (!audioBlob) {
      showToast('Genereer eerst een sample, voorproef of volle voice-over.')
      return
    }
    const ext = audioBlob.type.includes('mpeg') ? 'mp3' : 'audio'
    const name = `${slugifyTitle(script) || 'vox-lux'}.${ext}`
    const how = await triggerDownload(name, audioBlob)
    if (how === 'shared') showToast(`Deel/bewaar: ${name}`)
    else if (how === 'opened') showToast(`MP3 geopend — Deel → Bewaar in Bestanden`)
    else showToast(`Audio gedownload: ${name}`)
  }

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
          onSample={() => void speak(SAMPLE_LINE, true)}
          onPreview={() => void speak(script, false)}
          onFull={() => void speak(script, true)}
          speaking={speaking || busy}
        />
      </div>

      <div className="md:col-span-3">
        <Transport
          playing={speaking || busy}
          hasAudio={!!audioBlob}
          progress={progress}
          currentLabel={formatDuration(elapsed)}
          totalLabel={formatDuration(totalSeconds)}
          onPlayPause={() => {
            if (speaking || busy) {
              stopSpeech()
              return
            }
            if (audioBlob) {
              void replayBlob(audioBlob)
              return
            }
            void speak(script, true)
          }}
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
