import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

export function setApiAccessToken(accessToken: string | null): void {
  if (accessToken) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${accessToken}`
    return
  }

  delete apiClient.defaults.headers.common.Authorization
}

export default apiClient
