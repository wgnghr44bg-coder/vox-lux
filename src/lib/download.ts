function isIos(): boolean {
  if (typeof navigator === 'undefined') return false
  return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
}

export function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  void triggerDownload(filename, blob)
}

export function downloadBlob(filename: string, blob: Blob) {
  void triggerDownload(filename, blob)
}

/** Prefer Web Share on iOS (Save to Files); otherwise <a download>. */
export async function triggerDownload(filename: string, blob: Blob): Promise<'shared' | 'saved' | 'opened'> {
  const type = blob.type || 'application/octet-stream'
  const file = new File([blob], filename, { type })

  const nav = typeof navigator !== 'undefined' ? navigator : null
  const canShareFiles =
    !!nav &&
    typeof nav.share === 'function' &&
    typeof nav.canShare === 'function' &&
    nav.canShare({ files: [file] })

  if (canShareFiles) {
    try {
      await nav!.share({ files: [file], title: filename })
      return 'shared'
    } catch (err) {
      // User cancelled share sheet — not a failure to retry automatically.
      if (err instanceof DOMException && err.name === 'AbortError') {
        return 'shared'
      }
      /* fall through to anchor download */
    }
  }

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.rel = 'noopener'
  a.style.display = 'none'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)

  // iOS often ignores download= — open blob so Share/Save still works.
  if (isIos()) {
    window.setTimeout(() => {
      window.open(url, '_blank')
    }, 50)
    window.setTimeout(() => URL.revokeObjectURL(url), 120_000)
    return 'opened'
  }

  window.setTimeout(() => URL.revokeObjectURL(url), 10_000)
  return 'saved'
}

/** Minimal silent-ish WAV placeholder is not useful; we only enable audio download
 *  when we have a real MediaRecorder blob from a capture session. */
export function slugifyTitle(text: string): string {
  const first = text.split('\n').find((l) => l.trim()) ?? 'vox-script'
  return (
    first
      .toLowerCase()
      .replace(/\[.*?\]/g, '')
      .replace(/<[^>]+>/g, '')
      .replace(/[^a-z0-9\u00c0-\u024f]+/gi, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 48) || 'vox-script'
  )
}
