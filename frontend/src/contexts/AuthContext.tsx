import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import apiClient from '../services/api';

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for OAuth errors in URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const oauthError = urlParams.get('error');
        const oauthMessage = urlParams.get('message');
        
        if (oauthError) {
          console.error('OAuth error:', oauthError, oauthMessage);
          // Clear URL parameters
          window.history.replaceState({}, document.title, window.location.pathname);
          // You could show an error message here
        }
        
        // Check for tokens in URL fragment (from Google OAuth)
        const hash = window.location.hash;
        if (hash) {
          const params = new URLSearchParams(hash.substring(1));
          const accessToken = params.get('access_token');
          const refreshToken = params.get('refresh_token');
          const isNewUser = params.get('is_new_user') === 'true';
          const authMethod = params.get('auth_method');
          
          if (accessToken && refreshToken) {
            // Store tokens from OAuth
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
            
            // Set token in API client
            apiClient.setAuthToken(accessToken);
            
            // Get user info from API
            try {
              const userResponse = await apiClient.getCurrentUser();
              const userData = userResponse.data;
              localStorage.setItem('user', JSON.stringify(userData));
              setUser(userData);
              
              // Clear URL fragment
              window.location.hash = '';
              
              // Redirect to home page
              window.location.href = '/';
              return;
            } catch (userError) {
              console.error('Failed to get user info:', userError);
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
            }
          }
        }
        
        // Check for stored tokens
        const token = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('user');
        
        if (token && storedUser) {
          // Set token in API client
          apiClient.setAuthToken(token);
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const value = {
    user,
    setUser,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export { AuthContext };