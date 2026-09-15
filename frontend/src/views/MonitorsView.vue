<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'

import { useMonitorStore } from '@/stores/monitors'
import { useOrganizationStore } from '@/stores/organizations'
import type { Monitor, MonitorStatus } from '@/types/monitor'

const monitorStore = useMonitorStore()
const organizationStore = useOrganizationStore()

const canManageMonitors = computed(() => {
  const role = organizationStore.currentOrganization?.role

  return role === 'owner' || role === 'admin' || role === 'member'
})

async function loadMonitors(): Promise<void> {
  try {
    await monitorStore.loadMonitors()
  } catch {}
}

function getMonitorTarget(monitor: Monitor): string {
  switch (monitor.monitor_type) {
    case 'http':
      return monitor.config.url

    case 'tcp':
    case 'tls':
      return `${monitor.config.host}:${monitor.config.port}`

    case 'dns':
      return `${monitor.config.host} (${monitor.config.record_type})`

    case 'icmp':
      return monitor.config.host
  }
}

function getStatusLabel(status: MonitorStatus): string {
  switch (status) {
    case 'up':
      return 'Up'

    case 'down':
      return 'Down'

    case 'pending':
      return 'Pending'

    case 'paused':
      return 'Paused'
  }
}

onMounted(async () => {
  await loadMonitors()
})

watch(
  () => organizationStore.currentOrganizationId,
  async (currentOrganizationId, previousOrganizationId) => {
    if (currentOrganizationId && currentOrganizationId !== previousOrganizationId) {
      await loadMonitors()
    }
  },
)
</script>

<template>
  <section class="monitors-page">
    <div class="monitors-page__header">
      <div>
        <h1>Monitors</h1>

        <p>Monitor your services and infrastructure.</p>
      </div>

      <RouterLink v-if="canManageMonitors" class="create-monitor-button" to="/monitors/new">
        Create monitor
      </RouterLink>
    </div>

    <p v-if="monitorStore.loading" class="monitors-page__message">Loading monitors...</p>

    <div v-else-if="monitorStore.error" class="monitors-page__error">
      <p>
        {{ monitorStore.error }}
      </p>

      <button type="button" @click="loadMonitors">Try again</button>
    </div>

    <div v-else-if="monitorStore.monitors.length === 0" class="monitors-page__empty">
      <h2>No monitors yet</h2>

      <p>Create your first monitor to start checking a service.</p>
    </div>

    <div v-else class="monitors-table-wrapper">
      <table class="monitors-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Type</th>
            <th>Target</th>
            <th>Interval</th>
            <th>Next check</th>
            <th v-if="canManageMonitors">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="monitor in monitorStore.monitors" :key="monitor.id">
            <td>
              <RouterLink class="monitor-name" :to="`/monitors/${monitor.id}`">
                {{ monitor.name }}
              </RouterLink>
            </td>

            <td>
              <span class="monitor-status" :class="`monitor-status--${monitor.status}`">
                {{ getStatusLabel(monitor.status) }}
              </span>
            </td>

            <td class="monitor-type">
              {{ monitor.monitor_type.toUpperCase() }}
            </td>

            <td class="monitor-target">
              {{ getMonitorTarget(monitor) }}
            </td>

            <td>{{ monitor.interval_seconds }}s</td>

            <td>
              {{ new Date(monitor.next_check_at).toLocaleString() }}
            </td>
            <td v-if="canManageMonitors">
              <RouterLink class="monitor-edit-link" :to="`/monitors/${monitor.id}/edit`">
                Edit
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style lang="scss">
@use '@/assets/scss/pages/monitors';
</style>
