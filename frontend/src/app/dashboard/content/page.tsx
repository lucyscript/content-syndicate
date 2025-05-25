'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/hooks/temp-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { contentAPI, type ContentSource } from '@/lib/api'
import DashboardLayout from '@/components/dashboard/layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Plus, 
  Search, 
  Globe, 
  Rss, 
  Twitter,
  Youtube,
  Linkedin,
  Edit,
  Trash2,
  ExternalLink,
  RefreshCw,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { formatRelativeDate } from '@/lib/utils'

const sourceSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  url: z.string().url('Please enter a valid URL'),
  source_type: z.string().min(1, 'Source type is required'),
})

type SourceFormData = z.infer<typeof sourceSchema>

export default function ContentSourcesPage() {
  const queryClient = useQueryClient()
  const [isAddingSource, setIsAddingSource] = useState(false)
  const [editingSource, setEditingSource] = useState<ContentSource | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  const { data: sources, isLoading } = useQuery({
    queryKey: ['content', 'sources'],
    queryFn: () => contentAPI.getSources().then(res => res.data),
  })

  const addSourceMutation = useMutation({
    mutationFn: (data: Partial<ContentSource>) => 
      contentAPI.addSource(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', 'sources'] })
      setIsAddingSource(false)
      reset()
    },
  })

  const updateSourceMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ContentSource> }) =>
      contentAPI.updateSource(id, data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', 'sources'] })
      setEditingSource(null)
      reset()
    },
  })

  const deleteSourceMutation = useMutation({
    mutationFn: (id: number) => contentAPI.deleteSource(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', 'sources'] })
    },
  })

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<SourceFormData>({
    resolver: zodResolver(sourceSchema),
  })

  const filteredSources = sources?.filter(source =>
    source.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    source.url.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const getSourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'rss':
        return <Rss className="h-5 w-5 text-orange-500" />
      case 'twitter':
        return <Twitter className="h-5 w-5 text-blue-500" />
      case 'youtube':
        return <Youtube className="h-5 w-5 text-red-500" />
      case 'linkedin':
        return <Linkedin className="h-5 w-5 text-blue-600" />
      default:
        return <Globe className="h-5 w-5 text-gray-500" />
    }
  }

  const onSubmit = (data: SourceFormData) => {
    if (editingSource) {
      updateSourceMutation.mutate({ id: editingSource.id, data })
    } else {
      addSourceMutation.mutate({ ...data, is_active: true })
    }
  }

  const handleEdit = (source: ContentSource) => {
    setEditingSource(source)
    setValue('name', source.name)
    setValue('url', source.url)
    setValue('source_type', source.source_type)
    setIsAddingSource(true)
  }

  const handleCancel = () => {
    setIsAddingSource(false)
    setEditingSource(null)
    reset()
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Content Sources</h1>
            <p className="mt-1 text-sm text-gray-500">
              Manage your content sources for automated newsletter generation.
            </p>
          </div>
          <Button onClick={() => setIsAddingSource(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Source
          </Button>
        </div>

        {/* Add/Edit Source Form */}
        {isAddingSource && (
          <Card>
            <CardHeader>
              <CardTitle>
                {editingSource ? 'Edit Content Source' : 'Add New Content Source'}
              </CardTitle>
              <CardDescription>
                Add RSS feeds, social media accounts, or websites to automatically pull content from.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                      Source Name *
                    </label>
                    <Input
                      id="name"
                      placeholder="e.g., TechCrunch RSS"
                      {...register('name')}
                    />
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <label htmlFor="source_type" className="block text-sm font-medium text-gray-700 mb-1">
                      Source Type *
                    </label>
                    <select
                      id="source_type"
                      className="block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                      {...register('source_type')}
                    >
                      <option value="">Select type...</option>
                      <option value="rss">RSS Feed</option>
                      <option value="twitter">Twitter</option>
                      <option value="youtube">YouTube</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="website">Website</option>
                      <option value="blog">Blog</option>
                    </select>
                    {errors.source_type && (
                      <p className="mt-1 text-sm text-red-600">{errors.source_type.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                    URL *
                  </label>
                  <Input
                    id="url"
                    type="url"
                    placeholder="https://example.com/feed.xml"
                    {...register('url')}
                  />
                  {errors.url && (
                    <p className="mt-1 text-sm text-red-600">{errors.url.message}</p>
                  )}
                </div>

                <div className="flex justify-end space-x-3">
                  <Button type="button" variant="outline" onClick={handleCancel}>
                    Cancel
                  </Button>
                  <Button 
                    type="submit" 
                    disabled={addSourceMutation.isPending || updateSourceMutation.isPending}
                  >
                    {editingSource ? 'Update Source' : 'Add Source'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Search */}
        <Card>
          <CardContent className="p-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search content sources..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Sources List */}
        {isLoading ? (
          <div className="grid gap-4">
            {[...Array(3)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="animate-pulse">
                    <div className="h-6 bg-gray-200 rounded w-1/3 mb-2" />
                    <div className="h-4 bg-gray-200 rounded w-2/3 mb-4" />
                    <div className="h-4 bg-gray-200 rounded w-1/4" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredSources.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Globe className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm ? 'No sources found' : 'No content sources yet'}
              </h3>
              <p className="text-gray-500 mb-4">
                {searchTerm 
                  ? 'Try adjusting your search terms.' 
                  : 'Add your first content source to start aggregating content automatically.'
                }
              </p>
              {!searchTerm && (
                <Button onClick={() => setIsAddingSource(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Content Source
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {filteredSources.map((source) => (
              <Card key={source.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="flex-shrink-0">
                        {getSourceIcon(source.source_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-medium text-gray-900 truncate">
                            {source.name}
                          </h3>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            source.is_active 
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {source.is_active ? (
                              <>
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Active
                              </>
                            ) : (
                              <>
                                <XCircle className="h-3 w-3 mr-1" />
                                Inactive
                              </>
                            )}
                          </span>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {source.source_type}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-2 mb-3">
                          <a 
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-500 flex items-center"
                          >
                            {source.url}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        </div>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>Added {formatRelativeDate(source.created_at)}</span>
                          {source.last_crawled && (
                            <span className="flex items-center">
                              <RefreshCw className="h-4 w-4 mr-1" />
                              Last crawled {formatRelativeDate(source.last_crawled)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleEdit(source)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => deleteSourceMutation.mutate(source.id)}
                        disabled={deleteSourceMutation.isPending}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Stats Summary */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Globe className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Sources</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {sources?.length || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-6 w-6 text-green-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Active Sources</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {sources?.filter(s => s.is_active).length || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Rss className="h-6 w-6 text-orange-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">RSS Feeds</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {sources?.filter(s => s.source_type === 'rss').length || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
