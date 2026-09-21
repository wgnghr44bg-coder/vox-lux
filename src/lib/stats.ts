const WPM = 150

/** Strip markup tags/markers for counting spoken words */
export function plainText(script: string): string {
  return script
    .replace(/\[(?:long )?pause\]/gi, ' ')
    .replace(/\[laugh\]/gi, ' ')
    .replace(/<\/?(?:emphasis|whisper|slow|fast|soft)>/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export function countWords(script: string): number {
  const text = plainText(script)
  if (!text) return 0
  return text.split(/\s+/).filter(Boolean).length
}

export function countChars(script: string): number {
  return script.length
}

export function estimateSeconds(script: string, rate = 1): number {
  const words = countWords(script)
  if (words === 0) return 0
  return Math.round((words / WPM) * 60 / Math.max(0.5, rate))
}

export function formatDuration(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds))
  const m = Math.floor(s / 60)
  const rem = s % 60
  return `${m}:${rem.toString().padStart(2, '0')}`
}
