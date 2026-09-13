<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useMonitorStore } from '@/stores/monitors'
import { useOrganizationStore } from '@/stores/organizations'
import type {
  Check,
  Monitor,
  MonitorStatistics,
  MonitorStatus,
  StatisticsPeriod,
} from '@/types/monitor'

const route = useRoute()
const router = useRouter()

const monitorStore = useMonitorStore()
const organizationStore = useOrganizationStore()

const monitor = ref<Monitor | null>(null)
const lastManualCheck = ref<Check | null>(null)

const checks = ref<Check[]>([])

const statistics = ref<MonitorStatistics | null>(null)
const statisticsPeriod = ref<StatisticsPeriod>('24h')

const statisticsLoading = ref(false)
const statisticsError = ref<string | null>(null)

const checksLoading = ref(false)
const checksError = ref<string | null>(null)

const loading = ref(true)
const loadError = ref<string | null>(null)

const isRunningCheck = ref(false)
const checkError = ref<string | null>(null)

const canManageMonitor = computed(() => {
  const role = organizationStore.currentOrganization?.role

  return role === 'owner' || role === 'admin' || role === 'member'
})

function getMonitorId(): string | null {
  const monitorId = route.params.monitorId

  if (typeof monitorId !== 'string') {
    return null
  }

  return monitorId
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

async function loadMonitor(): Promise<void> {
  const monitorId = getMonitorId()

  if (!monitorId) {
    loadError.value = 'Invalid monitor ID'
    loading.value = false
    return
  }

  loading.value = true
  loadError.value = null

  try {
    monitor.value = await monitorStore.getMonitor(monitorId)
  } catch {
    monitor.value = null
    loadError.value = 'Unable to load monitor'
  } finally {
    loading.value = false
  }
}

async function loadChecks(): Promise<void> {
  const monitorId = getMonitorId()

  if (!monitorId) {
    return
  }

  checksLoading.value = true
  checksError.value = null

  try {
    checks.value = await monitorStore.getMonitorChecks(monitorId, 50)
  } catch {
    checks.value = []
    checksError.value = 'Unable to load check history'
  } finally {
    checksLoading.value = false
  }
}

async function runCheck(): Promise<void> {
  if (!monitor.value) {
    return
  }

  checkError.value = null
  isRunningCheck.value = true

  try {
    lastManualCheck.value = await monitorStore.runMonitorCheck(monitor.value.id)

    await loadMonitor()
    await loadChecks()
    await loadStatistics()
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        checkError.value = detail
      } else {
        checkError.value = 'Unable to run monitor check'
      }
    } else {
      checkError.value = 'Unable to run monitor check'
    }
  } finally {
    isRunningCheck.value = false
  }
}

async function loadStatistics(): Promise<void> {
  const monitorId = getMonitorId()

  if (!monitorId) {
    return
  }

  statisticsLoading.value = true
  statisticsError.value = null

  try {
    statistics.value = await monitorStore.getMonitorStatistics(monitorId, statisticsPeriod.value)
  } catch {
    statistics.value = null
    statisticsError.value = 'Unable to load statistics'
  } finally {
    statisticsLoading.value = false
  }
}

onMounted(async () => {
  await loadMonitor()

  if (monitor.value) {
    await loadChecks()
    await loadStatistics()
  }
})

watch(
  () => organizationStore.currentOrganizationId,
  async (currentOrganizationId, previousOrganizationId) => {
    if (previousOrganizationId && currentOrganizationId !== previousOrganizationId) {
      await router.push('/monitors')
    }
  },
)

watch(statisticsPeriod, async () => {
  await loadStatistics()
})
</script>

<template>
  <section class="monitor-details">
    <div class="monitor-details__top">
      <RouterLink class="monitor-details__back" to="/monitors"> ← Back to monitors </RouterLink>
    </div>

    <p v-if="loading">Loading monitor...</p>

    <div v-else-if="loadError" class="message-error">
      {{ loadError }}
    </div>

    <template v-else-if="monitor">
      <div class="monitor-details__header">
        <div>
          <div class="monitor-details__title">
            <h1>{{ monitor.name }}</h1>

            <span class="monitor-status" :class="`monitor-status--${monitor.status}`">
              {{ getStatusLabel(monitor.status) }}
            </span>
          </div>

          <p class="monitor-details__target">
            {{ getMonitorTarget(monitor) }}
          </p>
        </div>

        <div class="monitor-details__actions">
          <RouterLink
            v-if="canManageMonitor"
            class="button-secondary"
            :to="`/monitors/${monitor.id}/edit`"
          >
            Edit
          </RouterLink>

          <button
            v-if="canManageMonitor"
            class="button-primary"
            type="button"
            :disabled="isRunningCheck"
            @click="runCheck"
          >
            {{ isRunningCheck ? 'Running...' : 'Run check' }}
          </button>
        </div>
      </div>

      <div class="monitor-summary">
        <div class="summary-card">
          <span class="summary-card__label"> Type </span>

          <strong>
            {{ monitor.monitor_type.toUpperCase() }}
          </strong>
        </div>

        <div class="summary-card">
          <span class="summary-card__label"> Interval </span>

          <strong> {{ monitor.interval_seconds }}s </strong>
        </div>

        <div class="summary-card">
          <span class="summary-card__label"> Timeout </span>

          <strong> {{ monitor.timeout_seconds }}s </strong>
        </div>

        <div class="summary-card">
          <span class="summary-card__label"> Next check </span>

          <strong>
            {{ new Date(monitor.next_check_at).toLocaleString() }}
          </strong>
        </div>
      </div>

      <div class="monitor-details__grid">
        <div class="details-card">
          <h2>Check settings</h2>

          <dl>
            <div>
              <dt>Failure threshold</dt>
              <dd>{{ monitor.failure_threshold }}</dd>
            </div>

            <div>
              <dt>Recovery threshold</dt>
              <dd>{{ monitor.recovery_threshold }}</dd>
            </div>

            <div>
              <dt>Consecutive failures</dt>
              <dd>{{ monitor.consecutive_failures }}</dd>
            </div>

            <div>
              <dt>Consecutive successes</dt>
              <dd>{{ monitor.consecutive_successes }}</dd>
            </div>

            <div>
              <dt>Created</dt>
              <dd>
                {{ new Date(monitor.created_at).toLocaleString() }}
              </dd>
            </div>
          </dl>
        </div>

        <div class="details-card">
          <h2>Configuration</h2>

          <dl v-if="monitor.monitor_type === 'http'">
            <div>
              <dt>URL</dt>
              <dd>{{ monitor.config.url }}</dd>
            </div>

            <div>
              <dt>Method</dt>
              <dd>{{ monitor.config.method }}</dd>
            </div>

            <div>
              <dt>Expected status codes</dt>
              <dd>
                {{ monitor.config.expected_status_codes?.join(', ') ?? 'Default' }}
              </dd>
            </div>

            <div>
              <dt>Body contains</dt>
              <dd>{{ monitor.config.body_contains ?? '—' }}</dd>
            </div>

            <div>
              <dt>Follow redirects</dt>
              <dd>
                {{ monitor.config.follow_redirects ? 'Yes' : 'No' }}
              </dd>
            </div>

            <div>
              <dt>Verify TLS</dt>
              <dd>
                {{ monitor.config.verify_tls ? 'Yes' : 'No' }}
              </dd>
            </div>
          </dl>

          <dl v-else-if="monitor.monitor_type === 'tcp'">
            <div>
              <dt>Host</dt>
              <dd>{{ monitor.config.host }}</dd>
            </div>

            <div>
              <dt>Port</dt>
              <dd>{{ monitor.config.port }}</dd>
            </div>
          </dl>

          <dl v-else-if="monitor.monitor_type === 'dns'">
            <div>
              <dt>Host</dt>
              <dd>{{ monitor.config.host }}</dd>
            </div>

            <div>
              <dt>Record type</dt>
              <dd>{{ monitor.config.record_type }}</dd>
            </div>
          </dl>

          <dl v-else-if="monitor.monitor_type === 'tls'">
            <div>
              <dt>Host</dt>
              <dd>{{ monitor.config.host }}</dd>
            </div>

            <div>
              <dt>Port</dt>
              <dd>{{ monitor.config.port }}</dd>
            </div>

            <div>
              <dt>Expiry threshold</dt>
              <dd>{{ monitor.config.expiry_threshold_days }} days</dd>
            </div>
          </dl>

          <dl v-else-if="monitor.monitor_type === 'icmp'">
            <div>
              <dt>Host</dt>
              <dd>{{ monitor.config.host }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div v-if="checkError" class="message-error">
        {{ checkError }}
      </div>

      <div
        v-if="lastManualCheck"
        class="check-result"
        :class="{
          'check-result--success': lastManualCheck.success,
          'check-result--failure': !lastManualCheck.success,
        }"
      >
        <div class="check-result__header">
          <h2>Manual check result</h2>

          <strong>
            {{ lastManualCheck.success ? 'Successful' : 'Failed' }}
          </strong>
        </div>

        <dl>
          <div>
            <dt>Response time</dt>
            <dd>{{ lastManualCheck.response_time_ms.toFixed(2) }} ms</dd>
          </div>

          <div>
            <dt>Status code</dt>
            <dd>
              {{ lastManualCheck.status_code ?? '—' }}
            </dd>
          </div>

          <div>
            <dt>Checked at</dt>
            <dd>
              {{ new Date(lastManualCheck.checked_at).toLocaleString() }}
            </dd>
          </div>

          <div v-if="lastManualCheck.error">
            <dt>Error</dt>
            <dd>{{ lastManualCheck.error }}</dd>
          </div>
        </dl>
      </div>

      <div class="statistics">
        <div class="statistics__header">
          <div>
            <h2>Statistics</h2>

            <p>Monitor performance for the selected period.</p>
          </div>

          <div class="statistics__periods">
            <button
              type="button"
              class="period-button"
              :class="{
                'period-button--active': statisticsPeriod === '24h',
              }"
              @click="statisticsPeriod = '24h'"
            >
              24 hours
            </button>

            <button
              type="button"
              class="period-button"
              :class="{
                'period-button--active': statisticsPeriod === '7d',
              }"
              @click="statisticsPeriod = '7d'"
            >
              7 days
            </button>

            <button
              type="button"
              class="period-button"
              :class="{
                'period-button--active': statisticsPeriod === '30d',
              }"
              @click="statisticsPeriod = '30d'"
            >
              30 days
            </button>
          </div>
        </div>

        <p v-if="statisticsLoading && !statistics" class="statistics__message">
          Loading statistics...
        </p>

        <div v-else-if="statisticsError" class="message-error">
          {{ statisticsError }}
        </div>

        <div v-else-if="statistics" class="statistics__cards">
          <div class="statistics-card">
            <span>Uptime</span>

            <strong>
              {{
                statistics.uptime_percentage !== null
                  ? `${statistics.uptime_percentage.toFixed(2)}%`
                  : '—'
              }}
            </strong>
          </div>

          <div class="statistics-card">
            <span>Total checks</span>

            <strong>
              {{ statistics.total_checks }}
            </strong>
          </div>

          <div class="statistics-card">
            <span>Successful</span>

            <strong>
              {{ statistics.successful_checks }}
            </strong>
          </div>

          <div class="statistics-card">
            <span>Failed</span>

            <strong>
              {{ statistics.failed_checks }}
            </strong>
          </div>

          <div class="statistics-card">
            <span>Average response</span>

            <strong>
              {{
                statistics.average_response_time_ms !== null
                  ? `${statistics.average_response_time_ms.toFixed(2)} ms`
                  : '—'
              }}
            </strong>
          </div>
        </div>
      </div>

      <div class="check-history">
        <div class="check-history__header">
          <div>
            <h2>Check history</h2>

            <p>Latest monitor checks.</p>
          </div>

          <button
            class="button-secondary"
            type="button"
            :disabled="checksLoading"
            @click="loadChecks"
          >
            {{ checksLoading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <p v-if="checksLoading && checks.length === 0" class="check-history__message">
          Loading check history...
        </p>

        <div v-else-if="checksError" class="message-error">
          {{ checksError }}
        </div>

        <div v-else-if="checks.length === 0" class="check-history__empty">
          No checks have been recorded yet.
        </div>

        <div v-else class="check-history__table-wrapper">
          <table class="check-history__table">
            <thead>
              <tr>
                <th>Checked at</th>
                <th>Result</th>
                <th>Response time</th>
                <th>Status code</th>
                <th>Error</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="check in checks" :key="check.id">
                <td>
                  {{ new Date(check.checked_at).toLocaleString() }}
                </td>

                <td>
                  <span
                    class="check-status"
                    :class="{
                      'check-status--success': check.success,
                      'check-status--failure': !check.success,
                    }"
                  >
                    {{ check.success ? 'Success' : 'Failed' }}
                  </span>
                </td>

                <td>{{ check.response_time_ms.toFixed(2) }} ms</td>

                <td>
                  {{ check.status_code ?? '—' }}
                </td>

                <td class="check-history__error-cell">
                  {{ check.error ?? '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.monitor-details__top {
  margin-bottom: 20px;
}

.monitor-details__back {
  color: #2563eb;
  font-size: 14px;
  text-decoration: none;
}

.monitor-details__back:hover {
  text-decoration: underline;
}

.monitor-details__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 24px;
}

.monitor-details__title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.monitor-details__title h1 {
  margin: 0;

  color: #0f172a;
  font-size: 28px;
}

.monitor-details__target {
  margin: 8px 0 0;

  color: #64748b;
}

.monitor-details__actions {
  display: flex;
  gap: 12px;
}

.monitor-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;

  margin-bottom: 24px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 8px;

  padding: 20px;

  border: 1px solid #e2e8f0;
  border-radius: 8px;

  background: #ffffff;
}

.summary-card__label {
  color: #64748b;
  font-size: 13px;
}

.summary-card strong {
  color: #0f172a;
}

.monitor-details__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;

  margin-bottom: 24px;
}

.details-card {
  padding: 24px;

  border: 1px solid #e2e8f0;
  border-radius: 8px;

  background: #ffffff;
}

.details-card h2,
.check-result h2 {
  margin: 0 0 20px;

  color: #0f172a;
  font-size: 18px;
}

.details-card dl,
.check-result dl {
  margin: 0;
}

.details-card dl > div,
.check-result dl > div {
  display: flex;
  justify-content: space-between;
  gap: 24px;

  padding: 10px 0;

  border-bottom: 1px solid #f1f5f9;
}

.details-card dl > div:last-child,
.check-result dl > div:last-child {
  border-bottom: 0;
}

.details-card dt,
.check-result dt {
  color: #64748b;
}

.details-card dd,
.check-result dd {
  margin: 0;

  color: #0f172a;
  text-align: right;
  word-break: break-word;
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

.check-result {
  margin-top: 24px;
  padding: 24px;

  border: 1px solid;
  border-radius: 8px;

  background: #ffffff;
}

.check-result--success {
  border-color: #bbf7d0;
}

.check-result--failure {
  border-color: #fecaca;
}

.check-result__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.check-result--success .check-result__header strong {
  color: #166534;
}

.check-result--failure .check-result__header strong {
  color: #991b1b;
}

.message-error {
  padding: 16px;

  border: 1px solid #fecaca;
  border-radius: 8px;

  color: #991b1b;
  background: #fef2f2;
}

.button-primary,
.button-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;

  padding: 10px 16px;

  border-radius: 6px;

  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}

.button-primary {
  border: 0;

  color: #ffffff;
  background: #2563eb;

  cursor: pointer;
}

.button-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.button-primary:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.button-secondary {
  border: 1px solid #cbd5e1;

  color: #334155;
  background: #ffffff;
}

.button-secondary:hover {
  background: #f8fafc;
}

@media (max-width: 900px) {
  .monitor-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .monitor-details__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .monitor-details__header {
    flex-direction: column;
  }

  .monitor-summary {
    grid-template-columns: 1fr;
  }

  .monitor-details__actions {
    width: 100%;
  }
}

.check-history {
  margin-top: 24px;
  padding: 24px;

  border: 1px solid #e2e8f0;
  border-radius: 8px;

  background: #ffffff;
}

.check-history__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 20px;
}

.check-history__header h2 {
  margin: 0 0 6px;

  color: #0f172a;
  font-size: 18px;
}

.check-history__header p {
  margin: 0;

  color: #64748b;
  font-size: 14px;
}

.check-history__message,
.check-history__empty {
  margin: 0;

  color: #64748b;
}

.check-history__table-wrapper {
  overflow-x: auto;
}

.check-history__table {
  width: 100%;

  border-collapse: collapse;
}

.check-history__table th,
.check-history__table td {
  padding: 12px 14px;

  border-bottom: 1px solid #e2e8f0;

  text-align: left;
  vertical-align: top;
}

.check-history__table th {
  color: #64748b;
  background: #f8fafc;

  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.check-history__table tbody tr:last-child td {
  border-bottom: 0;
}

.check-status {
  display: inline-block;

  padding: 4px 8px;

  border-radius: 999px;

  font-size: 12px;
  font-weight: 600;
}

.check-status--success {
  color: #166534;
  background: #dcfce7;
}

.check-status--failure {
  color: #991b1b;
  background: #fee2e2;
}

.check-history__error-cell {
  max-width: 320px;

  color: #991b1b;

  white-space: normal;
  word-break: break-word;
}

.statistics {
  margin-top: 24px;
  padding: 24px;

  border: 1px solid #e2e8f0;
  border-radius: 8px;

  background: #ffffff;
}

.statistics__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 20px;
}

.statistics__header h2 {
  margin: 0 0 6px;

  color: #0f172a;
  font-size: 18px;
}

.statistics__header p {
  margin: 0;

  color: #64748b;
  font-size: 14px;
}

.statistics__periods {
  display: flex;
  gap: 4px;

  padding: 4px;

  border-radius: 8px;

  background: #f1f5f9;
}

.period-button {
  padding: 7px 12px;

  border: 0;
  border-radius: 6px;

  color: #64748b;
  background: transparent;

  font-size: 13px;
  font-weight: 500;

  cursor: pointer;
}

.period-button:hover {
  color: #0f172a;
}

.period-button--active {
  color: #0f172a;
  background: #ffffff;
}

.statistics__message {
  margin: 0;

  color: #64748b;
}

.statistics__cards {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.statistics-card {
  display: flex;
  flex-direction: column;
  gap: 8px;

  padding: 16px;

  border: 1px solid #e2e8f0;
  border-radius: 8px;

  background: #f8fafc;
}

.statistics-card span {
  color: #64748b;
  font-size: 12px;
}

.statistics-card strong {
  color: #0f172a;
  font-size: 20px;
}
</style>
