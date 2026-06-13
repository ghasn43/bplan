import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@/components/PageHeader'
import { SectionCard } from '@/components/SectionCard'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { LoadingScreen } from '@/components/ui/Spinner'
import { useToast } from '@/components/ui/Toast'
import { useCompanies } from '@/api/companyApi'
import {
  useAssignCompany,
  useCreateUser,
  useDeleteUser,
  useResetUserPassword,
  useSetUserActive,
  useUsers,
} from '@/api/adminUsersApi'
import type { CreateUserInput, Role } from '@/types/auth'

export function UserManagementPage() {
  const navigate = useNavigate()
  const { notify } = useToast()
  const usersQ = useUsers()
  const companiesQ = useCompanies()
  const create = useCreateUser()
  const setActive = useSetUserActive()
  const assign = useAssignCompany()
  const resetPw = useResetUserPassword()
  const del = useDeleteUser()
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')

  const companyName = useMemo(() => {
    const map = new Map((companiesQ.data ?? []).map((c) => [c.id, c.company_name]))
    return (id: string | null) => (id ? map.get(id) ?? id : '—')
  }, [companiesQ.data])

  if (usersQ.isLoading) return <LoadingScreen label="Loading users…" />

  const users = (usersQ.data ?? []).filter(
    (u) => !search || u.email.toLowerCase().includes(search.toLowerCase()) || u.full_name.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <>
      <PageHeader
        breadcrumb="Admin"
        title="User Management"
        subtitle="Create users, assign them to companies, and control access."
        actions={
          <>
            <button className="btn btn--ghost" onClick={() => navigate('/projects')}>← Projects</button>
            <button className="btn btn--primary" onClick={() => setOpen(true)}>+ Add User</button>
          </>
        }
      />
      <div className="stack">
        <SectionCard>
          <input className="input" placeholder="Search by name or email" value={search}
            onChange={(e) => setSearch(e.target.value)} style={{ maxWidth: 320, marginBottom: 12 }} />
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Role</th><th>Company</th><th>Status</th><th style={{ textAlign: 'right' }}>Actions</th></tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.full_name || '—'}</td>
                    <td>{u.email}</td>
                    <td><Badge tone={u.role === 'admin' ? 'blue' : 'neutral'}>{u.role}</Badge></td>
                    <td>{u.role === 'admin' ? 'All companies' : companyName(u.company_id)}</td>
                    <td><Badge tone={u.is_active ? 'green' : 'red'} dot>{u.is_active ? 'Active' : 'Disabled'}</Badge></td>
                    <td style={{ textAlign: 'right' }}>
                      <div className="row" style={{ gap: 6, justifyContent: 'flex-end' }}>
                        <button className="btn btn--ghost btn--sm" onClick={() => setActive.mutate({ id: u.id, active: !u.is_active })}>
                          {u.is_active ? 'Disable' : 'Enable'}
                        </button>
                        {u.role === 'user' && (
                          <select className="input input--sm" value={u.company_id ?? ''} style={{ width: 150 }}
                            onChange={(e) => assign.mutate({ id: u.id, company_id: e.target.value }, { onSuccess: () => notify('Company updated') })}>
                            {(companiesQ.data ?? []).map((c) => <option key={c.id} value={c.id}>{c.company_name}</option>)}
                          </select>
                        )}
                        <button className="btn btn--ghost btn--sm" onClick={() => {
                          const pw = window.prompt('New temporary password (min 10 chars, upper/lower/number/special):')
                          if (pw) resetPw.mutate({ id: u.id, temporary_password: pw }, {
                            onSuccess: () => notify('Password reset'), onError: (e) => notify((e as Error).message, 'error') })
                        }}>Reset PW</button>
                        <button className="btn btn--ghost btn--sm" onClick={() => {
                          if (window.confirm(`Delete ${u.email}?`)) del.mutate(u.id, { onSuccess: () => notify('User deleted') })
                        }}>🗑</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      </div>
      {open && <AddUserModal onClose={() => setOpen(false)} onCreate={(body) => create.mutate(body, {
        onSuccess: () => { notify('User created'); setOpen(false) },
        onError: (e) => notify((e as Error).message, 'error'),
      })} companies={companiesQ.data ?? []} pending={create.isPending} />}
    </>
  )
}

function AddUserModal({ onClose, onCreate, companies, pending }: {
  onClose: () => void
  onCreate: (body: CreateUserInput) => void
  companies: { id: string; company_name: string }[]
  pending: boolean
}) {
  const [form, setForm] = useState<CreateUserInput>({
    email: '', full_name: '', role: 'user', company_id: companies[0]?.id ?? null,
    temporary_password: '', must_change_password: true,
  })
  const set = (p: Partial<CreateUserInput>) => setForm((f) => ({ ...f, ...p }))
  return (
    <Modal title="Add User" open onClose={onClose} footer={
      <div className="row" style={{ gap: 8, justifyContent: 'flex-end', width: '100%' }}>
        <button className="btn btn--secondary" onClick={onClose}>Cancel</button>
        <button className="btn btn--primary" disabled={pending} onClick={() => onCreate({
          ...form, company_id: form.role === 'admin' ? null : form.company_id,
        })}>{pending ? 'Creating…' : 'Create User'}</button>
      </div>
    }>
      <div className="stack--sm">
        <div className="field"><span className="field__label">Full name</span>
          <input className="input" value={form.full_name} onChange={(e) => set({ full_name: e.target.value })} /></div>
        <div className="field"><span className="field__label">Email *</span>
          <input className="input" type="email" value={form.email} onChange={(e) => set({ email: e.target.value })} /></div>
        <div className="field"><span className="field__label">Role</span>
          <select className="input" value={form.role} onChange={(e) => set({ role: e.target.value as Role })}>
            <option value="user">User</option><option value="admin">Admin</option>
          </select></div>
        {form.role === 'user' && (
          <div className="field"><span className="field__label">Assigned company *</span>
            <select className="input" value={form.company_id ?? ''} onChange={(e) => set({ company_id: e.target.value })}>
              {companies.map((c) => <option key={c.id} value={c.id}>{c.company_name}</option>)}
            </select></div>
        )}
        <div className="field"><span className="field__label">Temporary password *</span>
          <input className="input" value={form.temporary_password} onChange={(e) => set({ temporary_password: e.target.value })}
            placeholder="Min 10 chars, upper/lower/number/special" /></div>
        <label className="row" style={{ gap: 8, alignItems: 'center' }}>
          <input type="checkbox" checked={form.must_change_password} onChange={(e) => set({ must_change_password: e.target.checked })} />
          <span style={{ fontSize: 13.5 }}>Must change password on first login</span>
        </label>
      </div>
    </Modal>
  )
}
