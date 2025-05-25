'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useNewsletters } from '@/hooks/useNewsletters'
import { useAuth } from '@/hooks/useAuth'
import DashboardLayout from '@/components/dashboard/layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { 
  Plus, 
  Search, 
  Calendar, 
  Eye, 
  Edit, 
  Trash2, 
  Send,
  FileText,
  Clock,
  CheckCircle
} from 'lucide-react'
import { formatRelativeDate } from '@/lib/utils'

export default function NewslettersPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading: authLoading, user } = useAuth()
  const { newsletters, isLoading, error, deleteNewsletter, sendNewsletter, isDeleting, isSending } = useNewsletters()
  const [searchTerm, setSearchTerm] = useState('')
  // Handle clicking on a newsletter card
  const handleNewsletterClick = (newsletter: any) => {
    // Always navigate to preview page when clicking on the card
    router.push(`/dashboard/newsletters/${newsletter.id}/preview`)
  }

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login?redirect=/dashboard/newsletters')
    }
  }, [isAuthenticated, authLoading, router])

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Checking authentication...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  // Don't render anything if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null
  }

  const filteredNewsletters = newsletters?.filter(newsletter =>
    newsletter.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    newsletter.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'scheduled':
        return <Clock className="h-4 w-4 text-blue-500" />
      default:
        return <FileText className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800'
      case 'scheduled':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (    <DashboardLayout>
      <div className="space-y-8">
        {/* Enhanced Header */}
        <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 rounded-2xl p-8 border border-blue-100">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Newsletter Hub
              </h1>
              <p className="mt-2 text-lg text-gray-600 font-medium">
                Create, manage, and send engaging newsletters to your subscribers
              </p>
              <div className="mt-4 flex items-center space-x-6 text-sm text-gray-500">
                <span className="flex items-center">
                  <FileText className="h-4 w-4 mr-2" />
                  {newsletters?.length || 0} Total
                </span>
                <span className="flex items-center">
                  <FileText className="h-4 w-4 mr-2 text-yellow-500" />
                  {newsletters?.filter(n => n.status === 'draft').length || 0} Drafts
                </span>
                <span className="flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  {newsletters?.filter(n => n.status === 'published').length || 0} Published
                </span>
              </div>
            </div>
            <Link href="/dashboard/newsletters/new">
              <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-6 py-3">
                <Plus className="h-5 w-5 mr-2" />
                Create Newsletter
              </Button>
            </Link>
          </div>
        </div>        {/* Enhanced Search and Filters */}
        <Card className="bg-gradient-to-r from-white to-gray-50 border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <Input
                  placeholder="Search newsletters by title or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-11 py-3 text-lg border-gray-200 focus:border-blue-300 focus:ring-blue-200 rounded-xl"
                />
              </div>
              <Button 
                variant="outline" 
                className="px-6 py-3 border-gray-200 hover:border-blue-300 hover:bg-blue-50 rounded-xl"
              >
                <FileText className="h-4 w-4 mr-2" />
                Filter
              </Button>
            </div>
          </CardContent>
        </Card>{/* Newsletters List */}
        {error ? (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-red-500 mb-4">
                <FileText className="h-12 w-12 mx-auto mb-4" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Failed to load newsletters
              </h3>              <p className="text-gray-500 mb-4">
                {error.message || 'An error occurred while loading newsletters.'}
              </p>
              <Button onClick={() => window.location.reload()}>
                Try Again
              </Button>
            </CardContent>
          </Card>
        ) : isLoading ? (
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
          </div>        ) : filteredNewsletters.length === 0 ? (
          <Card className="bg-gradient-to-br from-gray-50 to-gray-100 border-dashed border-2 border-gray-300">
            <CardContent className="p-16 text-center">
              <div className="bg-blue-100 rounded-full p-6 w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <FileText className="h-12 w-12 text-blue-600" />
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                {searchTerm ? 'No newsletters found' : 'Ready to create your first newsletter?'}
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto text-lg">
                {searchTerm 
                  ? 'Try adjusting your search terms or create a new newsletter.' 
                  : 'Start building engaging newsletters to connect with your audience and share valuable content.'
                }
              </p>
              <div className="space-y-3">
                <Link href="/dashboard/newsletters/new">
                  <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 text-lg">
                    <Plus className="h-5 w-5 mr-2" />
                    Create Your First Newsletter
                  </Button>
                </Link>
                {searchTerm && (
                  <div>
                    <Button 
                      variant="outline" 
                      onClick={() => setSearchTerm('')}
                      className="mt-3"
                    >
                      Clear Search
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (          <div className="grid gap-6">
            {filteredNewsletters.map((newsletter) => (
              <Card 
                key={newsletter.id} 
                className="hover:shadow-lg hover:shadow-blue-100 transition-all duration-300 border border-gray-200 hover:border-blue-200 cursor-pointer group"
                onClick={() => handleNewsletterClick(newsletter)}
              >
                <CardContent className="p-6">                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-3">
                        {getStatusIcon(newsletter.status)}
                        <h3 className="text-xl font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                          {newsletter.title}
                        </h3>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(newsletter.status)}`}>
                          {newsletter.status}
                        </span>
                      </div>
                      
                      {newsletter.description && (
                        <p className="text-gray-600 mb-4 line-clamp-2 leading-relaxed">
                          {newsletter.description}
                        </p>
                      )}
                      
                      <div className="flex items-center space-x-6 text-sm text-gray-500">
                        <span className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          Created {formatRelativeDate(newsletter.created_at)}
                        </span>
                        {newsletter.scheduled_for && (
                          <span className="flex items-center text-blue-600">
                            <Clock className="h-4 w-4 mr-1" />
                            Scheduled for {formatRelativeDate(newsletter.scheduled_for)}
                          </span>
                        )}                        {newsletter.status === 'draft' && (
                          <span className="text-blue-600 text-xs font-medium bg-blue-50 px-2 py-1 rounded">
                            Click to preview
                          </span>
                        )}
                      </div>
                    </div>                      <div className="flex items-center space-x-2 ml-4" onClick={(e) => e.stopPropagation()}>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="hover:bg-blue-50 hover:text-blue-600"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/dashboard/newsletters/${newsletter.id}/preview`);
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="hover:bg-green-50 hover:text-green-600"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/dashboard/newsletters/${newsletter.id}`);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      {newsletter.status === 'draft' && (
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            sendNewsletter(newsletter.id);
                          }}
                          disabled={isSending}
                          className="hover:bg-green-50 hover:text-green-600"
                        >
                          <Send className="h-4 w-4" />
                        </Button>
                      )}
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNewsletter(newsletter.id);
                        }}
                        disabled={isDeleting}
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
        )}        {/* Enhanced Stats Summary */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-blue-500 rounded-xl">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-blue-700">Total Newsletters</p>
                  <p className="text-3xl font-bold text-blue-900">
                    {newsletters?.length || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200 hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-green-500 rounded-xl">
                  <CheckCircle className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-green-700">Published</p>
                  <p className="text-3xl font-bold text-green-900">
                    {newsletters?.filter(n => n.status === 'published').length || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200 hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-yellow-500 rounded-xl">
                  <Clock className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-yellow-700">Drafts</p>
                  <p className="text-3xl font-bold text-yellow-900">
                    {newsletters?.filter(n => n.status === 'draft').length || 0}
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
