import axios, { AxiosInstance, AxiosResponse } from 'axios'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('notebooker-auth')
    if (token) {
      try {
        const authData = JSON.parse(token)
        if (authData.state?.sessionToken) {
          config.headers.Authorization = `Bearer ${authData.state.sessionToken}`
        }
      } catch (error) {
        console.error('Error parsing auth token:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('notebooker-auth')
      window.location.href = '/auth'
    }
    return Promise.reject(error)
  }
)

// API Service Types
export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
}

export interface AuthResponse {
  success: boolean
  user_id: string
  username: string
  session_token: string
  error?: string
}

export interface Project {
  id: number
  name: string
  description: string
  status: string
  created_at: string
  updated_at: string
}

export interface AITask {
  task_id: string
  status: string
  agent_reply?: string
  next_step?: any
  logs?: string
  error?: string
}

// API Service Functions
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/login', credentials)
    return response.data
  },

  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/register', userData)
    return response.data
  },

  verify: async (token: string): Promise<{ valid: boolean; user?: any }> => {
    const response = await api.post('/api/auth/verify', { session_token: token })
    return response.data
  },

  logout: async (token: string): Promise<{ success: boolean }> => {
    const response = await api.post('/api/auth/logout', { session_token: token })
    return response.data
  },
}

export const projectAPI = {
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get('/api/projects')
    return response.data
  },

  createProject: async (projectData: { name: string; description: string }): Promise<{ status: string; project_id?: number }> => {
    const response = await api.post('/api/projects', projectData)
    return response.data
  },

  updateProject: async (projectId: number, projectData: Partial<Project>): Promise<{ status: string }> => {
    const response = await api.put(`/api/projects/${projectId}`, projectData)
    return response.data
  },

  deleteProject: async (projectId: number): Promise<{ status: string }> => {
    const response = await api.delete(`/api/projects/${projectId}`)
    return response.data
  },
}

export const aiAPI = {
  createTask: async (taskData: {
    prompt_context: string
    agent_config?: any
    external_tool_endpoints?: any
  }): Promise<{ task_id: string; status: string; message: string }> => {
    const response = await api.post('/api/ai/tasks', taskData)
    return response.data
  },

  getTaskStatus: async (taskId: string): Promise<AITask> => {
    const response = await api.get(`/api/ai/tasks/${taskId}`)
    return response.data
  },

  cancelTask: async (taskId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/api/ai/tasks/${taskId}`)
    return response.data
  },

  listTasks: async (): Promise<{ active_tasks: any[]; task_history: any[] }> => {
    const response = await api.get('/api/ai/tasks')
    return response.data
  },

  healthCheck: async (): Promise<{ healthy: boolean; service_url: string; message: string }> => {
    const response = await api.get('/api/ai/health')
    return response.data
  },
}

export const contentAPI = {
  analyzeContent: async (content: string): Promise<{ status: string; analysis: string; suggestions: string[] }> => {
    const response = await api.post('/api/analyze_content', { content })
    return response.data
  },

  updatePlanning: async (updates: any): Promise<{ status: string }> => {
    const response = await api.post('/api/update_planning', updates)
    return response.data
  },
}

export default api
