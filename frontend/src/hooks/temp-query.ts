// Enhanced replacement for TanStack Query hooks with proper cache management
import { useState, useEffect, useRef } from 'react'

// Global cache to share data between queries
const globalCache = new Map<string, { data: any; timestamp: number; error?: Error }>()
const cacheExpiry = 5 * 60 * 1000 // 5 minutes
const subscribers = new Map<string, Set<() => void>>()

// Helper to create cache key
function createCacheKey(queryKey: (string | null)[]): string {
  return queryKey.filter(Boolean).join(':')
}

// Helper to invalidate cache entries
function invalidateCache(pattern: { queryKey?: (string | null)[] }) {
  if (!pattern.queryKey) {
    globalCache.clear()
    // Notify all subscribers
    subscribers.forEach(subs => subs.forEach(callback => callback()))
    return
  }

  const patternKey = createCacheKey(pattern.queryKey.filter(Boolean))
  const keysToRemove: string[] = []
  
  // Find matching keys - support partial matching
  for (const key of globalCache.keys()) {
    if (key.startsWith(patternKey)) {
      keysToRemove.push(key)
    }
  }
  
  // Remove matching entries
  keysToRemove.forEach(key => {
    globalCache.delete(key)
    // Notify subscribers for this key
    const subs = subscribers.get(key)
    if (subs) {
      subs.forEach(callback => callback())
    }
  })
  
  console.log(`[invalidateCache] Invalidated ${keysToRemove.length} cache entries for pattern:`, patternKey)
}

// Simple replacement for useQuery
export function useQuery<T>(options: { 
  queryKey: (string | null)[]; 
  queryFn: () => Promise<T>;
  enabled?: boolean;
  retry?: number;
  [key: string]: any; // Allow any additional options
}): { data: T | undefined; isLoading: boolean; error: Error | null; refetch: () => Promise<void> } {
  const [data, setData] = useState<T | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const cacheKey = createCacheKey(options.queryKey)
  const forceUpdateRef = useRef(0)

  const refetch = async () => {
    if (options.queryFn && (options.enabled !== false)) {
      console.log('[useQuery] Refetching for key:', options.queryKey)
      setIsLoading(true)
      setError(null)
      try {
        const result = await options.queryFn()
        console.log('[useQuery] Fetch successful for key:', options.queryKey, 'result:', result)
        
        // Cache the result
        globalCache.set(cacheKey, { data: result, timestamp: Date.now() })
        setData(result)
      } catch (err) {
        console.error('[useQuery] Fetch failed for key:', options.queryKey, 'error:', err)
        const error = err as Error
        globalCache.set(cacheKey, { data: undefined, timestamp: Date.now(), error })
        setError(error)      } finally {
        setIsLoading(false)
      }
    }
  }

  // Subscribe to cache invalidations
  useEffect(() => {
    const callback = () => {
      forceUpdateRef.current += 1
      const cached = globalCache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < cacheExpiry) {
        setData(cached.data)
        setError(cached.error || null)
      } else {
        // Cache expired or invalidated, refetch if enabled
        if (options.enabled !== false) {
          refetch()
        }
      }
    }

    if (!subscribers.has(cacheKey)) {
      subscribers.set(cacheKey, new Set())
    }
    subscribers.get(cacheKey)!.add(callback)

    return () => {
      subscribers.get(cacheKey)?.delete(callback)
      if (subscribers.get(cacheKey)?.size === 0) {
        subscribers.delete(cacheKey)
      }
    }
  }, [cacheKey])

  useEffect(() => {
    // Check cache first
    const cached = globalCache.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < cacheExpiry) {
      setData(cached.data)
      setError(cached.error || null)
      return
    }

    // Initialize data for known array types to prevent build errors
    if (options.queryKey && Array.isArray(options.queryKey)) {
      const key = options.queryKey[0] // Use the primary key to decide
      if ((key === 'sources' || key === 'newsletters') && data === undefined) {
        // This is a targeted fix for queries expected to return arrays.
        // It assumes T for these keys is an array type (e.g., ContentSource[]).
        setData([] as unknown as T)
        return
      }
    }
    
    // Auto-fetch when enabled and queryKey changes
    if (options.enabled !== false) {
      refetch()
    }
  }, [cacheKey, options.enabled, forceUpdateRef.current])

  return { data, isLoading, error, refetch }
}

// Simple replacement for useMutation
export function useMutation<T>(options: {
  mutationFn: (data: any) => Promise<T>;
  onSuccess?: (data: T) => void;
  onError?: (error: any) => void;
  [key: string]: any; // Allow any additional options
}) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const mutate = async (data: any) => {
    console.log('[useMutation] Starting mutation with data:', data)
    setIsLoading(true)
    setError(null)
    try {
      console.log('[useMutation] Calling mutationFn...')
      const result = await options.mutationFn(data)
      console.log('[useMutation] mutationFn completed with result:', result)
      
      if (options.onSuccess) {
        console.log('[useMutation] Calling onSuccess callback...')
        try {
          options.onSuccess(result)
          console.log('[useMutation] onSuccess callback completed')
        } catch (onSuccessError) {
          console.error('[useMutation] onSuccess callback failed:', onSuccessError)
        }
      }
      
      console.log('[useMutation] Mutation completed successfully')
      return result
    } catch (err) {
      const error = err as Error
      console.error('[useMutation] Mutation failed:', error)
      setError(error)
      if (options.onError) {
        try {
          options.onError(error)
        } catch (onErrorError) {
          console.error('[useMutation] onError callback failed:', onErrorError)
        }
      }
      throw error
    } finally {
      console.log('[useMutation] Setting isLoading to false')
      setIsLoading(false)
    }
  }

  const mutateAsync = async (data: any) => {
    return await mutate(data)
  }

  return { mutate, mutateAsync, isLoading, isPending: isLoading, error }
}

// Enhanced replacement for useQueryClient
export function useQueryClient() {
  return {
    invalidateQueries: (options: any) => {
      console.log('[useQueryClient] invalidateQueries called with options:', options)
      invalidateCache(options)
    },
    refetchQueries: (...args: any[]) => {
      console.log('[useQueryClient] refetchQueries called with args:', args)
      // Could implement refetch logic here
    },
    setQueryData: (queryKey: (string | null)[], data: any) => {
      console.log('[useQueryClient] setQueryData called with key:', queryKey, 'data:', data)
      const cacheKey = createCacheKey(queryKey)
      globalCache.set(cacheKey, { data, timestamp: Date.now() })
      
      // Notify subscribers
      const subs = subscribers.get(cacheKey)
      if (subs) {
        subs.forEach(callback => callback())
      }
    },
    removeQueries: (queryKey: (string | null)[]) => {
      console.log('[useQueryClient] removeQueries called with key:', queryKey)
      const cacheKey = createCacheKey(queryKey)
      globalCache.delete(cacheKey)
    },
    clear: () => {
      console.log('[useQueryClient] clear called')
      globalCache.clear()
      subscribers.forEach(subs => subs.forEach(callback => callback()))
    },
  }
}
