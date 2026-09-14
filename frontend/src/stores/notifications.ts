import { defineStore } from 'pinia'

import apiClient from '@/api/client'
import type {
  NotificationDestination,
  NotificationDestinationCreate,
  NotificationDestinationUpdate,
} from '@/types/notification'

interface NotificationState {
  destinations: NotificationDestination[]
  loading: boolean
  error: string | null
}

export const useNotificationStore = defineStore('notifications', {
  state: (): NotificationState => ({
    destinations: [],
    loading: false,
    error: null,
  }),

  actions: {
    async loadDestinations(): Promise<void> {
      this.loading = true
      this.error = null

      try {
        const response = await apiClient.get<NotificationDestination[]>(
          '/api/v1/notification-destinations',
        )

        this.destinations = response.data
      } catch (error) {
        this.destinations = []
        this.error = 'Unable to load notification destinations'

        throw error
      } finally {
        this.loading = false
      }
    },

    async createDestination(data: NotificationDestinationCreate): Promise<NotificationDestination> {
      const response = await apiClient.post<NotificationDestination>(
        '/api/v1/notification-destinations',
        data,
      )

      return response.data
    },

    async updateDestination(
      destinationId: string,
      data: NotificationDestinationUpdate,
    ): Promise<NotificationDestination> {
      const response = await apiClient.patch<NotificationDestination>(
        `/api/v1/notification-destinations/${destinationId}`,
        data,
      )

      const index = this.destinations.findIndex((destination) => {
        return destination.id === destinationId
      })

      if (index !== -1) {
        this.destinations[index] = response.data
      }

      return response.data
    },

    async deleteDestination(destinationId: string): Promise<void> {
      await apiClient.delete(`/api/v1/notification-destinations/${destinationId}`)

      this.destinations = this.destinations.filter((destination) => {
        return destination.id !== destinationId
      })
    },

    clear(): void {
      this.destinations = []
      this.loading = false
      this.error = null
    },
  },
})
