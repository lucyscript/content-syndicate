"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Sparkles, 
  FileText, 
  BarChart3, 
  Settings, 
  Zap,
  TrendingUp,
  Users,
  Calendar
} from 'lucide-react';
import MultiFormatGenerator from '@/components/dashboard/multi-format-generator';

export default function ContentHubPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Zap className="w-8 h-8 text-purple-500" />
            Content Hub
          </h1>
          <p className="text-muted-foreground mt-1">
            Generate, repurpose, and distribute your content across all platforms
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
          <Button size="sm">
            <Calendar className="w-4 h-4 mr-2" />
            Schedule Content
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardDescription>Content Generated</CardDescription>
              <FileText className="w-4 h-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">247</div>
            <p className="text-xs text-muted-foreground">+23% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardDescription>Platforms Reached</CardDescription>
              <TrendingUp className="w-4 h-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">Across all channels</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardDescription>Total Engagement</CardDescription>
              <Users className="w-4 h-4 text-purple-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12.4K</div>
            <p className="text-xs text-muted-foreground">+18% from last week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardDescription>Time Saved</CardDescription>
              <BarChart3 className="w-4 h-4 text-orange-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">28h</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="generator" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="generator" className="flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            Content Generator
          </TabsTrigger>
          <TabsTrigger value="library" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Content Library
          </TabsTrigger>
          <TabsTrigger value="schedule" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Schedule & Publish
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="generator" className="mt-6">
          <MultiFormatGenerator />
        </TabsContent>

        <TabsContent value="library" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Content Library</CardTitle>
              <CardDescription>
                Browse and manage your generated content across all formats
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Content Library Coming Soon</h3>
                <p className="text-muted-foreground mb-4">
                  View, search, and manage all your generated content in one place.
                </p>
                <Button variant="outline">
                  Request Early Access
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedule" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Schedule & Publish</CardTitle>
              <CardDescription>
                Schedule your content across multiple platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Scheduling Coming Soon</h3>
                <p className="text-muted-foreground mb-4">
                  Auto-schedule and publish your content to all connected platforms.
                </p>
                <Button variant="outline">
                  Connect Platforms
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Cross-Platform Analytics</CardTitle>
              <CardDescription>
                Track performance across all your content channels
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Analytics Dashboard Coming Soon</h3>
                <p className="text-muted-foreground mb-4">
                  Unified analytics across newsletters, social media, and publishing platforms.
                </p>
                <Button variant="outline">
                  Preview Analytics
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
