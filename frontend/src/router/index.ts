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
import IncidentDetailsView from '@/views/IncidentDetailsView.vue'
import IncidentsView from '@/views/IncidentsView.vue'
import MaintenanceView from '@/views/MaintenanceView.vue'
import NotificationsView from '@/views/NotificationsView.vue'
import PublicStatusPageView from '@/views/PublicStatusPageView.vue'
import StatusPageDetailsView from '@/views/StatusPageDetailsView.vue'
import StatusPagesView from '@/views/StatusPagesView.vue'

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
      path: '/status/:slug',
      name: 'public-status-page',
      component: PublicStatusPageView,
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
        {
          path: 'incidents',
          name: 'incidents',
          component: IncidentsView,
        },
        {
          path: 'incidents/:incidentId',
          name: 'incident-details',
          component: IncidentDetailsView,
        },
        {
          path: 'maintenance',
          name: 'maintenance',
          component: MaintenanceView,
        },
        {
          path: 'notifications',
          name: 'notifications',
          component: NotificationsView,
        },
        {
          path: 'status-pages',
          name: 'status-pages',
          component: StatusPagesView,
        },
        {
          path: 'status-pages/:pageId',
          name: 'status-page-details',
          component: StatusPageDetailsView,
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
