import { defineStore } from 'pinia'

import apiClient, { setApiAccessToken } from '@/api/client'
import type {
  LoginRequest,
  MeResponse,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
} from '@/types/auth'

interface AuthState {
  accessToken: string | null
  user: MeResponse | null
  initialized: boolean
}

let refreshPromise: Promise<void> | null = null

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: null,
    user: null,
    initialized: false,
  }),

  getters: {
    isAuthenticated: (state): boolean => {
      return state.accessToken !== null && state.user !== null
    },
  },

  actions: {
    async register(data: RegisterRequest): Promise<RegisterResponse> {
      const response = await apiClient.post<RegisterResponse>('/api/v1/auth/register', data)

      return response.data
    },

    async login(credentials: LoginRequest): Promise<void> {
      const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', credentials)

      this.accessToken = response.data.access_token
      setApiAccessToken(this.accessToken)

      try {
        await this.fetchMe()
        this.initialized = true
      } catch (error) {
        this.clearAuth()
        throw error
      }
    },

    async fetchMe(): Promise<void> {
      const response = await apiClient.get<MeResponse>('/api/v1/auth/me')

      this.user = response.data
    },

    async refreshAccessToken(): Promise<void> {
      if (refreshPromise) {
        await refreshPromise
        return
      }

      refreshPromise = (async () => {
        const response = await apiClient.post<TokenResponse>('/api/v1/auth/refresh')

        this.accessToken = response.data.access_token
        setApiAccessToken(this.accessToken)
      })()

      try {
        await refreshPromise
      } finally {
        refreshPromise = null
      }
    },

    async restoreSession(): Promise<void> {
      if (this.initialized) {
        return
      }

      try {
        await this.refreshAccessToken()
        await this.fetchMe()
      } catch {
        this.clearAuth()
      } finally {
        this.initialized = true
      }
    },

    async logout(): Promise<void> {
      await apiClient.post('/api/v1/auth/logout')

      this.clearAuth()
    },

    clearAuth(): void {
      this.accessToken = null
      this.user = null
      this.initialized = true

      setApiAccessToken(null)
    },
  },
})
