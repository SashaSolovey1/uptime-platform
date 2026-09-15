<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { useIncidentStore } from '@/stores/incidents'
import { useMonitorStore } from '@/stores/monitors'
import { useOrganizationStore } from '@/stores/organizations'
import type { Incident, IncidentStatus } from '@/types/incident'

const incidentStore = useIncidentStore()
const monitorStore = useMonitorStore()
const organizationStore = useOrganizationStore()

const statusFilter = ref<IncidentStatus | ''>('')
const monitorFilter = ref('')

const pageError = ref<string | null>(null)

async function loadIncidents(): Promise<void> {
  try {
    await incidentStore.loadIncidents({
      status: statusFilter.value || null,
      monitor_id: monitorFilter.value || null,
      limit: 100,
    })
  } catch {
    // Store already contains the incident error
  }
}

async function loadPageData(): Promise<void> {
  pageError.value = null

  try {
    await Promise.all([monitorStore.loadMonitors(), loadIncidents()])
  } catch {
    pageError.value = 'Unable to load incidents'
  }
}

function getMonitorName(monitorId: string): string {
  const monitor = monitorStore.monitors.find((monitor) => {
    return monitor.id === monitorId
  })

  return monitor?.name ?? monitorId
}

function getIncidentDuration(incident: Incident): string {
  const startedAt = new Date(incident.started_at)

  const endedAt = incident.resolved_at ? new Date(incident.resolved_at) : new Date()

  const durationMs = endedAt.getTime() - startedAt.getTime()

  const totalMinutes = Math.max(0, Math.floor(durationMs / 1000 / 60))

  if (totalMinutes < 60) {
    return `${totalMinutes}m`
  }

  const totalHours = Math.floor(totalMinutes / 60)

  if (totalHours < 24) {
    const minutes = totalMinutes % 60

    return `${totalHours}h ${minutes}m`
  }

  const days = Math.floor(totalHours / 24)
  const hours = totalHours % 24

  return `${days}d ${hours}h`
}

onMounted(async () => {
  await loadPageData()
})

watch([statusFilter, monitorFilter], async () => {
  await loadIncidents()
})

watch(
  () => organizationStore.currentOrganizationId,
  async (currentOrganizationId, previousOrganizationId) => {
    if (previousOrganizationId && currentOrganizationId !== previousOrganizationId) {
      await loadPageData()
    }
  },
)
</script>

<template>
  <section class="incidents-page">
    <div class="incidents-page__header">
      <div>
        <h1>Incidents</h1>

        <p>Monitor outages and recoveries.</p>
      </div>
    </div>

    <div class="incident-filters">
      <div class="filter-field">
        <label for="incident-status"> Status </label>

        <select id="incident-status" v-model="statusFilter">
          <option value="">All statuses</option>

          <option value="open">Open</option>

          <option value="resolved">Resolved</option>
        </select>
      </div>

      <div class="filter-field">
        <label for="incident-monitor"> Monitor </label>

        <select id="incident-monitor" v-model="monitorFilter">
          <option value="">All monitors</option>

          <option v-for="monitor in monitorStore.monitors" :key="monitor.id" :value="monitor.id">
            {{ monitor.name }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="pageError || incidentStore.error" class="message-error">
      <p>
        {{ pageError ?? incidentStore.error }}
      </p>

      <button type="button" @click="loadPageData">Try again</button>
    </div>

    <p v-else-if="incidentStore.loading" class="incidents-page__message">Loading incidents...</p>

    <div v-else-if="incidentStore.incidents.length === 0" class="incidents-page__empty">
      <h2>No incidents found</h2>

      <p>There are no incidents matching the selected filters.</p>
    </div>

    <div v-else class="incidents-table-wrapper">
      <table class="incidents-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Monitor</th>
            <th>Started</th>
            <th>Resolved</th>
            <th>Duration</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="incident in incidentStore.incidents" :key="incident.id">
            <td>
              <RouterLink class="incident-link" :to="`/incidents/${incident.id}`">
                <span class="incident-status" :class="`incident-status--${incident.status}`">
                  {{ incident.status === 'open' ? 'Open' : 'Resolved' }}
                </span>
              </RouterLink>
            </td>

            <td>
              <RouterLink class="monitor-link" :to="`/monitors/${incident.monitor_id}`">
                {{ getMonitorName(incident.monitor_id) }}
              </RouterLink>
            </td>

            <td>
              {{ new Date(incident.started_at).toLocaleString() }}
            </td>

            <td>
              {{ incident.resolved_at ? new Date(incident.resolved_at).toLocaleString() : '—' }}
            </td>

            <td>
              {{ getIncidentDuration(incident) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style lang="scss">
@use '@/assets/scss/pages/incidents';
</style>
