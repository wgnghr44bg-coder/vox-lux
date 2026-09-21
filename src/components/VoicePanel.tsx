import { Volume2 } from 'lucide-react'
import { LUX_VOICE } from '../data/examples'

type Props = {
  lang: string
  rate: number
  onLang: (v: string) => void
  onRate: (v: number) => void
  onSample: () => void
  onPreview: () => void
  onFull: () => void
  speaking: boolean
}

export function VoicePanel({
  lang,
  rate,
  onLang,
  onRate,
  onSample,
  onPreview,
  onFull,
  speaking,
}: Props) {
  const pct = ((rate - 0.7) / (1.5 - 0.7)) * 100

  return (
    <aside className="flex h-full min-h-0 w-full flex-col overflow-hidden bg-surface md:border-l md:border-line">
      <div className="border-b border-line px-5 py-4">
        <p className="text-xs font-medium tracking-wide text-subtle uppercase">
          Stem
        </p>
        <h2 className="font-display text-2xl leading-tight text-fg">
          {LUX_VOICE.name}
        </h2>
        <p className="mt-1 text-sm text-muted">{LUX_VOICE.short}</p>
      </div>

      <div className="voice-scroll min-h-0 flex-1 overflow-y-auto px-4 py-3">
        <button
          type="button"
          className="mb-4 w-full rounded-2xl bg-accent px-4 py-3.5 text-left text-accent-fg shadow-border transition-[background-color,box-shadow,transform] duration-150 ease-out hover:shadow-border-hover active:scale-[0.96]"
          aria-pressed
        >
          <span className="text-xs font-medium tracking-wide uppercase opacity-70">
            {LUX_VOICE.badge}
          </span>
          <span className="mt-1 block font-display text-2xl leading-none">
            {LUX_VOICE.name}
          </span>
          <span className="mt-0.5 block text-sm font-medium">
            {LUX_VOICE.subtitle}
          </span>
          <span className="mt-1.5 block text-xs leading-relaxed opacity-70">
            {LUX_VOICE.description}
          </span>
        </button>

        <p className="mb-2 px-1 text-xs font-medium tracking-wide text-subtle uppercase">
          Voice-over
        </p>
        <ul className="grid grid-cols-1 gap-2">
          <li>
            <button
              type="button"
              className="flex h-full w-full flex-col rounded-xl bg-accent px-3 py-2.5 text-left text-accent-fg transition-[background-color,box-shadow,transform] duration-150 ease-out active:scale-[0.96]"
            >
              <span className="text-sm font-medium">{LUX_VOICE.name}</span>
              <span className="mt-0.5 line-clamp-2 text-xs text-accent-fg/70">
                {LUX_VOICE.short}
              </span>
            </button>
          </li>
        </ul>
        <p className="mt-4 px-1 text-xs leading-relaxed text-subtle">
          Deze build bevat alleen Lux — geen Eve, Helix of andere stemmen.
        </p>
      </div>

      <div className="space-y-3 border-t border-line px-4 py-3">
        <label className="block">
          <span className="text-xs font-medium tracking-wide text-subtle uppercase">
            Taal
          </span>
          <select
            value={lang}
            onChange={(e) => onLang(e.target.value)}
            className="mt-1.5 h-11 w-full rounded-lg bg-elevated px-3 text-sm text-fg shadow-border focus:ring-2 focus:ring-ring focus:outline-none"
          >
            <option value="nl-NL">Nederlands</option>
            <option value="en-US">English (US)</option>
            <option value="en-GB">English (UK)</option>
            <option value="de-DE">Deutsch</option>
            <option value="fr-FR">Français</option>
            <option value="es-ES">Español</option>
            <option value="auto">Auto-detect</option>
          </select>
        </label>

        <div>
          <div className="flex items-center justify-between text-xs">
            <span className="font-medium tracking-wide text-subtle uppercase">
              Tempo
            </span>
            <span className="text-muted tabular-nums">{rate.toFixed(2)}×</span>
          </div>
          <input
            type="range"
            min={0.7}
            max={1.5}
            step={0.01}
            value={rate}
            onChange={(e) => onRate(Number(e.target.value))}
            aria-label="Tempo"
            className="mt-2 h-11 w-full cursor-pointer appearance-none bg-transparent accent-[var(--color-accent)]"
            style={{
              background: `linear-gradient(to right, var(--color-accent) ${pct}%, var(--color-elevated) ${pct}%)`,
              borderRadius: 999,
              height: 4,
              marginTop: 18,
              marginBottom: 14,
            }}
          />
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={onSample}
            className="inline-flex h-10 flex-1 items-center justify-center gap-2 rounded-md px-4 text-sm font-medium text-fg shadow-border transition-[transform,box-shadow] duration-150 hover:shadow-border-hover active:scale-[0.96]"
          >
            <Volume2 className="size-4" aria-hidden />
            Sample
          </button>
          <button
            type="button"
            onClick={onPreview}
            className="inline-flex h-10 flex-1 items-center justify-center gap-2 rounded-md bg-elevated px-4 text-sm font-medium text-fg transition-[background-color,transform] duration-150 hover:bg-surface-2 active:scale-[0.96]"
          >
            {speaking ? 'Stop' : 'Voorproef'}
          </button>
        </div>

        <button
          type="button"
          onClick={onFull}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-accent px-5 text-base font-medium text-accent-fg transition-[opacity,transform] duration-150 hover:opacity-90 active:scale-[0.96]"
        >
          Volledige voice-over
        </button>
        <p className="text-center text-xs text-subtle">
          Gratis Edge-stem (Lux-achtig) — niet de officiële Grok Lux.
        </p>
      </div>
    </aside>
  )
}
