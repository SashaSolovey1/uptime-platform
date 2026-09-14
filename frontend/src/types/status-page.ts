import type { MonitorStatus } from '@/types/monitor'

export type StatusPageStatus = 'operational' | 'partial_outage' | 'major_outage' | 'unknown'

export interface StatusPage {
  id: string
  name: string
  slug: string
  published: boolean
}

export interface StatusPageCreate {
  name: string
  slug: string
  published: boolean
}

export interface StatusPageUpdate {
  name?: string
  published?: boolean
}

export interface StatusPageMonitor {
  id: string
  name: string
  status: MonitorStatus
}

export interface PublicStatusPage {
  name: string
  slug: string
  status: StatusPageStatus
  monitors: StatusPageMonitor[]
}
