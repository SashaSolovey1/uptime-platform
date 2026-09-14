export interface MaintenanceWindow {
  id: string
  monitor_id: string
  starts_at: string
  ends_at: string
  reason: string | null
  created_at: string
}

export interface MaintenanceWindowCreate {
  monitor_id: string
  starts_at: string
  ends_at: string
  reason: string | null
}

export interface MaintenanceWindowFilters {
  monitor_id?: string | null
}

export type MaintenanceWindowStatus = 'upcoming' | 'active' | 'expired'
