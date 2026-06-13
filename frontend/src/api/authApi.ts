import { api } from './client'
import type { AuthUser } from '@/types/auth'

export function loginRequest(email: string, password: string) {
  return api.post<{ user: AuthUser }>('/auth/login', { email, password })
}

export function logoutRequest() {
  return api.post<{ message: string }>('/auth/logout')
}

export function meRequest() {
  return api.get<AuthUser>('/auth/me')
}

export function changePasswordRequest(current_password: string, new_password: string) {
  return api.post<{ message: string }>('/auth/change-password', { current_password, new_password })
}
