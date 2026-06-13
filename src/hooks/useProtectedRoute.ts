import { useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAuth } from '@/contexts/AuthContext';

/**
 * Hook to protect routes - redirects to login if not authenticated
 * @param redirectPath - Where to redirect on login (defaults to /dashboard)
 */
export function useProtectedRoute(redirectPath: string = '/dashboard') {
  const navigate = useNavigate();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate({ to: '/auth', search: { mode: 'login' } });
    }
  }, [isAuthenticated, loading, navigate, redirectPath]);

  return { isProtected: isAuthenticated, loading };
}
