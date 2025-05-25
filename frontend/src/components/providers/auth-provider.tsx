'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { setAuthToken as setApiAuthTokenHeader } from '@/lib/api'

// Define a more comprehensive context type
interface AuthContextType {
  isInitialized: boolean;
  authToken: string | null;
  user: any | null;
  setAuthToken: (token: string | null) => void;
  setUser: (user: any | null) => void;
}

export const AuthContext = createContext<AuthContextType>({
  isInitialized: false,
  authToken: null,
  user: null,
  setAuthToken: () => {},
  setUser: () => {},
})

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isInitialized, setIsInitialized] = useState(false)
  const [authToken, setAuthTokenState] = useState<string | null>(null)
  const [user, setUserState] = useState<any | null>(null)

  // Effect to initialize token and user from localStorage on mount
  useEffect(() => {
    console.log('[AuthProvider] Initialization effect triggered, window type:', typeof window)
    if (typeof window !== 'undefined') {
      console.log('[AuthProvider] Window is defined, starting initialization...')
      const storedToken = localStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('user')
      
      console.log('[AuthProvider] Stored token:', storedToken ? 'exists' : 'null')
      console.log('[AuthProvider] Stored user:', storedUser ? 'exists' : 'null')
      
      if (storedToken) {
        setAuthTokenState(storedToken)
        setApiAuthTokenHeader(storedToken) // Update Axios header
      }
      
      if (storedUser) {
        try {
          setUserState(JSON.parse(storedUser))
        } catch (error) {
          console.error('Error parsing stored user data:', error)
          localStorage.removeItem('user')
        }
      }      
      
      console.log('[AuthProvider] Setting isInitialized to true')
      setIsInitialized(true)
      console.log('[AuthProvider] Initialization completed')
    } else {
      console.log('[AuthProvider] Window is undefined, skipping initialization')
    }
  }, [])

  // Function to set/clear the auth token
  const setAuthToken = useCallback((token: string | null) => {
    console.log('[AuthProvider] setAuthToken called with:', token ? 'TOKEN_PROVIDED' : 'NULL')
    setAuthTokenState(token)
    
    if (token) {
      localStorage.setItem('auth_token', token)
      setApiAuthTokenHeader(token)
      console.log('[AuthProvider] Token stored in localStorage and API header set')
    } else {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user') // Also clear user data when clearing token
      setApiAuthTokenHeader(null)
      setUserState(null)
      console.log('[AuthProvider] Token and user data cleared from localStorage')
    }
  }, [])

  // Function to set/clear the user data
  const setUser = useCallback((userData: any | null) => {
    setUserState(userData)
    
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }, [])

  return (
    <AuthContext.Provider value={{ isInitialized, authToken, user, setAuthToken, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuthProvider = () => useContext(AuthContext)
