export type OrganizationRole = 'owner' | 'admin' | 'member' | 'viewer'

export interface Organization {
  id: string
  name: string
  role: OrganizationRole
  created_at: string
}
