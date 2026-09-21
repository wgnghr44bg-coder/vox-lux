import { Plus } from 'lucide-react'
import { EXAMPLES, type ExampleScript } from '../data/examples'

type Props = {
  activeTitle: string
  activeLabel?: string
  onNew: () => void
  onSelectExample: (ex: ExampleScript) => void
}

export function ScriptsPanel({
  activeTitle,
  activeLabel = 'Voorbeeld',
  onNew,
  onSelectExample,
}: Props) {
  return (
    <aside className="flex h-full min-h-0 w-full flex-col overflow-hidden bg-surface md:border-r md:border-line">
      <div className="flex items-center justify-between px-4 py-4">
        <p className="text-xs font-medium tracking-wide text-subtle uppercase">
          Scripts
        </p>
        <button
          type="button"
          onClick={onNew}
          className="inline-flex size-9 items-center justify-center rounded-md text-muted transition-[background-color,color] duration-150 hover:bg-elevated hover:text-fg active:scale-[0.96]"
          aria-label="Nieuw script"
        >
          <Plus className="size-4" aria-hidden />
        </button>
      </div>
      <div className="voice-scroll min-h-0 flex-1 overflow-y-auto px-3 pb-3">
        <ul className="space-y-1">
          <li>
            <button
              type="button"
              className="w-full rounded-xl bg-elevated px-3 py-2.5 text-left text-fg transition-[background-color] duration-150"
            >
              <span className="block truncate text-sm font-medium">
                {activeTitle || 'Leeg script'}
              </span>
              <span className="mt-0.5 block text-xs text-subtle tabular-nums">
                {activeLabel}
              </span>
            </button>
          </li>
        </ul>
        <p className="mt-6 mb-2 px-1 text-xs font-medium tracking-wide text-subtle uppercase">
          Voorbeelden
        </p>
        <ul className="space-y-1">
          {EXAMPLES.map((ex) => (
            <li key={ex.id}>
              <button
                type="button"
                onClick={() => onSelectExample(ex)}
                className="w-full rounded-xl px-3 py-2.5 text-left text-muted transition-[background-color,color] duration-150 hover:bg-elevated/70 hover:text-fg"
              >
                <span className="block text-sm font-medium">{ex.title}</span>
                <span className="mt-0.5 block text-xs text-subtle">
                  {ex.description}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  )
}
