export interface ApiKey {
  id: string
  name: string
  key_prefix: string
  created_at: string
  last_used_at: string | null
}

export interface ApiKeyCreate {
  name: string
}

export interface ApiKeyCreated extends ApiKey {
  key: string
}
