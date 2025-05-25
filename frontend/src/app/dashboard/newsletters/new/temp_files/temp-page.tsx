'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNewsletters } from '@/hooks/useNewsletters'
import DashboardLayout from '@/components/dashboard/layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Save, 
  Send, 
  Eye, 
  ArrowLeft,
  Sparkles,
} from 'lucide-react'

const newsletterSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().optional(),
  content: z.string().min(1, 'Content is required'),
  scheduled_for: z.string().optional(),
})

type NewsletterFormData = z.infer<typeof newsletterSchema>

export default function NewNewsletterPage() {
  const router = useRouter()
  const { createNewsletterAsync, generateContentAsync, isCreating } = useNewsletters()
  const [isPreviewMode, setIsPreviewMode] = useState(false)
  const [isGeneratingContent, setIsGeneratingContent] = useState(false)

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isDirty },
  } = useForm<NewsletterFormData>({
    resolver: zodResolver(newsletterSchema),
    defaultValues: {
      title: '',
      description: '',
      content: '',
      scheduled_for: '',
    },
  })

  const watchedContent = watch('content')
  const watchedTitle = watch('title')

  const onSubmit = async (data: NewsletterFormData) => {
    const newsletterData = {
      ...data,
      status: 'draft' as const,
      scheduled_for: data.scheduled_for || undefined,
    }
    
    try {
      await createNewsletterAsync(newsletterData)
      router.push('/dashboard/newsletters')
    } catch (error) {
      console.error('Failed to create newsletter:', error)
      alert('Failed to create newsletter. Please try again.')
    }
  }

  const handleGenerateContent = async () => {
    const title = watch('title')
    
    if (!title) {
      alert('Please enter a title first before generating content.')
      return
    }

    setIsGeneratingContent(true)

    try {
      // First create a draft newsletter to get an ID
      const newsletterData = {
        title,
        description: watch('description') || '',
        content: '', // Empty initially, will be populated by AI
        status: 'draft' as const,
        scheduled_for: watch('scheduled_for') || undefined,
      }

      // Create newsletter and get the response
      const createdNewsletter = await createNewsletterAsync(newsletterData)

      // Now generate content for the created newsletter
      const generateRequest = {
        sources: [], // Could be populated from user preferences
        topic: title,
        tone: 'professional',
        length: 'medium',
        audience: 'general'
      }

      // Generate content using the mutation
      const generatedContent = await generateContentAsync({ 
        id: createdNewsletter.id, 
        request: generateRequest 
      })

      // Update the form with the AI-generated content
      setValue('content', generatedContent.content, { shouldDirty: true })
      
      // Update title if AI generated a better one
      if (generatedContent.title && generatedContent.title !== title) {
        setValue('title', generatedContent.title, { shouldDirty: true })
      }

    } catch (error) {
      console.error('Content generation failed:', error)
      alert('Failed to generate content with AI. Please try again.')
    } finally {
      setIsGeneratingContent(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => router.back()}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Create Newsletter</h1>
              <p className="text-sm text-gray-500">
                Craft your next newsletter with AI-powered content generation
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline"
              onClick={() => setIsPreviewMode(!isPreviewMode)}
            >
              <Eye className="h-4 w-4 mr-2" />
              {isPreviewMode ? 'Edit' : 'Preview'}
            </Button>
            <Button 
              form="newsletter-form"
              type="submit"
              disabled={isCreating || !isDirty}
            >
              <Save className="h-4 w-4 mr-2" />
              {isCreating ? 'Saving...' : 'Save Draft'}
            </Button>
          </div>
        </div>

        {isPreviewMode ? (
          <Card>
            <CardHeader>
              <CardTitle>Newsletter Preview</CardTitle>
              <CardDescription>
                This is how your newsletter will appear to subscribers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-w-none prose prose-sm">
                <h1 className="text-2xl font-bold mb-4">{watchedTitle || 'Untitled Newsletter'}</h1>
                <div 
                  className="whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ 
                    __html: watchedContent.replace(/\n/g, '<br />').replace(/### (.*)/g, '<h3>$1</h3>').replace(/## (.*)/g, '<h2>$1</h2>').replace(/# (.*)/g, '<h1>$1</h1>')
                  }}
                />
              </div>
            </CardContent>
          </Card>
        ) : (
          <form id="newsletter-form" onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Newsletter Details</CardTitle>
                <CardDescription>
                  Basic information about your newsletter
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <Input
                    id="title"
                    placeholder="Enter newsletter title..."
                    {...register('title')}
                  />
                  {errors.title && (
                    <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <Input
                    id="description"
                    placeholder="Brief description of this newsletter..."
                    {...register('description')}
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="scheduled_for" className="block text-sm font-medium text-gray-700 mb-1">
                    Schedule for later (optional)
                  </label>
                  <Input
                    id="scheduled_for"
                    type="datetime-local"
                    {...register('scheduled_for')}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Content Generation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Content Creation
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleGenerateContent}
                    disabled={isGeneratingContent}
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    {isGeneratingContent ? 'Generating with AI...' : 'Generate with AI'}
                  </Button>
                </CardTitle>
                <CardDescription>
                  Write your newsletter content or use AI to generate it from trending topics using Gemini AI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div>
                  <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                    Content *
                  </label>
                  <textarea
                    id="content"
                    rows={20}
                    className="block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Write your newsletter content here... You can use Markdown formatting, or click 'Generate with AI' to create content automatically."
                    {...register('content')}
                  />
                  {errors.content && (
                    <p className="mt-1 text-sm text-red-600">{errors.content.message}</p>
                  )}
                  <p className="mt-1 text-xs text-gray-500">
                    Tip: Use Markdown formatting for headers (# ## ###), links [text](url), and **bold** text.
                  </p>
                </div>
              </CardContent>
            </Card>
          </form>
        )}

        {/* Actions */}
        {!isPreviewMode && (
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Ready to publish?</h3>
                  <p className="text-sm text-gray-500">
                    Save as draft to continue later, or publish to send to all subscribers.
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <Button 
                    variant="outline"
                    form="newsletter-form"
                    type="submit"
                    disabled={isCreating}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Draft
                  </Button>
                  <Button 
                    disabled={!watchedTitle || !watchedContent || isCreating}
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Publish Now
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
