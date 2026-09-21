import { useRef } from 'react'
import { SPEECH_CHIPS } from '../data/examples'
import { countChars, countWords, estimateSeconds, formatDuration } from '../lib/stats'

type Props = {
  value: string
  onChange: (v: string) => void
  rate: number
}

export function ScriptEditor({ value, onChange, rate }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null)
  const words = countWords(value)
  const chars = countChars(value)
  const est = formatDuration(estimateSeconds(value, rate))

  const insertAtCursor = (insert: string) => {
    const el = ref.current
    if (!el) {
      onChange(value + insert)
      return
    }
    const start = el.selectionStart
    const end = el.selectionEnd
    const before = value.slice(0, start)
    const after = value.slice(end)

    // For wrap tags like <emphasis></emphasis>, place cursor inside
    const closeIdx = insert.indexOf('></')
    let next = before + insert + after
    let caret = start + insert.length
    if (closeIdx !== -1) {
      caret = start + closeIdx + 1
    }

    onChange(next)
    requestAnimationFrame(() => {
      el.focus()
      el.setSelectionRange(caret, caret)
    })
  }

  return (
    <section className="flex h-full min-h-0 min-w-0 flex-col">
      <div className="flex flex-wrap items-center gap-1.5 border-b border-line px-4 py-2.5 md:px-6">
        {SPEECH_CHIPS.map((chip) => (
          <button
            key={chip.id}
            type="button"
            onClick={() => insertAtCursor(chip.insert)}
            className="h-8 rounded-full px-3 text-xs font-medium text-muted shadow-border transition-[color,box-shadow,transform] duration-150 ease-out hover:text-fg hover:shadow-border-hover active:scale-[0.96]"
          >
            {chip.label}
          </button>
        ))}
      </div>
      <div className="relative min-h-0 flex-1">
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck
          placeholder="Plak of schrijf je YouTube-script. De eerste zin is de hook."
          className="script-scroll h-full w-full resize-none bg-transparent px-4 py-5 text-base leading-relaxed text-fg placeholder:text-subtle focus:outline-none md:px-8 md:py-7 md:text-lg md:leading-8"
        />
      </div>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-line px-4 py-2.5 text-xs text-subtle tabular-nums md:px-6">
        <span>{words} woorden</span>
        <span>{est} geschat</span>
        <span>{chars} tekens · voorproef leest de opening</span>
      </div>
    </section>
  )
}
