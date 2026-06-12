import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateProject } from '@/api/hooks'
import { SectionCard } from '@/components/SectionCard'
import { FormField } from '@/components/form/FormField'
import { TextInput } from '@/components/form/inputs'
import { useToast } from '@/components/ui/Toast'

export function NewProjectPage() {
  const navigate = useNavigate()
  const create = useCreateProject()
  const { notify } = useToast()
  const [name, setName] = useState('')
  const [error, setError] = useState<string>()

  const submit = () => {
    if (!name.trim()) {
      setError('Please enter a plan name')
      return
    }
    create.mutate(name.trim(), {
      onSuccess: (project) => {
        notify('Business plan created')
        navigate(`/projects/${project.id}/setup`)
      },
      onError: (e) => notify((e as Error).message || 'Failed to create', 'error'),
    })
  }

  return (
    <div className="landing">
      <header className="landing__header">
        <div className="landing__brand">
          <div className="sidebar__logo">B</div>
          <div className="landing__title">New Business Plan</div>
        </div>
        <button className="btn btn--ghost" onClick={() => navigate('/projects')}>
          ← Back to Projects
        </button>
      </header>

      <div className="landing__body" style={{ maxWidth: 640 }}>
        <SectionCard
          title="Create a Business Plan"
          subtitle="Give your plan a name. You'll set the business identity, currency, and projection period next."
          icon="◧"
          footer={
            <div className="row row--between">
              <span className="muted" style={{ fontSize: 12.5 }}>You can rename this later in Project Setup.</span>
              <button className="btn btn--primary" onClick={submit} disabled={create.isPending}>
                {create.isPending ? 'Creating…' : 'Create & Continue →'}
              </button>
            </div>
          }
        >
          <FormField label="Plan Name" required error={error} htmlFor="plan-name">
            <TextInput
              id="plan-name"
              value={name}
              onChange={(v) => {
                setName(v)
                setError(undefined)
              }}
              placeholder="e.g. 2026 Growth Plan"
              error={!!error}
            />
          </FormField>
        </SectionCard>
      </div>
    </div>
  )
}
