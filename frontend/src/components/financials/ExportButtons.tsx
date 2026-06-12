import { useToast } from '@/components/ui/Toast'

/** Placeholder export buttons — wired up in a later phase (PDF/Excel/Word). */
export function ExportButtons() {
  const { notify } = useToast()
  const soon = (what: string) => notify(`${what} export is coming in the next phase`, 'success')
  return (
    <div className="field" style={{ minWidth: 0 }}>
      <span className="field__label">Export</span>
      <div className="row" style={{ gap: 8 }}>
        <button className="btn btn--secondary btn--sm" onClick={() => soon('PDF')}>⤓ PDF</button>
        <button className="btn btn--secondary btn--sm" onClick={() => soon('Excel')}>⤓ Excel</button>
        <button className="btn btn--secondary btn--sm" onClick={() => soon('Word')}>⤓ Word</button>
      </div>
    </div>
  )
}
