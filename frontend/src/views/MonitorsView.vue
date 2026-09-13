<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'

import { useMonitorStore } from '@/stores/monitors'
import { useOrganizationStore } from '@/stores/organizations'
import type { Monitor, MonitorStatus } from '@/types/monitor'

const monitorStore = useMonitorStore()
const organizationStore = useOrganizationStore()

const canManageMonitors = computed(() => {
  const role = organizationStore.currentOrganization?.role

  return (
    role === 'owner'
    || role === 'admin'
    || role === 'member'
  )
})

async function loadMonitors(): Promise<void> {
  try {
    await monitorStore.loadMonitors()
  } catch {

  }
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
    if (
      currentOrganizationId
      && currentOrganizationId !== previousOrganizationId
    ) {
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

      <p>
        Monitor your services and infrastructure.
      </p>
    </div>

    <RouterLink
      v-if="canManageMonitors"
      class="create-monitor-button"
      to="/monitors/new"
    >
      Create monitor
    </RouterLink>
  </div>

    <p
      v-if="monitorStore.loading"
      class="monitors-page__message"
    >
      Loading monitors...
    </p>

    <div
      v-else-if="monitorStore.error"
      class="monitors-page__error"
    >
      <p>
        {{ monitorStore.error }}
      </p>

      <button
        type="button"
        @click="loadMonitors"
      >
        Try again
      </button>
    </div>

    <div
      v-else-if="monitorStore.monitors.length === 0"
      class="monitors-page__empty"
    >
      <h2>No monitors yet</h2>

      <p>
        Create your first monitor to start checking a service.
      </p>
    </div>

    <div
      v-else
      class="monitors-table-wrapper"
    >
      <table class="monitors-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Type</th>
            <th>Target</th>
            <th>Interval</th>
            <th>Next check</th>
            <th v-if="canManageMonitors">
            Actions
            </th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="monitor in monitorStore.monitors"
            :key="monitor.id"
          >
            <td>
              <RouterLink
                class="monitor-name"
                :to="`/monitors/${monitor.id}`"
              >
                {{ monitor.name }}
              </RouterLink>
            </td>

            <td>
              <span
                class="monitor-status"
                :class="`monitor-status--${monitor.status}`"
              >
                {{ getStatusLabel(monitor.status) }}
              </span>
            </td>

            <td class="monitor-type">
              {{ monitor.monitor_type.toUpperCase() }}
            </td>

            <td class="monitor-target">
              {{ getMonitorTarget(monitor) }}
            </td>

            <td>
              {{ monitor.interval_seconds }}s
            </td>

            <td>
              {{ new Date(monitor.next_check_at).toLocaleString() }}
            </td>
            <td v-if="canManageMonitors">
            <RouterLink
              class="monitor-edit-link"
              :to="`/monitors/${monitor.id}/edit`"
            >
              Edit
            </RouterLink>
          </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.monitors-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-bottom: 24px;
}

.monitors-page__header h1 {
  margin: 0 0 8px;

  color: #0f172a;
  font-size: 28px;
}

.monitors-page__header p {
  margin: 0;

  color: #64748b;
}

.monitors-page__message {
  color: #64748b;
}

.monitors-page__error {
  padding: 20px;

  border: 1px solid #fecaca;
  border-radius: 8px;

  color: #991b1b;
  background: #fef2f2;
}

.monitors-page__error p {
  margin: 0 0 12px;
}

.monitors-page__error button {
  padding: 8px 12px;

  border: 1px solid #fca5a5;
  border-radius: 6px;

  color: #991b1b;
  background: #ffffff;

  cursor: pointer;
}

.monitors-page__empty {
  padding: 48px 24px;

  border: 1px dashed #cbd5e1;
  border-radius: 8px;

  text-align: center;
}

.monitors-page__empty h2 {
  margin: 0 0 8px;

  color: #334155;
  font-size: 18px;
}

.monitors-page__empty p {
  margin: 0;

  color: #64748b;
}

.monitors-table-wrapper {
  overflow-x: auto;

  border: 1px solid #e2e8f0;
  border-radius: 8px;

  background: #ffffff;
}

.monitors-table {
  width: 100%;

  border-collapse: collapse;
}

.monitors-table th,
.monitors-table td {
  padding: 14px 16px;

  border-bottom: 1px solid #e2e8f0;

  text-align: left;
  white-space: nowrap;
}

.monitors-table th {
  color: #64748b;
  background: #f8fafc;

  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.monitors-table tbody tr:last-child td {
  border-bottom: 0;
}

.monitors-table tbody tr:hover {
  background: #f8fafc;
}

.monitor-name {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
}

.monitor-name:hover {
  text-decoration: underline;
}

.monitor-status {
  display: inline-block;

  padding: 4px 8px;

  border-radius: 999px;

  font-size: 12px;
  font-weight: 600;
}

.monitor-status--up {
  color: #166534;
  background: #dcfce7;
}

.monitor-status--down {
  color: #991b1b;
  background: #fee2e2;
}

.monitor-status--pending {
  color: #854d0e;
  background: #fef9c3;
}

.monitor-status--paused {
  color: #475569;
  background: #f1f5f9;
}

.monitor-type {
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}

.monitor-target {
  overflow: hidden;

  max-width: 320px;

  color: #475569;
  text-overflow: ellipsis;
}
.create-monitor-button {
  padding: 10px 16px;

  border-radius: 6px;

  color: #ffffff;
  background: #2563eb;

  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}

.create-monitor-button:hover {
  background: #1d4ed8;
}
.monitor-edit-link {
  color: #2563eb;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
}

.monitor-edit-link:hover {
  text-decoration: underline;
}
</style>
