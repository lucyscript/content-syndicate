'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useNewsletters, useNewsletter } from '@/hooks/useNewsletters'
import { useAuth } from '@/hooks/useAuth'
import DashboardLayout from '@/components/dashboard/layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { 
  ArrowLeft, 
  Save, 
  Send, 
  Eye, 
  Trash2,
  Calendar,
  FileText,
  Loader2
} from 'lucide-react'
import Link from 'next/link'

export default function EditNewsletterPage() {
  const router = useRouter()
  const params = useParams()
  const newsletterId = parseInt(params.id as string)
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  
  // Use individual newsletter hook instead of finding from array
  const { newsletter, isLoading: newsletterLoading, error: newsletterError } = useNewsletter(newsletterId)
  
  const { 
    updateNewsletter, 
    deleteNewsletter, 
    sendNewsletter,
    isUpdating,
    isDeleting,
    isSending 
  } = useNewsletters()
  
  const [formData, setFormData] = useState({
    title: '',
    subject_line: '',
    content: '',
    target_audience: '',
    scheduled_for: ''
  })
  
  const [isMounted, setIsMounted] = useState(false)
  
  useEffect(() => {
    setIsMounted(true)
  }, [])
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login?redirect=/dashboard/newsletters')
    }
  }, [isAuthenticated, authLoading, router])
  
  // Load newsletter data into form when newsletter is fetched
  useEffect(() => {
    if (newsletter) {
      setFormData({
        title: newsletter.title || '',
        subject_line: newsletter.subject_line || '',
        content: newsletter.content || '',
        target_audience: newsletter.target_audience || '',
        scheduled_for: newsletter.scheduled_for ? 
          new Date(newsletter.scheduled_for).toISOString().slice(0, 16) : ''
      })
    }
  }, [newsletter])
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }
  
  const handleSave = async () => {
    if (!newsletter) return
    
    try {
      await updateNewsletter({ 
        id: newsletter.id, 
        data: {
          ...formData,
          scheduled_for: formData.scheduled_for || null
        }
      })
      // Success handled by hook
    } catch (error) {
      console.error('Failed to update newsletter:', error)
    }
  }
  
  const handleSend = async () => {
    if (!newsletter) return
    
    try {
      await sendNewsletter(newsletter.id)
      router.push('/dashboard/newsletters')
    } catch (error) {
      console.error('Failed to send newsletter:', error)
    }
  }
  
  const handleDelete = async () => {
    if (!newsletter || !confirm('Are you sure you want to delete this newsletter?')) return
    
    try {
      await deleteNewsletter(newsletter.id)
      router.push('/dashboard/newsletters')
    } catch (error) {
      console.error('Failed to delete newsletter:', error)
    }
  }
  
  // Show loading while checking authentication
  if (!isMounted || authLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading newsletter...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }
  
  // Don't render anything if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null
  }
  
  // Show loading if newsletter is still loading
  if (newsletterLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
            <p className="mt-4 text-gray-600">Loading newsletter...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }
  
  // Show error if there was an error fetching the newsletter
  if (newsletterError) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error loading newsletter</h2>
            <p className="text-gray-600 mb-6">There was an error loading the newsletter. Please try again.</p>
            <Link href="/dashboard/newsletters">
              <Button>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Newsletters
              </Button>
            </Link>
          </div>
        </div>
      </DashboardLayout>
    )
  }
  
  // Show error if newsletter not found
  if (!newsletter) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Newsletter not found</h2>
            <p className="text-gray-600 mb-6">The newsletter you're looking for doesn't exist or has been deleted.</p>
            <Link href="/dashboard/newsletters">
              <Button>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Newsletters
              </Button>
            </Link>
          </div>
        </div>
      </DashboardLayout>
    )
  }
  
  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Enhanced Header */}
        <div className="bg-gradient-to-r from-green-50 via-blue-50 to-indigo-50 rounded-2xl p-8 border border-green-100">
          <div className="flex justify-between items-start">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard/newsletters">
                <Button variant="ghost" size="sm" className="hover:bg-white/50">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </Link>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Edit Newsletter
                </h1>
                <p className="mt-2 text-lg text-gray-600">
                  Make changes to your newsletter draft
                </p>
                <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                    newsletter.status === 'published' 
                      ? 'bg-green-100 text-green-800'
                      : newsletter.status === 'scheduled'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {newsletter.status}
                  </span>
                  <span className="flex items-center">
                    <Calendar className="h-4 w-4 mr-1" />
                    Created {new Date(newsletter.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex space-x-3">
              <Link href={`/dashboard/newsletters/${newsletter.id}/preview`}>
                <Button variant="outline" className="border-blue-200 hover:border-blue-300 hover:bg-blue-50">
                  <Eye className="h-4 w-4 mr-2" />
                  Preview
                </Button>
              </Link>
              {newsletter.status === 'draft' && (
                <Button 
                  onClick={handleSend}
                  disabled={isSending}
                  className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white"
                >
                  {isSending ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4 mr-2" />
                  )}
                  Send Newsletter
                </Button>
              )}
            </div>
          </div>
        </div>
        
        {/* Edit Form */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <Card className="bg-gradient-to-br from-white to-gray-50 border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-gray-900">Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    Newsletter Title *
                  </label>
                  <Input
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="Enter newsletter title"
                    className="text-lg font-medium"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    Subject Line *
                  </label>
                  <Input
                    name="subject_line"
                    value={formData.subject_line}
                    onChange={handleInputChange}
                    placeholder="Email subject line"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    Target Audience
                  </label>
                  <Input
                    name="target_audience"
                    value={formData.target_audience}
                    onChange={handleInputChange}
                    placeholder="Describe your target audience"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    Schedule For Later (Optional)
                  </label>
                  <Input
                    type="datetime-local"
                    name="scheduled_for"
                    value={formData.scheduled_for}
                    onChange={handleInputChange}
                  />
                </div>
              </CardContent>
            </Card>
            
            {/* Content */}
            <Card className="bg-gradient-to-br from-white to-gray-50 border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-gray-900">Newsletter Content</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  placeholder="Write your newsletter content here..."
                  className="min-h-[400px] text-base leading-relaxed"
                />
              </CardContent>
            </Card>
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Actions */}
            <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-blue-900">Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={handleSave}
                  disabled={isUpdating}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  {isUpdating ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Save className="h-4 w-4 mr-2" />
                  )}
                  Save Changes
                </Button>
                
                {newsletter.status === 'draft' && (
                  <Button 
                    onClick={handleSend}
                    disabled={isSending}
                    variant="outline"
                    className="w-full border-green-200 hover:bg-green-50"
                  >
                    {isSending ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4 mr-2" />
                    )}
                    Send Now
                  </Button>
                )}
                
                <Button 
                  onClick={handleDelete}
                  disabled={isDeleting}
                  variant="outline"
                  className="w-full border-red-200 hover:bg-red-50 text-red-600 hover:text-red-700"
                >
                  {isDeleting ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4 mr-2" />
                  )}
                  Delete Newsletter
                </Button>
              </CardContent>
            </Card>
            
            {/* Newsletter Stats */}
            <Card className="bg-gradient-to-br from-gray-50 to-white border-gray-200">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-gray-900">Newsletter Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-600">Status</span>
                  <span className={`text-sm font-semibold ${
                    newsletter.status === 'published' ? 'text-green-600' :
                    newsletter.status === 'scheduled' ? 'text-blue-600' : 'text-yellow-600'
                  }`}>
                    {newsletter.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-600">Created</span>
                  <span className="text-sm text-gray-900">
                    {new Date(newsletter.created_at).toLocaleDateString()}
                  </span>
                </div>
                {newsletter.scheduled_for && (
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">Scheduled</span>
                    <span className="text-sm text-blue-600 font-medium">
                      {new Date(newsletter.scheduled_for).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
