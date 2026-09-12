export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
}

export interface MeResponse {
  id: string
  email: string
}

export interface RegisterRequest {
  email: string
  password: string
  organization_name: string
}

export interface RegisterResponse {
  user_id: string
  email: string
  organization_id: string
  organization_name: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
}
