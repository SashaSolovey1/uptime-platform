export type IncidentStatus = 'open' | 'resolved'

export interface Incident {
  id: string
  monitor_id: string
  status: IncidentStatus
  started_at: string
  resolved_at: string | null
}

export interface IncidentFilters {
  status?: IncidentStatus | null
  monitor_id?: string | null
  limit?: number
}
