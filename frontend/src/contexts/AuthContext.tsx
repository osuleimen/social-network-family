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
        // For demo purposes, create a demo user if no user is found
        const storedUser = localStorage.getItem('user');
        
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        } else {
          // Create a demo user for demonstration
          const demoUser = {
            id: 'demo-user-123',
            username: 'demo_user',
            display_name: 'Demo User',
            email: 'demo@example.com',
            bio: 'Demo user for testing',
            avatar_media_id: null,
            verified: false,
            private_account: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
          
          localStorage.setItem('user', JSON.stringify(demoUser));
          setUser(demoUser);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // Create demo user even if there's an error
        const demoUser = {
          id: 'demo-user-123',
          username: 'demo_user',
          display_name: 'Demo User',
          email: 'demo@example.com',
          bio: 'Demo user for testing',
          avatar_media_id: null,
          verified: false,
          private_account: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        localStorage.setItem('user', JSON.stringify(demoUser));
        setUser(demoUser);
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