export type SaveState = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error'

export function AutosaveIndicator({ state, savedAt }: { state: SaveState; savedAt?: Date | null }) {
  const map: Record<SaveState, { label: string; tone: string; dot: string }> = {
    idle: { label: 'All changes saved', tone: '#64748b', dot: '#cbd5e1' },
    unsaved: { label: 'Unsaved changes', tone: '#92400e', dot: '#d97706' },
    saving: { label: 'Saving…', tone: '#1e40af', dot: '#2563eb' },
    saved: { label: savedAt ? `Saved ${savedAt.toLocaleTimeString()}` : 'Saved', tone: '#047857', dot: '#059669' },
    error: { label: 'Error saving — will retry', tone: '#991b1b', dot: '#dc2626' },
  }
  const s = map[state]
  return (
    <span className="row" style={{ gap: 6, alignItems: 'center', fontSize: 12, color: s.tone }}>
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: s.dot }} />
      {s.label}
    </span>
  )
}
