import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { setupApiInterceptors } from '@/api/interceptors'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

import './assets/main.css'

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)

const authStore = useAuthStore(pinia)

setupApiInterceptors(authStore, router)

app.use(router)

app.mount('#app')
