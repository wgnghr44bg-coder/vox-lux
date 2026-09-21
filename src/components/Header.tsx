import { FilePlus, Sparkles, WandSparkles } from 'lucide-react'

type Props = {
  onNew: () => void
  onPrepareSpeech: () => void
}

export function Header({ onNew, onPrepareSpeech }: Props) {
  return (
    <header className="flex items-center gap-3 border-b border-line px-4 py-3 md:col-span-3 md:px-6">
      <div className="min-w-0 flex-1">
        <p className="font-display text-2xl leading-none tracking-tight text-fg">
          VOX
        </p>
        <p className="mt-0.5 hidden text-xs text-subtle sm:block">
          YouTube voice studio
        </p>
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onNew}
          className="hidden h-9 items-center justify-center gap-2 rounded-md px-3 text-sm font-medium text-muted transition-[transform,opacity,background-color,color,box-shadow] duration-150 ease-out hover:bg-elevated hover:text-fg active:scale-[0.96] sm:inline-flex"
        >
          <FilePlus className="size-4" aria-hidden />
          Nieuw
        </button>
        <button
          type="button"
          onClick={onPrepareSpeech}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md px-3 text-sm font-medium text-fg shadow-border transition-[transform,opacity,background-color,color,box-shadow] duration-150 ease-out hover:shadow-border-hover active:scale-[0.96]"
        >
          <WandSparkles className="size-4" aria-hidden />
          <span className="hidden sm:inline">Voor spraak</span>
        </button>
        <button
          type="button"
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md bg-accent px-3 text-sm font-medium text-accent-fg transition-[transform,opacity] duration-150 ease-out hover:opacity-90 active:scale-[0.96]"
          title="AI script (mock)"
          onClick={() =>
            alert(
              'AI script is een mock in deze Lux-build. Plak of kies een voorbeeld hieronder.',
            )
          }
        >
          <Sparkles className="size-4" aria-hidden />
          AI script
        </button>
      </div>
    </header>
  )
}
