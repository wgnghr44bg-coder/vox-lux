import { Download, Pause, Play, Square } from 'lucide-react'
import { useMemo } from 'react'

type Props = {
  playing: boolean
  hasAudio: boolean
  progress: number
  currentLabel: string
  totalLabel: string
  onPlayPause: () => void
  onStop: () => void
  onDownloadScript: () => void
  onDownloadAudio: () => void
}

function Waveform({ progress, active }: { progress: number; active: boolean }) {
  const bars = useMemo(
    () =>
      Array.from({ length: 64 }, (_, i) => {
        const n = Math.sin(i * 0.45) * 0.35 + Math.cos(i * 0.17) * 0.25 + 0.4
        return Math.max(0.12, Math.min(1, n))
      }),
    [],
  )

  return (
    <div
      className="flex h-10 w-full items-end gap-px rounded-md px-0.5"
      aria-hidden
    >
      {bars.map((h, i) => {
        const filled = i / bars.length <= progress
        return (
          <span
            key={i}
            className={`min-w-px flex-1 rounded-full transition-colors duration-150 ${
              filled && active ? 'bg-accent' : 'bg-subtle/50'
            } ${active && !filled ? 'rec-dot' : ''}`}
            style={{ height: `${h * 100}%` }}
          />
        )
      })}
    </div>
  )
}

export function Transport({
  playing,
  hasAudio,
  progress,
  currentLabel,
  totalLabel,
  onPlayPause,
  onStop,
  onDownloadScript,
  onDownloadAudio,
}: Props) {
  return (
    <div className="border-t border-line bg-surface px-4 py-3 md:col-span-3 md:px-6">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 sm:flex-row sm:items-center">
        <div className="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
          <button
            type="button"
            onClick={onPlayPause}
            className="inline-flex size-9 shrink-0 items-center justify-center rounded-md bg-accent text-accent-fg transition-[opacity,transform] duration-150 hover:opacity-90 active:scale-[0.96]"
            aria-label={playing ? 'Pauze' : 'Afspelen'}
          >
            <span className="relative size-5">
              {playing ? (
                <Pause className="absolute inset-0 size-5" />
              ) : (
                <Play className="absolute inset-0 ml-0.5 size-5" />
              )}
            </span>
          </button>

          <div className="min-w-0 flex-1">
            <Waveform progress={progress} active={playing || progress > 0} />
            <div className="mt-1 flex items-center justify-between text-xs text-subtle tabular-nums">
              <span>{currentLabel}</span>
              <span>{totalLabel}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={onStop}
            disabled={!playing && progress === 0}
            className="hidden size-9 items-center justify-center rounded-md text-muted transition-[background-color,color] duration-150 hover:bg-elevated hover:text-fg disabled:pointer-events-none disabled:opacity-40 sm:inline-flex"
            aria-label="Stop"
          >
            <Square className="size-3.5" aria-hidden />
          </button>
        </div>

        <div className="flex w-full gap-2 sm:max-w-sm">
          <button
            type="button"
            onClick={onDownloadScript}
            className="inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-xl px-4 text-sm font-medium text-fg shadow-border transition-[box-shadow,transform] duration-150 hover:shadow-border-hover active:scale-[0.96]"
          >
            <Download className="size-4" aria-hidden />
            Script .txt
          </button>
          <button
            type="button"
            onClick={onDownloadAudio}
            disabled={!hasAudio}
            className="inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-xl bg-accent px-4 text-sm font-medium text-accent-fg transition-[opacity,transform] duration-150 hover:opacity-90 active:scale-[0.96] disabled:pointer-events-none disabled:opacity-40"
            title={
              hasAudio
                ? 'Download MP3 (Lux)'
                : 'Genereer eerst sample / voorproef / volle voice-over'
            }
          >
            <Download className="size-4" aria-hidden />
            Download MP3
          </button>
        </div>
      </div>
    </div>
  )
}
