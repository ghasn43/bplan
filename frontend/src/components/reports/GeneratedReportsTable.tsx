import { ReportFormatBadge } from './ReportStatusBadge'
import type { ReportFile } from '@/types/reports'

function fmtSize(bytes: number): string {
  if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(1)} MB`
  if (bytes >= 1000) return `${Math.round(bytes / 1000)} KB`
  return `${bytes} B`
}

function fmtDate(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString()
}

export function GeneratedReportsTable({
  reports,
  onDelete,
  deletingId,
}: {
  reports: ReportFile[]
  onDelete: (reportId: string) => void
  deletingId?: string | null
}) {
  if (reports.length === 0) {
    return <p className="muted" style={{ fontSize: 13.5 }}>No reports generated yet. Choose your options above and generate a Word or PDF report.</p>
  }
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>File</th>
            <th>Format</th>
            <th>Scenario</th>
            <th>View</th>
            <th style={{ textAlign: 'right' }}>Size</th>
            <th>Created</th>
            <th style={{ textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((r) => (
            <tr key={r.report_id}>
              <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={r.file_name}>
                {r.file_name}
                {r.message && <div className="muted" style={{ fontSize: 11 }}>{r.message}</div>}
              </td>
              <td><ReportFormatBadge format={r.format} /></td>
              <td style={{ textTransform: 'capitalize' }}>{r.scenario}</td>
              <td style={{ textTransform: 'capitalize' }}>{r.view}</td>
              <td style={{ textAlign: 'right' }}>{fmtSize(r.size_bytes)}</td>
              <td>{fmtDate(r.created_at)}</td>
              <td style={{ textAlign: 'right' }}>
                <div className="row" style={{ gap: 6, justifyContent: 'flex-end' }}>
                  <a className="btn btn--secondary btn--sm" href={r.download_url} download={r.file_name}>
                    ⤓ Download
                  </a>
                  <button
                    className="btn btn--ghost btn--sm"
                    onClick={() => onDelete(r.report_id)}
                    disabled={deletingId === r.report_id}
                  >
                    {deletingId === r.report_id ? '…' : 'Delete'}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
