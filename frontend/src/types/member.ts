import type { OrganizationRole } from '@/types/organization'

export interface OrganizationMember {
  user_id: string
  email: string
  role: OrganizationRole
  created_at: string
}

export interface OrganizationMemberCreate {
  email: string
  role: OrganizationRole
}

export interface OrganizationMemberUpdate {
  role: OrganizationRole
}
