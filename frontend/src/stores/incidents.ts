import { defineStore } from 'pinia'

import apiClient from '@/api/client'
import type { Incident, IncidentFilters } from '@/types/incident'

interface IncidentState {
  incidents: Incident[]
  loading: boolean
  error: string | null
}

export const useIncidentStore = defineStore('incidents', {
  state: (): IncidentState => ({
    incidents: [],
    loading: false,
    error: null,
  }),

  actions: {
    async getIncidents(filters: IncidentFilters = {}): Promise<Incident[]> {
      const response = await apiClient.get<Incident[]>('/api/v1/incidents', {
        params: {
          status: filters.status ?? undefined,
          monitor_id: filters.monitor_id ?? undefined,
          limit: filters.limit ?? 100,
        },
      })

      return response.data
    },

    async loadIncidents(filters: IncidentFilters = {}): Promise<void> {
      this.loading = true
      this.error = null

      try {
        this.incidents = await this.getIncidents(filters)
      } catch (error) {
        this.incidents = []
        this.error = 'Unable to load incidents'

        throw error
      } finally {
        this.loading = false
      }
    },

    async getIncident(incidentId: string): Promise<Incident> {
      const response = await apiClient.get<Incident>(`/api/v1/incidents/${incidentId}`)

      return response.data
    },

    clear(): void {
      this.incidents = []
      this.loading = false
      this.error = null
    },
  },
})
