import { defineStore } from 'pinia'

import apiClient from '@/api/client'
import type {
  Monitor,
  MonitorCreate,
  MonitorUpdate,
} from '@/types/monitor'

interface MonitorState {
  monitors: Monitor[]
  loading: boolean
  error: string | null
}

export const useMonitorStore = defineStore('monitors', {
  state: (): MonitorState => ({
    monitors: [],
    loading: false,
    error: null,
  }),

  actions: {
    async loadMonitors(): Promise<void> {
      this.loading = true
      this.error = null

      try {
        const response = await apiClient.get<Monitor[]>(
          '/api/v1/monitors',
        )

        this.monitors = response.data
      } catch (error) {
        this.monitors = []
        this.error = 'Unable to load monitors'

        throw error
      } finally {
        this.loading = false
      }
    },

    async getMonitor(monitorId: string): Promise<Monitor> {
      const response = await apiClient.get<Monitor>(
        `/api/v1/monitors/${monitorId}`,
      )

      return response.data
    },

    async createMonitor(data: MonitorCreate): Promise<Monitor> {
      const response = await apiClient.post<Monitor>(
        '/api/v1/monitors',
        data,
      )

      return response.data
    },

    async updateMonitor(
      monitorId: string,
      data: MonitorUpdate,
    ): Promise<Monitor> {
      const response = await apiClient.patch<Monitor>(
        `/api/v1/monitors/${monitorId}`,
        data,
      )

      const monitorIndex = this.monitors.findIndex((monitor) => {
        return monitor.id === monitorId
      })

      if (monitorIndex !== -1) {
        this.monitors[monitorIndex] = response.data
      }

      return response.data
    },

    async deleteMonitor(monitorId: string): Promise<void> {
      await apiClient.delete(
        `/api/v1/monitors/${monitorId}`,
      )

      this.monitors = this.monitors.filter((monitor) => {
        return monitor.id !== monitorId
      })
    },

    clear(): void {
      this.monitors = []
      this.loading = false
      this.error = null
    },
  },
})
