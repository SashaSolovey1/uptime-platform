import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { setupApiInterceptors } from '@/api/interceptors'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import { useOrganizationStore } from '@/stores/organizations'

import './assets/scss/main.scss'

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)

const authStore = useAuthStore(pinia)
const organizationStore = useOrganizationStore(pinia)

setupApiInterceptors(authStore, organizationStore, router)

app.use(router)

app.mount('#app')
