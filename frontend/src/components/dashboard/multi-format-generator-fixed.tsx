"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Copy, 
  Send, 
  Wand2, 
  Twitter, 
  Linkedin, 
  Facebook, 
  Instagram,
  Youtube,
  FileText,
  Globe,
  MessageSquare,
  Hash,
  Sparkles,
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { multiFormatAPI } from '@/lib/multi-format-api';

interface ContentFormat {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  characterLimit?: number;
  wordLimit?: number;
  color: string;
  category: 'social' | 'publishing' | 'email';
}

interface GeneratedContent {
  format: string;
  content: any;
  metadata?: any;
  error?: string;
}

const CONTENT_FORMATS: ContentFormat[] = [
  {
    id: 'newsletter',
    name: 'Newsletter',
    icon: <FileText className="w-4 h-4" />,
    description: 'Professional email newsletter',
    wordLimit: 800,
    color: 'bg-blue-500',
    category: 'email'
  },
  {
    id: 'twitter_thread',
    name: 'Twitter Thread',
    icon: <Twitter className="w-4 h-4" />,
    description: 'Multi-tweet thread',
    characterLimit: 280,
    color: 'bg-sky-500',
    category: 'social'
  },
  {
    id: 'twitter_post',
    name: 'Twitter Post',
    icon: <Twitter className="w-4 h-4" />,
    description: 'Single tweet',
    characterLimit: 280,
    color: 'bg-sky-400',
    category: 'social'
  },
  {
    id: 'linkedin_post',
    name: 'LinkedIn Post',
    icon: <Linkedin className="w-4 h-4" />,
    description: 'Professional update',
    characterLimit: 3000,
    color: 'bg-blue-600',
    category: 'social'
  },
  {
    id: 'linkedin_article',
    name: 'LinkedIn Article',
    icon: <Linkedin className="w-4 h-4" />,
    description: 'Long-form article',
    wordLimit: 1200,
    color: 'bg-blue-700',
    category: 'publishing'
  },
  {
    id: 'reddit_post',
    name: 'Reddit Post',
    icon: <MessageSquare className="w-4 h-4" />,
    description: 'Community discussion',
    wordLimit: 500,
    color: 'bg-orange-500',
    category: 'social'
  },
  {
    id: 'medium_article',
    name: 'Medium Article',
    icon: <FileText className="w-4 h-4" />,
    description: 'Storytelling article',
    wordLimit: 1500,
    color: 'bg-green-600',
    category: 'publishing'
  },
  {
    id: 'instagram_caption',
    name: 'Instagram Caption',
    icon: <Instagram className="w-4 h-4" />,
    description: 'Visual-first post',
    characterLimit: 2200,
    color: 'bg-pink-500',
    category: 'social'
  },
  {
    id: 'facebook_post',
    name: 'Facebook Post',
    icon: <Facebook className="w-4 h-4" />,
    description: 'Community engagement',
    characterLimit: 500,
    color: 'bg-blue-500',
    category: 'social'
  },
  {
    id: 'blog_post',
    name: 'Blog Post',
    icon: <Globe className="w-4 h-4" />,
    description: 'SEO-optimized article',
    wordLimit: 1000,
    color: 'bg-purple-500',
    category: 'publishing'
  },
  {
    id: 'youtube_script',
    name: 'YouTube Script',
    icon: <Youtube className="w-4 h-4" />,
    description: 'Video narration',
    wordLimit: 800,
    color: 'bg-red-500',
    category: 'publishing'
  },
  {
    id: 'tiktok_caption',
    name: 'TikTok Caption',
    icon: <Hash className="w-4 h-4" />,
    description: 'Short-form video',
    characterLimit: 150,
    color: 'bg-black',
    category: 'social'
  }
];

export default function MultiFormatGenerator() {
  const [sourceContent, setSourceContent] = useState('');
  const [topic, setTopic] = useState('');
  const [targetAudience, setTargetAudience] = useState('general');
  const [tone, setTone] = useState('professional');
  const [selectedFormats, setSelectedFormats] = useState<string[]>([]);
  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<Record<string, GeneratedContent>>({});
  const [activeTab, setActiveTab] = useState('setup');

  // Quick select presets
  const QUICK_PRESETS = {
    'Social Media Pack': ['twitter_thread', 'linkedin_post', 'instagram_caption'],
    'Publishing Suite': ['newsletter', 'medium_article', 'blog_post'],
    'Professional Content': ['newsletter', 'linkedin_article', 'twitter_thread'],
    'Creator Kit': ['twitter_thread', 'instagram_caption', 'tiktok_caption', 'youtube_script'],
    'Everything': CONTENT_FORMATS.map(f => f.id)
  };

  const handleFormatToggle = (formatId: string, checked: boolean) => {
    if (checked) {
      setSelectedFormats(prev => [...prev, formatId]);
    } else {
      setSelectedFormats(prev => prev.filter(id => id !== formatId));
    }
  };

  const handlePresetSelect = (preset: string) => {
    setSelectedFormats(QUICK_PRESETS[preset as keyof typeof QUICK_PRESETS]);
  };

  const generateAllContent = async () => {
    if (!sourceContent.trim()) {
      toast.error('Please provide source content');
      return;
    }

    if (selectedFormats.length === 0) {
      toast.error('Please select at least one content format');
      return;
    }

    setIsGenerating(true);
    setActiveTab('results');

    try {
      const response = await multiFormatAPI.generateMultiFormat({
        source_content: sourceContent,
        topic,
        target_audience: targetAudience,
        tone,
        selected_formats: selectedFormats,
        custom_instructions: customInstructions
      });

      if (response.data.success) {
        setGeneratedContent(response.data.generated_content);
        toast.success(`Generated ${Object.keys(response.data.generated_content).length} content formats!`);
      } else {
        toast.error(response.data.error || 'Failed to generate content');
      }
    } catch (error) {
      console.error('Generation error:', error);
      toast.error('Failed to generate content');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      toast.success('Copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy to clipboard');
    }
  };

  const getFormatsByCategory = (category: string) => {
    return CONTENT_FORMATS.filter(format => format.category === category);
  };

  const renderContentCard = (formatId: string, content: GeneratedContent) => {
    const format = CONTENT_FORMATS.find(f => f.id === formatId);
    if (!format) return null;

    const hasError = !!content.error;
    const displayContent = hasError ? content.error : content.content?.raw_content || '';

    return (
      <Card key={formatId} className={`${hasError ? 'border-red-200' : 'border-green-200'}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`p-2 rounded ${format.color} text-white`}>
                {format.icon}
              </div>
              <div>
                <CardTitle className="text-sm">{format.name}</CardTitle>
                <CardDescription className="text-xs">{format.description}</CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {hasError ? (
                <AlertCircle className="w-4 h-4 text-red-500" />
              ) : (
                <CheckCircle className="w-4 h-4 text-green-500" />
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {!hasError && (
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              {content.metadata?.character_count && (
                <Badge variant="outline">
                  {content.metadata.character_count} chars
                </Badge>
              )}
              {content.metadata?.word_count && (
                <Badge variant="outline">
                  {content.metadata.word_count} words
                </Badge>
              )}
              {format.characterLimit && (
                <Badge variant={content.metadata?.character_count > format.characterLimit ? "destructive" : "secondary"}>
                  Limit: {format.characterLimit}
                </Badge>
              )}
            </div>
          )}
          
          <div className="space-y-2">
            {/* Special rendering for Twitter threads */}
            {formatId === 'twitter_thread' && content.content?.tweets && (
              <div className="space-y-2">
                {content.content.tweets.map((tweet: string, index: number) => (
                  <div key={index} className="p-2 bg-gray-50 rounded text-sm border-l-2 border-sky-500">
                    <div className="font-mono text-xs text-muted-foreground mb-1">
                      {index + 1}/{content.content.tweets.length}
                    </div>
                    {tweet}
                  </div>
                ))}
              </div>
            )}
            
            {/* Default content display */}
            {(formatId !== 'twitter_thread' || !content.content?.tweets) && (
              <Textarea
                value={displayContent}
                readOnly
                className={`min-h-[120px] text-sm ${hasError ? 'text-red-600' : ''}`}
                placeholder={hasError ? "Generation failed" : "Generated content will appear here..."}
              />
            )}
          </div>

          {!hasError && (
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => copyToClipboard(displayContent)}
                className="flex-1"
              >
                <Copy className="w-3 h-3 mr-1" />
                Copy
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex-1"
              >
                <Send className="w-3 h-3 mr-1" />
                Post to {format.name}
              </Button>
            </div>
          )}

          {/* Display hashtags if available */}
          {content.content?.hashtags && (
            <div className="flex flex-wrap gap-1">
              {content.content.hashtags.map((hashtag: string, index: number) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {hashtag}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Sparkles className="w-8 h-8 text-purple-500" />
          Multi-Format Content Generator
        </h1>
        <p className="text-muted-foreground">
          Create content for all platforms from a single source. Generate once, distribute everywhere.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="setup">Setup & Generate</TabsTrigger>
          <TabsTrigger value="results">Generated Content</TabsTrigger>
        </TabsList>

        <TabsContent value="setup" className="space-y-6">
          {/* Source Content */}
          <Card>
            <CardHeader>
              <CardTitle>Source Content</CardTitle>
              <CardDescription>
                Provide the source material for content generation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="source-content">Source Material</Label>
                <Textarea
                  id="source-content"
                  placeholder="Paste your source content, articles, or ideas here..."
                  value={sourceContent}
                  onChange={(e) => setSourceContent(e.target.value)}
                  className="min-h-[120px]"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="topic">Topic/Theme</Label>
                  <Input
                    id="topic"
                    placeholder="e.g., AI productivity tips"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="audience">Target Audience</Label>
                  <Select value={targetAudience} onValueChange={setTargetAudience}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="general">General</SelectItem>
                      <SelectItem value="entrepreneurs">Entrepreneurs</SelectItem>
                      <SelectItem value="developers">Developers</SelectItem>
                      <SelectItem value="marketers">Marketers</SelectItem>
                      <SelectItem value="creators">Content Creators</SelectItem>
                      <SelectItem value="students">Students</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="tone">Tone</Label>
                  <Select value={tone} onValueChange={setTone}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="authoritative">Authoritative</SelectItem>
                      <SelectItem value="conversational">Conversational</SelectItem>
                      <SelectItem value="humorous">Humorous</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="custom-instructions">Custom Instructions (Optional)</Label>
                <Textarea
                  id="custom-instructions"
                  placeholder="Any specific instructions or requirements..."
                  value={customInstructions}
                  onChange={(e) => setCustomInstructions(e.target.value)}
                  className="min-h-[60px]"
                />
              </div>
            </CardContent>
          </Card>

          {/* Format Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Content Formats</CardTitle>
              <CardDescription>
                Select which formats to generate. Choose individual formats or use quick presets.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Quick Presets */}
              <div className="space-y-2">
                <Label>Quick Presets</Label>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(QUICK_PRESETS).map((preset) => (
                    <Button
                      key={preset}
                      variant="outline"
                      size="sm"
                      onClick={() => handlePresetSelect(preset)}
                      className="text-xs"
                    >
                      {preset}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Format Categories */}
              <div className="space-y-4">
                {['social', 'publishing', 'email'].map((category) => (
                  <div key={category} className="space-y-2">
                    <Label className="capitalize font-medium">
                      {category === 'social' ? 'Social Media' : category === 'publishing' ? 'Publishing Platforms' : 'Email Marketing'}
                    </Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                      {getFormatsByCategory(category).map((format) => (
                        <div key={format.id} className="flex items-center space-x-2 p-2 border rounded">
                          <Checkbox
                            id={format.id}
                            checked={selectedFormats.includes(format.id)}
                            onCheckedChange={(checked: boolean) => handleFormatToggle(format.id, checked)}
                          />
                          <label htmlFor={format.id} className="flex items-center gap-2 cursor-pointer flex-1">
                            <div className={`p-1 rounded ${format.color} text-white`}>
                              {format.icon}
                            </div>
                            <div className="flex-1">
                              <div className="text-sm font-medium">{format.name}</div>
                              <div className="text-xs text-muted-foreground">{format.description}</div>
                              {(format.characterLimit || format.wordLimit) && (
                                <div className="text-xs text-muted-foreground">
                                  {format.characterLimit ? `${format.characterLimit} chars` : `${format.wordLimit} words`}
                                </div>
                              )}
                            </div>
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Selected count */}
              <div className="flex items-center justify-between p-3 bg-muted rounded">
                <span className="text-sm">
                  {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
                </span>
                <Button
                  onClick={generateAllContent}
                  disabled={isGenerating || selectedFormats.length === 0 || !sourceContent.trim()}
                  className="flex items-center gap-2"
                >
                  {isGenerating ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Wand2 className="w-4 h-4" />
                  )}
                  {isGenerating ? 'Generating...' : 'Generate All Content'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-6">
          {Object.keys(generatedContent).length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Wand2 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Content Generated Yet</h3>
                <p className="text-muted-foreground mb-4">
                  Go to the Setup tab to configure and generate your multi-format content.
                </p>
                <Button onClick={() => setActiveTab('setup')}>
                  Go to Setup
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {Object.entries(generatedContent).map(([formatId, content]) =>
                renderContentCard(formatId, content)
              )}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
