import { useState } from 'react'
import { ExcelModelExportDialog } from './ExcelModelExportDialog'

export function ExcelModelButton({
  projectId,
  className = 'btn btn--secondary',
  label = '▦ Generate Excel Model',
}: {
  projectId: string
  className?: string
  label?: string
}) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button type="button" className={className} onClick={() => setOpen(true)} title="Export the full financial model to Excel">
        {label}
      </button>
      <ExcelModelExportDialog projectId={projectId} open={open} onClose={() => setOpen(false)} />
    </>
  )
}
