export type MonitorType =
  | 'http'
  | 'tcp'
  | 'dns'
  | 'tls'
  | 'icmp'

export type MonitorStatus =
  | 'pending'
  | 'up'
  | 'down'
  | 'paused'

export type HttpMethod =
  | 'GET'
  | 'HEAD'

export type DnsRecordType =
  | 'A'
  | 'AAAA'
  | 'CNAME'
  | 'MX'
  | 'TXT'

export interface HttpMonitorConfig {
  url: string
  method: HttpMethod
  expected_status_codes: number[] | null
  body_contains: string | null
  follow_redirects: boolean
  verify_tls: boolean
}

export interface TcpMonitorConfig {
  host: string
  port: number
}

export interface DnsMonitorConfig {
  host: string
  record_type: DnsRecordType
}

export interface TlsMonitorConfig {
  host: string
  port: number
  expiry_threshold_days: number
}

export interface IcmpMonitorConfig {
  host: string
}

interface BaseMonitor {
  id: string
  name: string
  interval_seconds: number
  timeout_seconds: number
  status: MonitorStatus
  created_at: string
  next_check_at: string
  failure_threshold: number
  recovery_threshold: number
  consecutive_failures: number
  consecutive_successes: number
}

export interface HttpMonitor extends BaseMonitor {
  monitor_type: 'http'
  config: HttpMonitorConfig
}

export interface TcpMonitor extends BaseMonitor {
  monitor_type: 'tcp'
  config: TcpMonitorConfig
}

export interface DnsMonitor extends BaseMonitor {
  monitor_type: 'dns'
  config: DnsMonitorConfig
}

export interface TlsMonitor extends BaseMonitor {
  monitor_type: 'tls'
  config: TlsMonitorConfig
}

export interface IcmpMonitor extends BaseMonitor {
  monitor_type: 'icmp'
  config: IcmpMonitorConfig
}

export type Monitor =
  | HttpMonitor
  | TcpMonitor
  | DnsMonitor
  | TlsMonitor
  | IcmpMonitor

interface BaseMonitorCreate {
  name: string
  interval_seconds: number
  timeout_seconds: number
  failure_threshold: number
  recovery_threshold: number
}

export type MonitorCreate =
  | (
      BaseMonitorCreate
      & {
        monitor_type: 'http'
        config: HttpMonitorConfig
      }
    )
  | (
      BaseMonitorCreate
      & {
        monitor_type: 'tcp'
        config: TcpMonitorConfig
      }
    )
  | (
      BaseMonitorCreate
      & {
        monitor_type: 'dns'
        config: DnsMonitorConfig
      }
    )
  | (
      BaseMonitorCreate
      & {
        monitor_type: 'tls'
        config: TlsMonitorConfig
      }
    )
  | (
      BaseMonitorCreate
      & {
        monitor_type: 'icmp'
        config: IcmpMonitorConfig
      }
    )

export type MonitorConfigUpdate =
  | Partial<HttpMonitorConfig>
  | Partial<TcpMonitorConfig>
  | Partial<DnsMonitorConfig>
  | Partial<TlsMonitorConfig>
  | Partial<IcmpMonitorConfig>

export interface MonitorUpdate {
  name?: string
  config?: MonitorConfigUpdate
  interval_seconds?: number
  timeout_seconds?: number
  failure_threshold?: number
  recovery_threshold?: number
}
