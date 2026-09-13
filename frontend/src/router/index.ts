import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/layouts/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import DashboardView from '@/views/DashboardView.vue'
import LoginView from '@/views/LoginView.vue'
import MonitorsView from '@/views/MonitorsView.vue'
import RegisterView from '@/views/RegisterView.vue'
import MonitorCreateView from '@/views/MonitorCreateView.vue'
import MonitorEditView from '@/views/MonitorEditView.vue'
import MonitorDetailsView from '@/views/MonitorDetailsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/',
      component: AppLayout,
      meta: {
        requiresAuth: true,
      },
      children: [
        {
          path: '',
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView,
        },
        {
          path: 'monitors',
          name: 'monitors',
          component: MonitorsView,
        },
        {
          path: 'monitors/new',
          name: 'monitor-create',
          component: MonitorCreateView,
        },
        {
          path: 'monitors/:monitorId/edit',
          name: 'monitor-edit',
          component: MonitorEditView,
        },
        {
          path: 'monitors/:monitorId',
          name: 'monitor-details',
          component: MonitorDetailsView,
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.restoreSession()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (authStore.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    return {
      name: 'dashboard',
    }
  }
})

export default router
