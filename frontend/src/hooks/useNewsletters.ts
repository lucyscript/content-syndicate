import { useMutation, useQuery, useQueryClient } from './temp-query'
import { newsletterAPI, type Newsletter, type ContentGenerationRequest } from '@/lib/api'
import { useAuth } from './useAuth'

export const useNewsletters = () => {
  const queryClient = useQueryClient()
  const { isAuthenticated, user } = useAuth()
  const { data: newsletters, isLoading, error } = useQuery({
    queryKey: ['newsletters', user?.id],
    queryFn: () => newsletterAPI.getAll().then(res => res.data),
    enabled: isAuthenticated, // Only fetch when authenticated
  })
  
  const createMutation = useMutation({
    mutationFn: (data: Partial<Newsletter>) => 
      newsletterAPI.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id] })
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id, 'single'] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Newsletter> }) =>
      newsletterAPI.update(id, data).then(res => res.data),
    onSuccess: (result: Newsletter) => {
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id] })
      // Invalidate all single newsletter queries for this user
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id, 'single'] })
      // Also update the specific cache entry
      if (result.id) {
        queryClient.setQueryData(['newsletters', user?.id, 'single', result.id.toString()], result)
      }
    },
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => newsletterAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id] })
      // Invalidate all single newsletter queries for this user      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id, 'single'] })
    },
  })
  
  const generateContentMutation = useMutation({
    mutationFn: ({ id, request }: { id: number; request: ContentGenerationRequest }) => 
      newsletterAPI.generateContent(id, request).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id] })
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id, 'single'] })
    },
  })

  const sendMutation = useMutation({
    mutationFn: (id: number) => newsletterAPI.send(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id] })
      queryClient.invalidateQueries({ queryKey: ['newsletters', user?.id, 'single'] })
    },
  })
  return {
    newsletters,
    isLoading,
    error,
    createNewsletter: createMutation.mutate,
    createNewsletterAsync: createMutation.mutateAsync,
    updateNewsletter: updateMutation.mutate,
    deleteNewsletter: deleteMutation.mutate,
    generateContent: generateContentMutation.mutate,
    generateContentAsync: generateContentMutation.mutateAsync,
    sendNewsletter: sendMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isGeneratingContent: generateContentMutation.isPending,
    isSending: sendMutation.isPending,
  }
}

export const useNewsletter = (id: number) => {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  
  const { data: newsletter, isLoading, error } = useQuery({
    queryKey: ['newsletters', user?.id, 'single', id.toString()],
    queryFn: () => newsletterAPI.getById(id).then(res => res.data),
    enabled: !!id,
  })

  return {
    newsletter,
    isLoading,
    error,
  }
}
