import { createContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { loginRequest, logoutRequest, meRequest } from '@/api/authApi'
import type { AuthUser, Role } from '@/types/auth'

interface AuthContextValue {
  currentUser: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  isAdmin: boolean
  hasRole: (...roles: Role[]) => boolean
  login: (email: string, password: string) => Promise<AuthUser>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = async () => {
    try {
      const user = await meRequest()
      setCurrentUser(user)
    } catch {
      setCurrentUser(null)
    }
  }

  useEffect(() => {
    refreshUser().finally(() => setIsLoading(false))
  }, [])

  // The API client emits this when a request 401s and refresh fails.
  useEffect(() => {
    const handler = () => setCurrentUser(null)
    window.addEventListener('bp:unauthorized', handler)
    return () => window.removeEventListener('bp:unauthorized', handler)
  }, [])

  const login = async (email: string, password: string) => {
    const { user } = await loginRequest(email, password)
    setCurrentUser(user)
    return user
  }

  const logout = async () => {
    try {
      await logoutRequest()
    } finally {
      setCurrentUser(null)
    }
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      currentUser,
      isAuthenticated: !!currentUser,
      isLoading,
      isAdmin: currentUser?.role === 'admin',
      hasRole: (...roles: Role[]) => !!currentUser && roles.includes(currentUser.role),
      login,
      logout,
      refreshUser,
    }),
    [currentUser, isLoading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
