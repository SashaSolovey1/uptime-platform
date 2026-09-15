<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import apiClient from '@/api/client'
import { useIncidentStore } from '@/stores/incidents'
import { useMonitorStore } from '@/stores/monitors'
import { useOrganizationStore } from '@/stores/organizations'
import type { Incident } from '@/types/incident'

const monitorStore = useMonitorStore()
const incidentStore = useIncidentStore()
const organizationStore = useOrganizationStore()

const openIncidents = ref<Incident[]>([])
const recentIncidents = ref<Incident[]>([])

const apiStatus = ref('Checking...')
const loading = ref(false)
const error = ref<string | null>(null)
const lastUpdated = ref<Date | null>(null)

const totalMonitors = computed(() => {
  return monitorStore.monitors.length
})

const upMonitors = computed(() => {
  return monitorStore.monitors.filter((monitor) => {
    return monitor.status === 'up'
  })
})

const downMonitors = computed(() => {
  return monitorStore.monitors.filter((monitor) => {
    return monitor.status === 'down'
  })
})

const pausedMonitors = computed(() => {
  return monitorStore.monitors.filter((monitor) => {
    return monitor.status === 'paused'
  })
})

const pendingMonitors = computed(() => {
  return monitorStore.monitors.filter((monitor) => {
    return monitor.status === 'pending'
  })
})

const problemMonitors = computed(() => {
  return downMonitors.value.slice(0, 5)
})

const monitorNames = computed(() => {
  return new Map(
    monitorStore.monitors.map((monitor) => {
      return [monitor.id, monitor.name]
    }),
  )
})

function getMonitorName(monitorId: string): string {
  return monitorNames.value.get(monitorId) ?? 'Unknown monitor'
}

function formatDate(date: string): string {
  return new Date(date).toLocaleString()
}

function formatIncidentDuration(incident: Incident): string {
  const startedAt = new Date(incident.started_at).getTime()

  const endedAt = incident.resolved_at ? new Date(incident.resolved_at).getTime() : Date.now()

  const durationSeconds = Math.max(0, Math.floor((endedAt - startedAt) / 1000))

  if (durationSeconds < 60) {
    return `${durationSeconds}s`
  }

  const durationMinutes = Math.floor(durationSeconds / 60)

  if (durationMinutes < 60) {
    return `${durationMinutes}m`
  }

  const durationHours = Math.floor(durationMinutes / 60)

  if (durationHours < 24) {
    return `${durationHours}h`
  }

  const durationDays = Math.floor(durationHours / 24)

  return `${durationDays}d`
}

async function loadApiStatus(): Promise<void> {
  try {
    const response = await apiClient.get<{ status: string }>('/health')

    apiStatus.value = response.data.status
  } catch {
    apiStatus.value = 'Unavailable'
  }
}

async function loadDashboard(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const [, loadedOpenIncidents, loadedRecentIncidents] = await Promise.all([
      monitorStore.loadMonitors(),

      incidentStore.getIncidents({
        status: 'open',
        limit: 500,
      }),

      incidentStore.getIncidents({
        limit: 5,
      }),

      loadApiStatus(),
    ])

    openIncidents.value = loadedOpenIncidents

    recentIncidents.value = loadedRecentIncidents.sort((first, second) => {
      return new Date(second.started_at).getTime() - new Date(first.started_at).getTime()
    })

    lastUpdated.value = new Date()
  } catch {
    error.value = 'Unable to load dashboard data'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadDashboard()
})

watch(
  () => organizationStore.currentOrganizationId,
  async (currentOrganizationId, previousOrganizationId) => {
    if (currentOrganizationId && currentOrganizationId !== previousOrganizationId) {
      openIncidents.value = []
      recentIncidents.value = []

      await loadDashboard()
    }
  },
)
</script>

<template>
  <section class="dashboard-page">
    <div class="dashboard-page__header">
      <div>
        <h1>Dashboard</h1>

        <p>Overview of the current organization.</p>
      </div>

      <div class="dashboard-page__actions">
        <span v-if="lastUpdated" class="text-muted">
          Updated
          {{ lastUpdated.toLocaleTimeString() }}
        </span>

        <button class="button-secondary" type="button" :disabled="loading" @click="loadDashboard">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="message-error">
      {{ error }}
    </div>

    <div class="dashboard-summary">
      <RouterLink class="dashboard-summary-card" to="/monitors">
        <span class="dashboard-summary-card__label"> Total monitors </span>

        <strong class="dashboard-summary-card__value">
          {{ totalMonitors }}
        </strong>
      </RouterLink>

      <RouterLink class="dashboard-summary-card" to="/monitors">
        <span class="dashboard-summary-card__label"> Up </span>

        <strong class="dashboard-summary-card__value dashboard-summary-card__value--success">
          {{ upMonitors.length }}
        </strong>
      </RouterLink>

      <RouterLink class="dashboard-summary-card" to="/monitors">
        <span class="dashboard-summary-card__label"> Down </span>

        <strong class="dashboard-summary-card__value dashboard-summary-card__value--danger">
          {{ downMonitors.length }}
        </strong>
      </RouterLink>

      <RouterLink class="dashboard-summary-card" to="/incidents">
        <span class="dashboard-summary-card__label"> Open incidents </span>

        <strong class="dashboard-summary-card__value dashboard-summary-card__value--danger">
          {{ openIncidents.length }}
        </strong>
      </RouterLink>
    </div>

    <div class="dashboard-grid">
      <div class="section-card">
        <div class="section-header">
          <div>
            <h2>Monitor status</h2>

            <p>Current state of all monitors.</p>
          </div>

          <RouterLink class="text-link" to="/monitors"> View monitors </RouterLink>
        </div>

        <div class="dashboard-status-list">
          <div class="dashboard-status-row">
            <span class="monitor-status monitor-status--up"> Up </span>

            <strong>
              {{ upMonitors.length }}
            </strong>
          </div>

          <div class="dashboard-status-row">
            <span class="monitor-status monitor-status--down"> Down </span>

            <strong>
              {{ downMonitors.length }}
            </strong>
          </div>

          <div class="dashboard-status-row">
            <span class="monitor-status monitor-status--paused"> Paused </span>

            <strong>
              {{ pausedMonitors.length }}
            </strong>
          </div>

          <div class="dashboard-status-row">
            <span class="monitor-status monitor-status--pending"> Pending </span>

            <strong>
              {{ pendingMonitors.length }}
            </strong>
          </div>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <div>
            <h2>Platform</h2>

            <p>Backend API status.</p>
          </div>
        </div>

        <div class="dashboard-api-status">
          <span>API</span>

          <strong
            :class="{
              'dashboard-api-status--success':
                apiStatus !== 'Unavailable' && apiStatus !== 'Checking...',
              'dashboard-api-status--danger': apiStatus === 'Unavailable',
            }"
          >
            {{ apiStatus }}
          </strong>
        </div>
      </div>
    </div>

    <div class="section-card">
      <div class="section-header">
        <div>
          <h2>Monitors requiring attention</h2>

          <p>Monitors that are currently down.</p>
        </div>

        <RouterLink class="text-link" to="/monitors"> View all </RouterLink>
      </div>

      <p v-if="loading && totalMonitors === 0" class="text-muted">Loading monitors...</p>

      <p v-else-if="problemMonitors.length === 0" class="dashboard-healthy">
        All monitors are currently operational.
      </p>

      <div v-else class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Monitor</th>
              <th>Type</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="monitor in problemMonitors" :key="monitor.id">
              <td>
                <RouterLink
                  class="text-link"
                  :to="{
                    name: 'monitor-details',
                    params: {
                      monitorId: monitor.id,
                    },
                  }"
                >
                  {{ monitor.name }}
                </RouterLink>
              </td>

              <td>
                {{ monitor.monitor_type.toUpperCase() }}
              </td>

              <td>
                <span class="monitor-status monitor-status--down"> Down </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="section-card">
      <div class="section-header">
        <div>
          <h2>Recent incidents</h2>

          <p>Latest incidents in this organization.</p>
        </div>

        <RouterLink class="text-link" to="/incidents"> View all </RouterLink>
      </div>

      <p v-if="loading && recentIncidents.length === 0" class="text-muted">Loading incidents...</p>

      <p v-else-if="recentIncidents.length === 0" class="text-muted">No incidents yet.</p>

      <div v-else class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Monitor</th>
              <th>Status</th>
              <th>Started</th>
              <th>Duration</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="incident in recentIncidents" :key="incident.id">
              <td>
                <RouterLink
                  class="text-link"
                  :to="{
                    name: 'monitor-details',
                    params: {
                      monitorId: incident.monitor_id,
                    },
                  }"
                >
                  {{ getMonitorName(incident.monitor_id) }}
                </RouterLink>
              </td>

              <td>
                <RouterLink
                  :to="{
                    name: 'incident-details',
                    params: {
                      incidentId: incident.id,
                    },
                  }"
                >
                  <span class="incident-status" :class="`incident-status--${incident.status}`">
                    {{ incident.status }}
                  </span>
                </RouterLink>
              </td>

              <td>
                {{ formatDate(incident.started_at) }}
              </td>

              <td>
                {{ formatIncidentDuration(incident) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
@use '@/assets/scss/pages/dashboard';
</style>
