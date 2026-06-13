import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { createClient } from '@supabase/supabase-js';

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
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Initialize Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://zckmfdcdfemnkfjfuujb.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || 'sb_publishable_0x82kaK8XFyTmK5_dm8e_w_ZOAluzWP';
const supabase = createClient(supabaseUrl, supabaseKey);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize from Supabase (not localStorage)
  useEffect(() => {
    // Check if we're on client side
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    const initializeAuth = async () => {
      try {
        // Read token from sessionStorage (session-based)
        // But also check localStorage as fallback for persistence across page reloads
        let storedToken = sessionStorage.getItem('token');
        if (!storedToken) {
          storedToken = localStorage.getItem('token');
        }
        
        console.log('🔍 AuthContext: Initializing auth...', { hasToken: !!storedToken });
        
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
        
        if (storedToken) {
          try {
            // Verify token with backend
            console.log('🔄 AuthContext: Verifying token with backend...', { API_URL });
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch(`${API_URL}/api/auth/me`, {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${storedToken}`,
                'Content-Type': 'application/json',
              },
              signal: controller.signal,
            });
            
            clearTimeout(timeout);
            console.log('📡 AuthContext: Backend response status:', response.status);

            if (response.ok) {
              const data = await response.json();
              console.log('✅ AuthContext: Token verified successfully:', data);
              
              if (data.status === 'success' && data.user) {
                setToken(storedToken);
                setUser(data.user);
                console.log('✅ AuthContext: User set from backend verification');
              } else {
                // Token is invalid, clear storage
                console.warn('⚠️ AuthContext: Invalid response from backend');
                sessionStorage.removeItem('token');
                sessionStorage.removeItem('user');
                localStorage.removeItem('token');
                localStorage.removeItem('user');
              }
            } else if (response.status === 401) {
              // Unauthorized - token expired
              console.warn('⚠️ AuthContext: Token expired (401)');
              sessionStorage.removeItem('token');
              sessionStorage.removeItem('user');
              localStorage.removeItem('token');
              localStorage.removeItem('user');
            } else {
              // Other error - keep token but try to restore user
              console.warn('⚠️ AuthContext: Backend error (status:', response.status + '), keeping token');
              setToken(storedToken);
              
              // Try to restore user from storage
              const storedUser = sessionStorage.getItem('user') || localStorage.getItem('user');
              if (storedUser) {
                try {
                  setUser(JSON.parse(storedUser));
                  console.log('ℹ️ AuthContext: Restored user from storage');
                } catch (e) {
                  console.error('Failed to parse stored user');
                }
              }
            }
          } catch (err) {
            console.error('❌ AuthContext: Token verification error:', err);
            // On network error, keep the token AND try to restore user
            setToken(storedToken);
            
            // Try to restore user from storage
            const storedUser = sessionStorage.getItem('user') || localStorage.getItem('user');
            if (storedUser) {
              try {
                setUser(JSON.parse(storedUser));
                console.log('ℹ️ AuthContext: Restored user from storage (network issue)');
              } catch (e) {
                console.error('Failed to parse stored user');
              }
            }
            
            console.log('ℹ️ AuthContext: Kept token & user despite verification error');
          }
        } else {
          console.log('ℹ️ AuthContext: No stored token');
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
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
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
    return () => {
      window.removeEventListener('userProfileUpdated', handleProfileUpdate);
    };
  }, []);

  const logout = () => {
    console.log('🔓 AuthContext: Logout initiated');
    
    if (typeof window !== 'undefined') {
      // Force clear ALL storage
      try {
        sessionStorage.clear();
        localStorage.clear();
        console.log('✅ All storage cleared');
      } catch (e) {
        console.error('Failed to clear storage:', e);
        // Fallback: clear individually
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    
    // Force reset state
    setToken(null);
    setUser(null);
    setLoading(false);
    
    console.log('✅ Logout complete - state reset');
  };

  const refreshAuth = async () => {
    console.log('🔄 AuthContext: Refreshing auth...');
    let storedToken = sessionStorage.getItem('token');
    if (!storedToken) {
      storedToken = localStorage.getItem('token');
    }
    
    if (storedToken) {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${storedToken}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success' && data.user) {
            setToken(storedToken);
            setUser(data.user);
            console.log('✅ Auth refreshed from backend');
          }
        } else if (response.status === 401) {
          // Token expired
          setToken(null);
          setUser(null);
          sessionStorage.clear();
          localStorage.clear();
        } else {
          // Try to restore from storage
          const storedUser = sessionStorage.getItem('user') || localStorage.getItem('user');
          if (storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
            console.log('✅ Auth restored from storage');
          }
        }
      } catch (err) {
        console.error('Auth refresh error:', err);
        // Keep token and restore user from storage
        const storedUser = sessionStorage.getItem('user') || localStorage.getItem('user');
        if (storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
        }
      }
    }
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    logout,
    setUser,
    refreshAuth,
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
