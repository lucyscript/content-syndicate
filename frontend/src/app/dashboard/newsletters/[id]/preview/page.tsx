'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useNewsletters, useNewsletter } from '@/hooks/useNewsletters'
import { useAuth } from '@/hooks/useAuth'
import DashboardLayout from '@/components/dashboard/layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  ArrowLeft, 
  Edit, 
  Send, 
  Copy,
  Mail,
  Calendar,
  Users,
  Eye,
  Loader2,
  FileText,
  ExternalLink,
  Clock
} from 'lucide-react'
import Link from 'next/link'

export default function PreviewNewsletterPage() {
  const router = useRouter()
  const params = useParams()
  const newsletterId = parseInt(params.id as string)
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { newsletter, isLoading, error } = useNewsletter(newsletterId)
  
  const [isMounted, setIsMounted] = useState(false)
  const [copied, setCopied] = useState(false)
  
  useEffect(() => {
    setIsMounted(true)
  }, [])
    // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login?redirect=/dashboard/newsletters')
    }
  }, [isAuthenticated, authLoading, router])
  
  const copyToClipboard = () => {
    if (newsletter?.content) {
      navigator.clipboard.writeText(newsletter.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
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
  
  // Show loading if newsletters are still loading
  if (isLoading) {
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
        <div className="bg-gradient-to-r from-purple-50 via-indigo-50 to-blue-50 rounded-2xl p-8 border border-purple-100">
          <div className="flex justify-between items-start">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard/newsletters">
                <Button variant="ghost" size="sm" className="hover:bg-white/50">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </Link>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent">
                  Newsletter Preview
                </h1>
                <p className="mt-2 text-lg text-gray-600">
                  {newsletter.title}
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
                  {newsletter.scheduled_for && (
                    <span className="flex items-center text-blue-600">
                      <Clock className="h-4 w-4 mr-1" />
                      Scheduled for {new Date(newsletter.scheduled_for).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex space-x-3">
              <Button 
                onClick={copyToClipboard}
                variant="outline" 
                className="border-purple-200 hover:border-purple-300 hover:bg-purple-50"
              >
                <Copy className="h-4 w-4 mr-2" />
                {copied ? 'Copied!' : 'Copy Content'}
              </Button>
              <Link href={`/dashboard/newsletters/${newsletter.id}`}>
                <Button className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white">
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Newsletter
                </Button>
              </Link>
            </div>
          </div>
        </div>
        
        {/* Preview Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3">
            <Card className="bg-gradient-to-br from-white to-gray-50 border-0 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-gray-50 to-white border-b">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                      {newsletter.title}
                    </CardTitle>
                    <p className="text-lg text-gray-600 font-medium">
                      Subject: {newsletter.subject_line}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Mail className="h-6 w-6 text-blue-600" />
                    <span className="text-sm font-medium text-gray-600">Email Preview</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-8">
                {newsletter.content ? (
                  <div className="prose prose-lg max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                      {newsletter.content}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">No content yet</h3>
                    <p className="text-gray-600 mb-6">This newsletter doesn't have any content.</p>
                    <Link href={`/dashboard/newsletters/${newsletter.id}`}>
                      <Button>
                        <Edit className="h-4 w-4 mr-2" />
                        Add Content
                      </Button>
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Newsletter Info */}
            <Card className="bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-indigo-900">Newsletter Details</CardTitle>
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
                {newsletter.target_audience && (
                  <div>
                    <span className="text-sm font-medium text-gray-600 block mb-2">Target Audience</span>
                    <span className="text-sm text-gray-900 bg-white/50 px-3 py-2 rounded-lg block">
                      {newsletter.target_audience}
                    </span>
                  </div>
                )}
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
            
            {/* Stats */}
            <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-green-900">Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Eye className="h-4 w-4 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-gray-600">Opens</span>
                  </div>
                  <span className="text-lg font-bold text-green-600">
                    {(newsletter as any).opens || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <ExternalLink className="h-4 w-4 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-gray-600">Clicks</span>
                  </div>
                  <span className="text-lg font-bold text-blue-600">
                    {(newsletter as any).clicks || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Users className="h-4 w-4 text-purple-600 mr-2" />
                    <span className="text-sm font-medium text-gray-600">Recipients</span>
                  </div>
                  <span className="text-lg font-bold text-purple-600">
                    {(newsletter as any).recipients || 0}
                  </span>
                </div>
                {newsletter.status === 'draft' && (
                  <div className="pt-2 border-t border-green-200">
                    <p className="text-xs text-green-700 bg-green-100 p-2 rounded">
                      Statistics will be available after sending
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Quick Actions */}
            <Card className="bg-gradient-to-br from-gray-50 to-white border-gray-200">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-gray-900">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link href={`/dashboard/newsletters/${newsletter.id}`}>
                  <Button variant="outline" className="w-full">
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Newsletter
                  </Button>
                </Link>
                <Button 
                  onClick={copyToClipboard}
                  variant="outline" 
                  className="w-full"
                >
                  <Copy className="h-4 w-4 mr-2" />
                  {copied ? 'Copied!' : 'Copy Content'}
                </Button>
                <Link href="/dashboard/newsletters/new">
                  <Button variant="outline" className="w-full">
                    <FileText className="h-4 w-4 mr-2" />
                    Create Similar
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
