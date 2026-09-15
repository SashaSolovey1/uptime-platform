import type { MaintenanceWindow, MaintenanceWindowStatus } from '@/types/maintenance'

export function getMaintenanceWindowStatus(
  maintenanceWindow: MaintenanceWindow,
  now = Date.now(),
): MaintenanceWindowStatus {
  const startsAt = new Date(maintenanceWindow.starts_at).getTime()

  const endsAt = new Date(maintenanceWindow.ends_at).getTime()

  if (now < startsAt) {
    return 'upcoming'
  }

  if (now < endsAt) {
    return 'active'
  }

  return 'expired'
}
