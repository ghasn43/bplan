export type Role = 'admin' | 'user'

export interface AuthUser {
  id: string
  email: string
  username?: string | null
  full_name: string
  role: Role
  company_id: string | null
  is_active: boolean
  must_change_password: boolean
  last_login_at?: string | null
  created_at: string
  updated_at: string
}

export interface ManagedUser extends AuthUser {}

export interface CreateUserInput {
  email: string
  full_name: string
  role: Role
  company_id: string | null
  temporary_password: string
  must_change_password: boolean
}
