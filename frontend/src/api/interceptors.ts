import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type { Router } from 'vue-router'

import apiClient from '@/api/client'
import type { useAuthStore } from '@/stores/auth'
import type { useOrganizationStore } from '@/stores/organizations'

type AuthStore = ReturnType<typeof useAuthStore>

type OrganizationStore = ReturnType<typeof useOrganizationStore>

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

const AUTH_ENDPOINTS_WITHOUT_REFRESH = [
  '/api/v1/auth/login',
  '/api/v1/auth/register',
  '/api/v1/auth/refresh',
  '/api/v1/auth/logout',
]

function shouldSkipRefresh(url?: string): boolean {
  if (!url) {
    return false
  }

  return AUTH_ENDPOINTS_WITHOUT_REFRESH.some((path) => {
    return url.endsWith(path)
  })
}

export function setupApiInterceptors(
  authStore: AuthStore,
  organizationStore: OrganizationStore,
  router: Router,
): void {
  apiClient.interceptors.request.use((config) => {
    if (organizationStore.currentOrganizationId) {
      config.headers.set('X-Organization-ID', organizationStore.currentOrganizationId)
    } else {
      config.headers.delete('X-Organization-ID')
    }

    return config
  })

  apiClient.interceptors.response.use(
    (response) => response,

    async (error: AxiosError) => {
      const request = error.config as RetryableRequestConfig | undefined

      if (
        error.response?.status !== 401 ||
        !request ||
        request._retry ||
        shouldSkipRefresh(request.url)
      ) {
        return Promise.reject(error)
      }

      request._retry = true

      try {
        await authStore.refreshAccessToken()

        if (!authStore.accessToken) {
          return Promise.reject(error)
        }

        request.headers.set('Authorization', `Bearer ${authStore.accessToken}`)

        return apiClient(request)
      } catch {
        authStore.clearAuth()
        organizationStore.clear()

        const currentRoute = router.currentRoute.value

        if (currentRoute.name !== 'login') {
          await router.push({
            name: 'login',
            query: {
              redirect: currentRoute.fullPath,
            },
          })
        }

        return Promise.reject(error)
      }
    },
  )
}
