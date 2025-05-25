'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useNewsletters } from '@/hooks/useNewsletters'
import { useAuth } from '@/hooks/useAuth'
import { useAuthProvider } from '@/components/providers/auth-provider'
import { contentAPI } from '@/lib/api'

export default function NewNewsletterPage() {
  const router = useRouter()
  const { createNewsletterAsync, generateContentAsync } = useNewsletters()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { isInitialized } = useAuthProvider()
  
  // Fix hydration mismatch by ensuring client-only rendering
  const [isMounted, setIsMounted] = useState(false)
  
  console.log('[NewNewsletterPage] Render state:', {
    isAuthenticated,
    authLoading,
    isInitialized,
    isMounted
  })
  
  console.log('[NewNewsletterPage] Rendering decision:', {
    willShowFirstLoading: !isMounted,
    willShowSecondLoading: isMounted && (!isInitialized || authLoading),
    willShowContent: isMounted && isInitialized && !authLoading
  })
  
  const [formData, setFormData] = useState({
    title: '',
    subject_line: '',
    content_sources: '',
    target_audience: '',
    scheduled_for: '',
    newsletterId: null as number | null
  })
  const [generatedContent, setGeneratedContent] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  
  // Topic suggestions state
  const [showTopicSuggestions, setShowTopicSuggestions] = useState(false)
  const [topicSuggestions, setTopicSuggestions] = useState<any[]>([])
  const [loadingTopics, setLoadingTopics] = useState(false)
  const [topicNiche, setTopicNiche] = useState('general')

  // Fix hydration by ensuring component is mounted on client
  useEffect(() => {
    setIsMounted(true)
  }, [])
  
  // Redirect if not authenticated
  useEffect(() => {
    if (isInitialized && !authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isInitialized, authLoading, isAuthenticated, router])
  
  // Load topic suggestions
  const loadTopicSuggestions = async (niche: string = 'general') => {
    if (!isAuthenticated || !isInitialized) {
      console.log('Not authenticated or not initialized, skipping topic suggestions')
      return
    }

    setLoadingTopics(true)
    try {
      const [trendingResponse, aiResponse] = await Promise.all([
        contentAPI.getTrendingTopics({ limit: 5 }),
        contentAPI.generateRandomTopics({ count: 5, niche, tone: 'professional' })
      ])
      
      const trending = trendingResponse.data.trending_topics || []
      const aiGenerated = aiResponse.data.topics || []
      
      // Combine and format suggestions
      const combined = [
        ...trending.map((topic: any) => ({ ...topic, type: 'trending' })),
        ...aiGenerated.map((topic: any) => ({ ...topic, type: 'ai_generated' }))
      ]
      
      setTopicSuggestions(combined)
    } catch (error: any) {
      console.error('Error loading topic suggestions:', error)
      // Show user-friendly error message
      if (error.response?.status === 401) {
        alert('Please log in to access topic suggestions.')
      } else {
        alert('Failed to load topic suggestions. Please try again.')
      }
    } finally {
      setLoadingTopics(false)
    }
  }

  // Apply topic suggestion to form
  const applyTopicSuggestion = (suggestion: any) => {
    setFormData(prev => ({
      ...prev,
      title: suggestion.title,
      subject_line: suggestion.title, // Use title as default subject
      target_audience: suggestion.audience || prev.target_audience
    }))
    setShowTopicSuggestions(false)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }
  
  const handleGenerateContent = async () => {
    if (!formData.title || !formData.subject_line || !formData.target_audience) {
      alert('Please fill in at least the title, subject line, and target audience to generate content.')
      return
    }

    setIsGenerating(true)
    try {
      // First create a draft newsletter to get an ID
      const draftNewsletter = await createNewsletterAsync({
        title: formData.title,
        subject_line: formData.subject_line,
        content_sources: formData.content_sources ? JSON.parse(formData.content_sources) : [],
        target_audience: formData.target_audience,
        scheduled_for: formData.scheduled_for ? new Date(formData.scheduled_for).toISOString() : undefined,
        content: '', // Empty initially
        status: 'draft'
      })

      // Then generate content for the created newsletter
      const response = await generateContentAsync({
        id: draftNewsletter.id,
        request: {
          sources: formData.content_sources ? JSON.parse(formData.content_sources) : [],
          topic: formData.title,
          tone: 'professional',
          length: 'medium',
          audience: formData.target_audience
        }
      })
      
      setGeneratedContent(response.content)
      
      // Set the newsletter ID for future updates
      setFormData(prev => ({ ...prev, newsletterId: draftNewsletter.id }))
      
    } catch (error) {
      console.error('Error generating content:', error)
      alert('Failed to generate content. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }
  
  const handleCreateNewsletter = async () => {
    if (!formData.title) {
      alert('Please ensure you have a title.')
      return
    }

    setIsCreating(true)
    try {
      // If we already have a newsletter with generated content, just navigate
      if (formData.newsletterId && generatedContent) {
        alert('Newsletter created successfully!')
        router.push('/dashboard/newsletters')
        return
      }

      // If no generated content, create a newsletter without content
      await createNewsletterAsync({
        title: formData.title,
        subject_line: formData.subject_line,
        content_sources: formData.content_sources ? JSON.parse(formData.content_sources) : [],
        target_audience: formData.target_audience,
        scheduled_for: formData.scheduled_for ? new Date(formData.scheduled_for).toISOString() : undefined,
        content: generatedContent || '',
        status: 'draft'
      })
      alert('Newsletter created successfully!')
      router.push('/dashboard/newsletters')
    } catch (error) {
      console.error('Error creating newsletter:', error)
      alert('Failed to create newsletter. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }
  
  // Show loading during hydration and authentication
  if (!isMounted || !isInitialized || authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="flex items-center justify-center min-h-screen">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/20">
            <div className="flex items-center gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gradient-to-r from-blue-500 to-purple-500"></div>
              <span className="text-slate-700 font-medium">Loading your workspace...</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-5xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Create New Newsletter
          </h1>
          <p className="text-slate-600 mt-3 text-lg font-medium">Use AI to generate engaging newsletter content</p>
        </div>
        
        <div className="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl border border-white/20 overflow-hidden">
          {/* Topic Suggestions Section */}
          <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-white" data-testid="topic-inspiration-header">
                  ✨ Topic Inspiration
                </h2>
                <p className="text-indigo-100 text-sm font-medium">Get AI-powered topic suggestions to kickstart your newsletter</p>
              </div>
              <button
                data-testid="show-topic-suggestions-button"
                onClick={() => {
                  setShowTopicSuggestions(!showTopicSuggestions)
                  if (!showTopicSuggestions && topicSuggestions.length === 0) {
                    loadTopicSuggestions(topicNiche)
                  }
                }}
                className="bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-xl hover:bg-white/30 transition-all duration-200 flex items-center gap-2 font-medium border border-white/30 shadow-lg"
              >
                ✨ {showTopicSuggestions ? 'Hide' : 'Show'} Suggestions
              </button>
            </div>
            
            {showTopicSuggestions && loadingTopics && (
              <div className="text-center py-6" data-testid="loading-topic-suggestions">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-white border-t-transparent mx-auto"></div>
                <p className="text-white/80 mt-3 font-medium">Loading inspiring topics...</p>
              </div>
            )}
            
            {showTopicSuggestions && !loadingTopics && topicSuggestions.length === 0 && (
              <div className="text-center py-6" data-testid="no-topic-suggestions">
                <div className="text-white/80 mb-2">💡</div>
                <p className="text-white/80 font-medium">No topic suggestions available at the moment.</p>
                <p className="text-white/60 text-sm">Try adjusting the niche or check back later.</p>
              </div>
            )}
            
            {showTopicSuggestions && !loadingTopics && topicSuggestions.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                {topicSuggestions.map((suggestion, index) => (
                  <div 
                    key={index} 
                    className="bg-white/90 backdrop-blur-sm p-5 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 cursor-pointer border border-white/30 hover:bg-white group"
                    onClick={() => applyTopicSuggestion(suggestion)}
                    data-testid={`topic-suggestion-card-${index}`}
                  >
                    <h3 className="font-bold text-slate-800 text-lg mb-2 group-hover:text-purple-600 transition-colors">
                      {suggestion.title}
                    </h3>
                    <p className="text-slate-600 text-sm leading-relaxed mb-3">
                      {suggestion.description || 'No description available.'}
                    </p>
                    {(suggestion.keywords || suggestion.angles) && (
                      <div className="flex flex-wrap gap-2">
                        {(suggestion.keywords || suggestion.angles)?.slice(0, 3).map((tag: string, i: number) => (
                          <span key={i} className="bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 px-3 py-1 rounded-full text-xs font-medium">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Newsletter Details Form */}
          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3">
                  Newsletter Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all duration-200 bg-white/50 backdrop-blur-sm text-slate-800 font-medium"
                  placeholder="e.g., Weekly Tech Updates"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3">
                  Subject Line *
                </label>
                <input
                  type="text"
                  name="subject_line"
                  value={formData.subject_line}
                  onChange={handleInputChange}
                  className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all duration-200 bg-white/50 backdrop-blur-sm text-slate-800 font-medium"
                  placeholder="e.g., This Week in Technology"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3">
                  Target Audience *
                </label>
                <input
                  type="text"
                  name="target_audience"
                  value={formData.target_audience}
                  onChange={handleInputChange}
                  className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all duration-200 bg-white/50 backdrop-blur-sm text-slate-800 font-medium"
                  placeholder="e.g., Tech professionals, developers, startup founders"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3">
                  Scheduled For
                </label>
                <input
                  type="datetime-local"
                  name="scheduled_for"
                  value={formData.scheduled_for}
                  onChange={handleInputChange}
                  className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all duration-200 bg-white/50 backdrop-blur-sm text-slate-800 font-medium"
                />
              </div>
            </div>

            <div className="mb-8">
              <label className="block text-sm font-semibold text-slate-700 mb-3">
                Content Sources (JSON format)
              </label>
              <textarea
                name="content_sources"
                value={formData.content_sources}
                onChange={handleInputChange}
                className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all duration-200 bg-white/50 backdrop-blur-sm text-slate-800 font-medium resize-none"
                rows={3}
                placeholder='e.g., ["https://techcrunch.com", "https://arstechnica.com"]'
              />
              <p className="text-sm text-slate-500 mt-2 font-medium">
                Enter URLs or content sources as a JSON array (optional)
              </p>
            </div>

            {/* AI Content Generation Section */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    🤖 AI Content Generation
                  </h2>
                  <p className="text-slate-600 text-sm font-medium mt-1">
                    Generate professional newsletter content automatically
                  </p>
                </div>
                <button
                  onClick={handleGenerateContent}
                  disabled={isGenerating || !formData.title || !formData.subject_line || !formData.target_audience}
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-indigo-700 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed flex items-center gap-2 font-semibold shadow-lg transition-all duration-200"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <span>🚀</span>
                      Generate Content
                    </>
                  )}
                </button>
              </div>

              {generatedContent && (
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-3">
                    Generated Content
                  </label>
                  <div className="border-2 border-blue-200 rounded-xl p-6 bg-white/80 backdrop-blur-sm max-h-96 overflow-y-auto">
                    <div className="prose prose-sm max-w-none text-slate-700">
                      {generatedContent.split('\n').map((paragraph, index) => (
                        <p key={index} className="mb-3 leading-relaxed">{paragraph}</p>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex justify-between pt-8 border-t border-slate-200 mt-8">
              <button
                onClick={() => router.back()}
                className="bg-slate-500 text-white px-6 py-3 rounded-xl hover:bg-slate-600 font-semibold shadow-lg transition-all duration-200"
              >
                ← Back
              </button>
              
              <button
                onClick={handleCreateNewsletter}
                disabled={isCreating || !formData.title}
                className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-8 py-3 rounded-xl hover:from-green-600 hover:to-emerald-700 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed flex items-center gap-2 font-semibold shadow-lg transition-all duration-200"
              >
                {isCreating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    ✅ Create Newsletter
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
