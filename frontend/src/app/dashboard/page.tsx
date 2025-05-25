'use client'

import { useQuery } from '@/hooks/temp-query'
import { analyticsAPI, newsletterAPI } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import DashboardLayout from '@/components/dashboard/layout'
import { 
  Mail, 
  Users, 
  TrendingUp, 
  Eye, 
  Plus,
  Calendar,
  BarChart3,
  Clock
} from 'lucide-react'
import Link from 'next/link'
import { formatCurrency, formatRelativeDate } from '@/lib/utils'

export default function DashboardPage() {
  const { isAuthenticated, user } = useAuth()
  
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: () => analyticsAPI.getDashboard().then(res => res.data),
  })

  const { data: newsletters, isLoading: newslettersLoading } = useQuery({
    queryKey: ['newsletters', user?.id],
    queryFn: () => newsletterAPI.getAll().then(res => res.data),
    enabled: isAuthenticated, // Only fetch when authenticated
  })

  const recentNewsletters = newsletters?.slice(0, 5) || []

  const stats = [
    {
      name: 'Total Newsletters',
      value: analytics?.total_newsletters || 0,
      icon: Mail,
      color: 'bg-blue-500',
    },
    {
      name: 'Total Subscribers',
      value: analytics?.total_subscribers || 0,
      icon: Users,
      color: 'bg-green-500',
    },
    {
      name: 'Newsletters Sent',
      value: analytics?.total_sends || 0,
      icon: TrendingUp,
      color: 'bg-purple-500',
    },
    {
      name: 'Avg. Open Rate',
      value: `${(analytics?.avg_open_rate || 0).toFixed(1)}%`,
      icon: Eye,
      color: 'bg-orange-500',
    },
  ]
  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Enhanced Header */}
        <div className="bg-gradient-to-r from-indigo-50 via-blue-50 to-cyan-50 rounded-2xl p-8 border border-indigo-100">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 bg-clip-text text-transparent">
                Welcome back, {user?.username || 'Creator'}!
              </h1>
              <p className="mt-2 text-lg text-gray-600">
                Here's what's happening with your content syndication today
              </p>
              <div className="mt-4 flex items-center space-x-6 text-sm text-gray-500">
                <span className="flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  {new Date().toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </span>
              </div>
            </div>
            <div className="flex space-x-3">
              <Link href="/dashboard/newsletters/new">
                <Button className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white shadow-lg transition-all duration-200 transform hover:scale-105">
                  <Plus className="h-4 w-4 mr-2" />
                  New Newsletter
                </Button>
              </Link>
              <Link href="/dashboard/analytics">
                <Button variant="outline" className="border-indigo-200 hover:border-indigo-300 hover:bg-indigo-50">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analytics
                </Button>
              </Link>
            </div>
          </div>
        </div>        {/* Enhanced Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            const gradientClasses = [
              'from-blue-500 to-blue-600',
              'from-green-500 to-green-600', 
              'from-purple-500 to-purple-600',
              'from-orange-500 to-orange-600'
            ]
            const bgClasses = [
              'from-blue-50 to-blue-100 border-blue-200',
              'from-green-50 to-green-100 border-green-200',
              'from-purple-50 to-purple-100 border-purple-200', 
              'from-orange-50 to-orange-100 border-orange-200'
            ]
            return (
              <Card key={stat.name} className={`bg-gradient-to-br ${bgClasses[index]} hover:shadow-lg transition-all duration-300 transform hover:scale-105`}>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className={`flex-shrink-0 p-3 rounded-xl bg-gradient-to-r ${gradientClasses[index]} shadow-lg`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-semibold text-gray-700">{stat.name}</p>
                      <p className="text-3xl font-bold text-gray-900">
                        {analyticsLoading ? (
                          <div className="h-8 bg-gray-300 rounded animate-pulse w-16" />
                        ) : (
                          stat.value
                        )}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Recent Activity Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                Newsletter sends and new subscribers over the last 7 days
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analyticsLoading ? (
                <div className="h-48 bg-gray-200 rounded animate-pulse" />
              ) : analytics?.recent_activity && analytics.recent_activity.length > 0 ? (
                <div className="space-y-3">
                  {analytics.recent_activity.map((day, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{formatRelativeDate(day.date)}</span>
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-blue-600">
                          {day.newsletters_sent} sent
                        </span>
                        <span className="text-sm text-green-600">
                          +{day.new_subscribers} subscribers
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-48 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No activity data yet</p>
                    <p className="text-sm">Start sending newsletters to see your stats here</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Newsletters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <Mail className="h-5 w-5 mr-2" />
                  Recent Newsletters
                </div>
                <Link href="/dashboard/newsletters">
                  <Button variant="ghost" size="sm">View all</Button>
                </Link>
              </CardTitle>
              <CardDescription>
                Your latest newsletter drafts and published content
              </CardDescription>
            </CardHeader>
            <CardContent>
              {newslettersLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-200 rounded animate-pulse" />
                  ))}
                </div>              ) : recentNewsletters.length > 0 ? (
                <div className="space-y-3">
                  {recentNewsletters.map((newsletter) => (                    <Link 
                      key={newsletter.id}
                      href={`/dashboard/newsletters/${newsletter.id}/preview`}
                    >
                      <div className="flex items-center justify-between p-4 border rounded-xl hover:bg-gradient-to-r hover:from-gray-50 hover:to-blue-50 hover:border-blue-200 transition-all duration-200 cursor-pointer group">
                        <div className="flex-1">
                          <h4 className="text-sm font-semibold text-gray-900 truncate group-hover:text-blue-600">
                            {newsletter.title}
                          </h4>
                          <div className="flex items-center mt-2 space-x-4">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                              newsletter.status === 'published' 
                                ? 'bg-green-100 text-green-800'
                                : newsletter.status === 'scheduled'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {newsletter.status}
                            </span>
                            <span className="text-xs text-gray-500 flex items-center">
                              <Calendar className="h-3 w-3 mr-1" />
                              {formatRelativeDate(newsletter.created_at)}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {newsletter.scheduled_for && (
                            <div className="text-blue-600 bg-blue-50 p-2 rounded-lg">
                              <Clock className="h-4 w-4" />
                            </div>
                          )}
                          <Eye className="h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6">
                  <Mail className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500 mb-4">No newsletters yet</p>
                  <Link href="/dashboard/newsletters/new">
                    <Button variant="outline">
                      <Plus className="h-4 w-4 mr-2" />
                      Create your first newsletter
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </div>        {/* Enhanced Quick Actions */}
        <Card className="bg-gradient-to-r from-gray-50 to-white border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-gray-900">Quick Actions</CardTitle>
            <CardDescription className="text-gray-600">
              Common tasks to help you manage your content syndication effectively
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <Link href="/dashboard/newsletters/new">
                <Button variant="outline" className="w-full h-24 flex-col bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 hover:border-blue-300 hover:from-blue-100 hover:to-blue-200 transition-all duration-200 group">
                  <Plus className="h-8 w-8 mb-2 text-blue-600 group-hover:scale-110 transition-transform" />
                  <span className="font-semibold text-blue-700">New Newsletter</span>
                </Button>
              </Link>
              <Link href="/dashboard/content">
                <Button variant="outline" className="w-full h-24 flex-col bg-gradient-to-br from-green-50 to-green-100 border-green-200 hover:border-green-300 hover:from-green-100 hover:to-green-200 transition-all duration-200 group">
                  <TrendingUp className="h-8 w-8 mb-2 text-green-600 group-hover:scale-110 transition-transform" />
                  <span className="font-semibold text-green-700">Add Content Source</span>
                </Button>
              </Link>
              <Link href="/dashboard/subscribers">
                <Button variant="outline" className="w-full h-24 flex-col bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200 hover:border-purple-300 hover:from-purple-100 hover:to-purple-200 transition-all duration-200 group">
                  <Users className="h-8 w-8 mb-2 text-purple-600 group-hover:scale-110 transition-transform" />
                  <span className="font-semibold text-purple-700">Manage Subscribers</span>
                </Button>
              </Link>
              <Link href="/dashboard/analytics">
                <Button variant="outline" className="w-full h-24 flex-col bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200 hover:border-orange-300 hover:from-orange-100 hover:to-orange-200 transition-all duration-200 group">
                  <BarChart3 className="h-8 w-8 mb-2 text-orange-600 group-hover:scale-110 transition-transform" />
                  <span className="font-semibold text-orange-700">View Analytics</span>
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
