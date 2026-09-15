<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useIncidentStore } from '@/stores/incidents'
import { useMonitorStore } from '@/stores/monitors'
import { useOrganizationStore } from '@/stores/organizations'
import type { Incident } from '@/types/incident'

const route = useRoute()
const router = useRouter()

const incidentStore = useIncidentStore()
const monitorStore = useMonitorStore()
const organizationStore = useOrganizationStore()

const incident = ref<Incident | null>(null)

const loading = ref(true)
const loadError = ref<string | null>(null)

const monitor = computed(() => {
  if (!incident.value) {
    return null
  }

  return (
    monitorStore.monitors.find((monitor) => {
      return monitor.id === incident.value?.monitor_id
    }) ?? null
  )
})

const duration = computed(() => {
  if (!incident.value) {
    return '—'
  }

  const startedAt = new Date(incident.value.started_at)

  const endedAt = incident.value.resolved_at ? new Date(incident.value.resolved_at) : new Date()

  const totalMinutes = Math.max(
    0,
    Math.floor((endedAt.getTime() - startedAt.getTime()) / 1000 / 60),
  )

  if (totalMinutes < 60) {
    return `${totalMinutes}m`
  }

  const totalHours = Math.floor(totalMinutes / 60)

  if (totalHours < 24) {
    return `${totalHours}h ${totalMinutes % 60}m`
  }

  return `${Math.floor(totalHours / 24)}d ${totalHours % 24}h`
})

function getIncidentId(): string | null {
  const incidentId = route.params.incidentId

  if (typeof incidentId !== 'string') {
    return null
  }

  return incidentId
}

async function loadIncident(): Promise<void> {
  const incidentId = getIncidentId()

  if (!incidentId) {
    loadError.value = 'Invalid incident ID'
    loading.value = false
    return
  }

  loading.value = true
  loadError.value = null

  try {
    const [loadedIncident] = await Promise.all([
      incidentStore.getIncident(incidentId),
      monitorStore.loadMonitors(),
    ])

    incident.value = loadedIncident
  } catch {
    incident.value = null
    loadError.value = 'Unable to load incident'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadIncident()
})

watch(
  () => organizationStore.currentOrganizationId,
  async (currentOrganizationId, previousOrganizationId) => {
    if (previousOrganizationId && currentOrganizationId !== previousOrganizationId) {
      await router.push('/incidents')
    }
  },
)
</script>

<template>
  <section class="incident-details">
    <RouterLink class="incident-details__back" to="/incidents"> ← Back to incidents </RouterLink>

    <p v-if="loading">Loading incident...</p>

    <div v-else-if="loadError" class="message-error">
      {{ loadError }}
    </div>

    <template v-else-if="incident">
      <div class="incident-details__header">
        <div>
          <div class="incident-details__title">
            <h1>Incident</h1>

            <span class="incident-status" :class="`incident-status--${incident.status}`">
              {{ incident.status === 'open' ? 'Open' : 'Resolved' }}
            </span>
          </div>

          <p>
            {{ incident.id }}
          </p>
        </div>
      </div>

      <div class="incident-summary">
        <div class="summary-card">
          <span>Monitor</span>

          <RouterLink :to="`/monitors/${incident.monitor_id}`">
            {{ monitor?.name ?? incident.monitor_id }}
          </RouterLink>
        </div>

        <div class="summary-card">
          <span>Started</span>

          <strong>
            {{ new Date(incident.started_at).toLocaleString() }}
          </strong>
        </div>

        <div class="summary-card">
          <span>Resolved</span>

          <strong>
            {{
              incident.resolved_at ? new Date(incident.resolved_at).toLocaleString() : 'Still open'
            }}
          </strong>
        </div>

        <div class="summary-card">
          <span>Duration</span>

          <strong>
            {{ duration }}
          </strong>
        </div>
      </div>
    </template>
  </section>
</template>

<style lang="scss">
@use '@/assets/scss/pages/incidents';
</style>
