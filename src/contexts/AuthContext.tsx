import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name?: string;
  photo?: string;
  is_new_user?: boolean;
  role?: string;
  is_admin?: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  logout: () => void;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize from localStorage and verify with backend
  useEffect(() => {
    // Check if we're on client side
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');
        
        console.log('🔍 AuthContext: Initializing auth...', { hasToken: !!storedToken, hasUser: !!storedUser });
        
        if (storedToken && storedUser) {
          try {
            // First, try to use stored user data
            const userData = JSON.parse(storedUser);
            console.log('📦 AuthContext: Using stored user data:', userData);
            
            // Then verify token with backend
            console.log('🔄 AuthContext: Verifying token with backend...');
            const response = await fetch('http://localhost:5000/api/auth/me', {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${storedToken}`,
                'Content-Type': 'application/json',
              },
            });

            console.log('📡 AuthContext: Backend response status:', response.status);

            if (response.ok) {
              const data = await response.json();
              console.log('✅ AuthContext: Token verified successfully:', data);
              
              if (data.status === 'success' && data.user) {
                setToken(storedToken);
                setUser(data.user);
                console.log('✅ AuthContext: User set from backend verification');
              } else {
                // Token is invalid, clear localStorage
                console.warn('⚠️ AuthContext: Invalid response from backend');
                localStorage.removeItem('token');
                localStorage.removeItem('user');
              }
            } else {
              // Token verification failed, but use stored user data anyway
              console.warn('⚠️ AuthContext: Backend verification failed, using stored data');
              setToken(storedToken);
              setUser(userData);
            }
          } catch (err) {
            console.error('❌ AuthContext: Token verification error:', err);
            // If backend verification fails, still use stored data
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
          }
        } else {
          console.log('ℹ️ AuthContext: No stored token or user');
        }
      } catch (err) {
        console.error('❌ AuthContext: Failed to initialize auth:', err);
      } finally {
        setLoading(false);
        console.log('✅ AuthContext: Initialization complete');
      }
    };

    initializeAuth();
  }, []);

  // Listen for storage changes (for multi-tab sync)
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const handleStorageChange = (e: StorageEvent) => {
      console.log('🔄 AuthContext: Storage changed:', e.key);
      
      if (e.key === 'token') {
        const newToken = e.newValue;
        setToken(newToken);
        if (!newToken) {
          setUser(null);
        }
      } else if (e.key === 'user') {
        if (e.newValue) {
          try {
            setUser(JSON.parse(e.newValue));
          } catch (err) {
            console.error('Failed to parse user from storage:', err);
          }
        } else {
          setUser(null);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Listen for profile updates
  useEffect(() => {
    // Only on client side
    if (typeof window === 'undefined') {
      return;
    }

    const handleProfileUpdate = (event: Event) => {
      const customEvent = event as CustomEvent;
      setUser(customEvent.detail);
    };

    window.addEventListener('userProfileUpdated', handleProfileUpdate);
    return () => window.removeEventListener('userProfileUpdated', handleProfileUpdate);
  }, []);

  const logout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    setToken(null);
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    logout,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
