import axios, { AxiosResponse } from 'axios'

const API_BASE_URL = 'http://localhost:8000' // Backend server port

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true // Important for handling cookies with CORS
})

// Add request interceptor to ensure token is included
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage - both ways for maximum reliability
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      if (token) {
      if (!config.headers) {
        config.headers = {} as any
      }
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors gracefully
    if (error.response?.status === 401) {
      console.warn('Authentication error detected')
      
      // Clear invalid token from localStorage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
      }
      
      // Redirect to login if on client side and not already on login page
      if (typeof window !== 'undefined' && 
          !window.location.pathname.includes('/auth/login')) {
        console.log('Redirecting to login page due to authentication error')
        window.location.href = '/auth/login'
      }
    }    return Promise.reject(error)
  }
)

// Types based on our backend schemas
export interface User {
  id: number
  email: string
  full_name: string
  is_verified: boolean
  subscription_plan: 'free' | 'pro' | 'enterprise'
  created_at: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  full_name: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ContentGenerationRequest {
  sources: string[]
  topic?: string
  tone?: string
  length?: string
  audience?: string
}

export interface ContentGenerationResponse {
  content: string
  title: string
  subject_line: string
  sources_used: Array<{[key: string]: any}>
  generation_time: number
}

export interface Newsletter {
  id: number
  title: string
  description: string
  content: string
  status: 'draft' | 'published' | 'scheduled'
  scheduled_for?: string
  created_at: string
  updated_at: string
  user_id: number
  subject_line?: string
  content_sources?: any[]
  target_audience?: string
}

export interface ContentSource {
  id: number
  name: string
  url: string
  source_type: string
  is_active: boolean
  last_crawled?: string
  created_at: string
}

export interface AnalyticsData {
  total_newsletters: number
  total_subscribers: number
  total_sends: number
  avg_open_rate: number
  avg_click_rate: number
  recent_activity: Array<{
    date: string
    newsletters_sent: number
    new_subscribers: number
  }>
}

// Token management
let authToken: string | null = null

export const setAuthToken = (token: string | null) => {
  authToken = token
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  } else {
    delete api.defaults.headers.common['Authorization']
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }
}

export const clearAuthToken = () => {
  setAuthToken(null) // Simplified to use the updated setAuthToken
}

// Initialize token from localStorage on app start
// This part might need adjustment based on how AuthProvider initializes
// For now, let AuthProvider handle initial load from localStorage.
// if (typeof window !== 'undefined') {
//   const storedToken = localStorage.getItem('auth_token');
//   if (storedToken) {
//     setAuthToken(storedToken);
//   }
// }

// API Methods
export const authAPI = {
  login: (credentials: LoginCredentials): Promise<AxiosResponse<AuthResponse>> => {
    return api.post<AuthResponse>('/api/auth/login', credentials); // Explicit type for api.post
  },
  register: (data: RegisterData): Promise<AxiosResponse<User>> => {
    // Explicitly specify User as the expected response data type for this post request
    return api.post<User, AxiosResponse<User>, RegisterData>('/api/auth/register', data);
  },
  getCurrentUser: (): Promise<AxiosResponse<User>> => {
    return api.get<User>('/api/auth/me'); // Explicit type for api.get
  },
  logout: (): Promise<AxiosResponse<any>> => {
    return api.post('/api/auth/logout');
  }
}

export const newsletterAPI = {
  getAll: (): Promise<AxiosResponse<Newsletter[]>> =>
    api.get('/api/newsletters/'),
  
  getById: (id: number): Promise<AxiosResponse<Newsletter>> =>
    api.get(`/api/newsletters/${id}`),
  
  create: (data: Partial<Newsletter>): Promise<AxiosResponse<Newsletter>> =>
    api.post('/api/newsletters/', data),
    update: (id: number, data: Partial<Newsletter>): Promise<AxiosResponse<Newsletter>> =>
    api.put(`/api/newsletters/${id}`, data),
  
  delete: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/api/newsletters/${id}`),
  
  generateContent: (id: number, request: ContentGenerationRequest): Promise<AxiosResponse<ContentGenerationResponse>> =>
    api.post(`/api/newsletters/${id}/generate`, request),
  
  send: (id: number): Promise<AxiosResponse<void>> =>
    api.post(`/api/newsletters/${id}/send`)
}

export const contentAPI = {
  getSources: (): Promise<AxiosResponse<ContentSource[]>> =>
    api.get('/api/content/sources'),
  
  addSource: (data: Partial<ContentSource>): Promise<AxiosResponse<ContentSource>> =>
    api.post('/api/content/sources', data),
  
  updateSource: (id: number, data: Partial<ContentSource>): Promise<AxiosResponse<ContentSource>> =>
    api.put(`/api/content/sources/${id}`, data),
  
  deleteSource: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/api/content/sources/${id}`),
  
  getTrending: (): Promise<AxiosResponse<any[]>> =>
    api.get('/api/content/trending'),
  
  // Topic generation endpoints
  getTrendingTopics: (params?: {
    platforms?: string;
    limit?: number;
    categories?: string;
  }): Promise<AxiosResponse<any>> =>
    api.get('/api/content/topics/trending', { params }),
  
  generateRandomTopics: (params?: {
    count?: number;
    niche?: string;
    tone?: string;
  }): Promise<AxiosResponse<any>> =>
    api.get('/api/content/topics/generate', { params }),
  
  matchContentToTopics: (data: {
    user_topics: string[];
    content_data: any[];
    relevance_threshold?: number;
  }): Promise<AxiosResponse<any>> =>
    api.post('/api/content/topics/match', data),
  
  getEnhancedSuggestions: (params?: {
    topic?: string;
    audience?: string;
    include_trending?: boolean;
    include_ai_generated?: boolean;
    limit?: number;
  }): Promise<AxiosResponse<any>> =>
    api.get('/api/content/topics/suggestions', { params })
}

export const analyticsAPI = {
  getDashboard: (): Promise<AxiosResponse<AnalyticsData>> =>
    api.get('/api/analytics/dashboard'),
  
  getPerformance: (newsletterId: number): Promise<AxiosResponse<any>> =>
    api.get(`/api/analytics/performance/${newsletterId}`)
}

export default api
