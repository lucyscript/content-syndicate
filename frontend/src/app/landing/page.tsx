import Link from "next/link";
import { ArrowRight, BarChart3, Mail, Zap, Users } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="flex items-center justify-between p-6 max-w-7xl mx-auto">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg"></div>
          <span className="text-xl font-bold text-gray-900">ContentSyndicate</span>
        </div>
        <div className="flex items-center space-x-4">
          <Link 
            href="/auth/login" 
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            Login
          </Link>
          <Link 
            href="/auth/register" 
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 pt-20 pb-32">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            AI-Powered Newsletter
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Revolution</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Transform trending content from multiple platforms into personalized, 
            high-quality newsletters using advanced AI agents. 
            Create engaging content in minutes, not hours.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <Link 
              href="/dashboard" 
              className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <span>Start Creating</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link 
              href="/demo" 
              className="border border-gray-300 text-gray-700 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Watch Demo
            </Link>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-16">
            Everything you need to create amazing newsletters
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Content Generation</h3>
              <p className="text-gray-600">Generate high-quality newsletter content from trending topics automatically</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Analytics</h3>
              <p className="text-gray-600">Track performance, engagement, and optimize your content strategy</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Audience Segmentation</h3>
              <p className="text-gray-600">Personalize content for different audience segments automatically</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Multi-Platform Distribution</h3>
              <p className="text-gray-600">Send newsletters via email and share on social media platforms</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Preview */}
      <div className="bg-gray-50 py-24">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Simple, Transparent Pricing
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-white rounded-lg p-8 border">
              <h3 className="text-xl font-semibold mb-2">Starter</h3>
              <div className="text-3xl font-bold text-blue-600 mb-4">$19<span className="text-sm text-gray-500">/month</span></div>
              <ul className="text-gray-600 space-y-2 mb-6">
                <li>5 newsletters/month</li>
                <li>2 content sources</li>
                <li>Basic AI curation</li>
                <li>Email delivery</li>
              </ul>
            </div>
            <div className="bg-white rounded-lg p-8 border-2 border-blue-500 relative">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded text-sm">
                Most Popular
              </div>
              <h3 className="text-xl font-semibold mb-2">Professional</h3>
              <div className="text-3xl font-bold text-blue-600 mb-4">$49<span className="text-sm text-gray-500">/month</span></div>
              <ul className="text-gray-600 space-y-2 mb-6">
                <li>20 newsletters/month</li>
                <li>All content sources</li>
                <li>Advanced AI personalization</li>
                <li>Social media posting</li>
                <li>Analytics dashboard</li>
              </ul>
            </div>
            <div className="bg-white rounded-lg p-8 border">
              <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
              <div className="text-3xl font-bold text-blue-600 mb-4">$99<span className="text-sm text-gray-500">/month</span></div>
              <ul className="text-gray-600 space-y-2 mb-6">
                <li>Unlimited newsletters</li>
                <li>Custom content sources</li>
                <li>White-label branding</li>
                <li>API access</li>
                <li>Priority support</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg"></div>
            <span className="text-xl font-bold">ContentSyndicate</span>
          </div>
          <p className="text-gray-400 mb-4">
            Transform your content strategy with AI-powered newsletter creation
          </p>
          <div className="flex items-center justify-center space-x-6 text-sm text-gray-400">
            <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
