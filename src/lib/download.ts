export function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function downloadBlob(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
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
