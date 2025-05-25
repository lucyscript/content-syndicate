import { useEffect, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '../hooks/temp-query'
import { useRouter } from 'next/navigation'
import { authAPI, type LoginCredentials, type RegisterData, type User, type AuthResponse as ApiAuthResponse } from '@/lib/api'
import { useAuthProvider } from '../components/providers/auth-provider'

export const useAuth = () => {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { authToken, user: storedUser, setAuthToken, setUser, isInitialized } = useAuthProvider()
  const { data: user, isLoading: userLoading, refetch: refetchUser, error: userError } = useQuery<User>({
    queryKey: ['currentUser', authToken],
    queryFn: async () => {
      if (!isInitialized) {
        console.warn('useAuth: queryFn called before AuthProvider is initialized.')
        throw new Error('Auth provider not initialized')
      }
      if (!authToken) {
        console.warn('useAuth: queryFn called without authToken.')
        throw new Error('No auth token available')
      }
      const response = await authAPI.getCurrentUser()
      return response.data
    },
    enabled: isInitialized && !!authToken, // Only run if provider is initialized and token exists
    retry: 1,
  })

  useEffect(() => {
    console.log('[useAuth] AuthToken:', authToken);
    console.log('[useAuth] User from query:', user);
    console.log('[useAuth] IsInitialized:', isInitialized);
    console.log('[useAuth] UserLoading:', userLoading);
    if (userError) {
      console.error('[useAuth] User query error:', userError);
    }
  }, [user, authToken, isInitialized, userLoading, userError]);  useEffect(() => {
    if (isInitialized && !authToken) {
      queryClient.setQueryData(['currentUser', authToken], null)
      queryClient.removeQueries(['currentUser'])
    }
  }, [authToken, isInitialized, queryClient])

  // Fix the login mutation to properly use AuthProvider's setAuthToken and setUser
  const loginMutation = useMutation<ApiAuthResponse>({
    mutationFn: async (credentials: LoginCredentials) => {
      console.log('[loginMutation] Starting login with credentials:', { email: credentials.email })
      const response = await authAPI.login(credentials)
      console.log('[loginMutation] Login API call successful:', response.data)
      return response.data
    },    onSuccess: async (data: ApiAuthResponse) => {
      console.log('[loginMutation] onSuccess called with data:', data)
      
      // Set the auth token first
      console.log('[loginMutation] Setting auth token...')
      setAuthToken(data.access_token)
      console.log('[loginMutation] Auth token set successfully')
      
      // Fetch and store user data immediately
      try {
        console.log('[loginMutation] Fetching user data...')
        const userResponse = await authAPI.getCurrentUser()
        console.log('[loginMutation] User data fetched successfully:', userResponse.data)
        setUser(userResponse.data)
        console.log('[loginMutation] User data stored in localStorage')
      } catch (error) {
        console.error('[loginMutation] Failed to fetch user data:', error)
        // Don't fail the login if user fetch fails
      }
      
      console.log('[loginMutation] Invalidating currentUser queries...')
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
      console.log('[loginMutation] Queries invalidated, navigating to dashboard...')
      
      router.push('/dashboard')
      console.log('[loginMutation] onSuccess completed')
    },
    onError: (error) => {
      console.error('[loginMutation] Login failed:', error)
      // Consider setting a specific login error state here if needed for the UI
    }
  })
  const registerMutation = useMutation<User>({
    mutationFn: async (data: RegisterData): Promise<User> => { // Using async/await
      const response = await authAPI.register(data)
      return response.data // This should be type User
    },
    onSuccess: () => {
      router.push('/auth/login?registrationSuccess=true')
    },
    onError: (error) => {
      console.error('Registration failed:', error)
    }
  })
  const logout = useCallback(() => {
    setAuthToken(null) // Clear token using AuthProvider (also clears user)
    queryClient.clear() // Clear all cached queries
    router.push('/auth/login')
  }, [setAuthToken, router, queryClient])

  // Use stored user if available, otherwise use the fetched user from the query
  const currentUser = storedUser || user
  const isAuthenticated = isInitialized && !!authToken && !!currentUser;

  useEffect(() => {
    console.log('[useAuth] IsAuthenticated calculated:', isAuthenticated);
  }, [isAuthenticated]);
  return {
    user: currentUser || null,
    isAuthenticated,
    isLoading: !isInitialized || userLoading || loginMutation.isPending || registerMutation.isPending,
    login: loginMutation.mutateAsync,
    register: registerMutation.mutateAsync,
    logout,
    refetchUser, 
    authError: userError, 
  }
}
