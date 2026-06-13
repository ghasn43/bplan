import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { LoadingScreen } from '@/components/ui/Spinner'
import { useAuth } from './useAuth'

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()
  if (isLoading) return <LoadingScreen label="Loading…" />
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return <Outlet />
}

export function AdminRoute() {
  const { isAdmin, isLoading } = useAuth()
  if (isLoading) return <LoadingScreen label="Loading…" />
  if (!isAdmin) return <Navigate to="/projects" replace />
  return <Outlet />
}
