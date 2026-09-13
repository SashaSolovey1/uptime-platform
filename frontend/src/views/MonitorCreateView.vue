<script setup lang="ts">
import axios from 'axios'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { useMonitorStore } from '@/stores/monitors'
import { useOrganizationStore } from '@/stores/organizations'
import type {
  DnsRecordType,
  HttpMethod,
  MonitorCreate,
  MonitorType,
} from '@/types/monitor'

const router = useRouter()

const monitorStore = useMonitorStore()
const organizationStore = useOrganizationStore()

const name = ref('')
const monitorType = ref<MonitorType>('http')

const intervalSeconds = ref(60)
const timeoutSeconds = ref(5)
const failureThreshold = ref(3)
const recoveryThreshold = ref(2)

const httpUrl = ref('')
const httpMethod = ref<HttpMethod>('GET')
const expectedStatusCodes = ref('')
const bodyContains = ref('')
const followRedirects = ref(false)
const verifyTls = ref(true)

const tcpHost = ref('')
const tcpPort = ref(80)

const dnsHost = ref('')
const dnsRecordType = ref<DnsRecordType>('A')

const tlsHost = ref('')
const tlsPort = ref(443)
const tlsExpiryThresholdDays = ref(14)

const icmpHost = ref('')

const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

const canCreateMonitor = computed(() => {
  const role = organizationStore.currentOrganization?.role

  return (
    role === 'owner'
    || role === 'admin'
    || role === 'member'
  )
})

watch(httpMethod, (method) => {
  if (method === 'HEAD') {
    bodyContains.value = ''
  }
})

function parseExpectedStatusCodes(): number[] | null {
  const value = expectedStatusCodes.value.trim()

  if (!value) {
    return null
  }

  const statusCodes = value
    .split(',')
    .map((statusCode) => {
      return Number(statusCode.trim())
    })

  const hasInvalidStatusCode = statusCodes.some((statusCode) => {
    return (
      !Number.isInteger(statusCode)
      || statusCode < 100
      || statusCode > 599
    )
  })

  if (hasInvalidStatusCode) {
    throw new Error(
      'Expected status codes must be numbers between 100 and 599',
    )
  }

  return statusCodes
}

function buildMonitorCreate(): MonitorCreate {
  const base = {
    name: name.value.trim(),
    interval_seconds: intervalSeconds.value,
    timeout_seconds: timeoutSeconds.value,
    failure_threshold: failureThreshold.value,
    recovery_threshold: recoveryThreshold.value,
  }

  switch (monitorType.value) {
    case 'http':
      return {
        ...base,
        monitor_type: 'http',
        config: {
          url: httpUrl.value.trim(),
          method: httpMethod.value,
          expected_status_codes: parseExpectedStatusCodes(),
          body_contains:
            httpMethod.value === 'HEAD'
              ? null
              : bodyContains.value.trim() || null,
          follow_redirects: followRedirects.value,
          verify_tls: verifyTls.value,
        },
      }

    case 'tcp':
      return {
        ...base,
        monitor_type: 'tcp',
        config: {
          host: tcpHost.value.trim(),
          port: tcpPort.value,
        },
      }

    case 'dns':
      return {
        ...base,
        monitor_type: 'dns',
        config: {
          host: dnsHost.value.trim(),
          record_type: dnsRecordType.value,
        },
      }

    case 'tls':
      return {
        ...base,
        monitor_type: 'tls',
        config: {
          host: tlsHost.value.trim(),
          port: tlsPort.value,
          expiry_threshold_days: tlsExpiryThresholdDays.value,
        },
      }

    case 'icmp':
      return {
        ...base,
        monitor_type: 'icmp',
        config: {
          host: icmpHost.value.trim(),
        },
      }
  }
}

async function submitMonitor(): Promise<void> {
  errorMessage.value = null
  isSubmitting.value = true

  try {
    const data = buildMonitorCreate()

    await monitorStore.createMonitor(data)

    await router.push('/monitors')
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        errorMessage.value = detail
      } else if (
        Array.isArray(detail)
        && typeof detail[0]?.msg === 'string'
      ) {
        errorMessage.value = detail[0].msg
      } else {
        errorMessage.value = 'Unable to create monitor'
      }
    } else if (error instanceof Error) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'Unable to create monitor'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="monitor-create">
    <div class="monitor-create__header">
      <div>
        <h1>Create monitor</h1>

        <p>
          Configure a new monitor for the selected organization.
        </p>
      </div>

      <RouterLink
        class="monitor-create__back"
        to="/monitors"
      >
        Back to monitors
      </RouterLink>
    </div>

    <div
      v-if="!canCreateMonitor"
      class="monitor-create__forbidden"
    >
      Your organization role does not allow creating monitors.
    </div>

    <form
      v-else
      class="monitor-form"
      @submit.prevent="submitMonitor"
    >
      <div class="form-section">
        <h2>General</h2>

        <div class="form-field">
          <label for="name">
            Name
          </label>

          <input
            id="name"
            v-model.trim="name"
            type="text"
            maxlength="100"
            required
          >
        </div>

        <div class="form-field">
          <label for="monitor-type">
            Monitor type
          </label>

          <select
            id="monitor-type"
            v-model="monitorType"
          >
            <option value="http">
              HTTP
            </option>

            <option value="tcp">
              TCP
            </option>

            <option value="dns">
              DNS
            </option>

            <option value="tls">
              TLS
            </option>

            <option value="icmp">
              ICMP
            </option>
          </select>
        </div>
      </div>

      <div class="form-section">
        <h2>Target</h2>

        <template v-if="monitorType === 'http'">
          <div class="form-field">
            <label for="http-url">
              URL
            </label>

            <input
              id="http-url"
              v-model.trim="httpUrl"
              type="url"
              placeholder="https://example.com/health"
              required
            >
          </div>

          <div class="form-field">
            <label for="http-method">
              Method
            </label>

            <select
              id="http-method"
              v-model="httpMethod"
            >
              <option value="GET">
                GET
              </option>

              <option value="HEAD">
                HEAD
              </option>
            </select>
          </div>

          <div class="form-field">
            <label for="expected-status-codes">
              Expected status codes
            </label>

            <input
              id="expected-status-codes"
              v-model.trim="expectedStatusCodes"
              type="text"
              placeholder="200, 204"
            >

            <small>
              Leave empty to use the backend default behavior.
            </small>
          </div>

          <div
            v-if="httpMethod !== 'HEAD'"
            class="form-field"
          >
            <label for="body-contains">
              Response body contains
            </label>

            <input
              id="body-contains"
              v-model="bodyContains"
              type="text"
              maxlength="4096"
              placeholder="Optional text"
            >
          </div>

          <label class="form-checkbox">
            <input
              v-model="followRedirects"
              type="checkbox"
            >

            Follow redirects
          </label>

          <label class="form-checkbox">
            <input
              v-model="verifyTls"
              type="checkbox"
            >

            Verify TLS certificate
          </label>
        </template>

        <template v-else-if="monitorType === 'tcp'">
          <div class="form-grid">
            <div class="form-field">
              <label for="tcp-host">
                Host
              </label>

              <input
                id="tcp-host"
                v-model.trim="tcpHost"
                type="text"
                maxlength="255"
                placeholder="example.com"
                required
              >
            </div>

            <div class="form-field">
              <label for="tcp-port">
                Port
              </label>

              <input
                id="tcp-port"
                v-model.number="tcpPort"
                type="number"
                min="1"
                max="65535"
                required
              >
            </div>
          </div>
        </template>

        <template v-else-if="monitorType === 'dns'">
          <div class="form-grid">
            <div class="form-field">
              <label for="dns-host">
                Host
              </label>

              <input
                id="dns-host"
                v-model.trim="dnsHost"
                type="text"
                maxlength="253"
                placeholder="example.com"
                required
              >
            </div>

            <div class="form-field">
              <label for="dns-record-type">
                Record type
              </label>

              <select
                id="dns-record-type"
                v-model="dnsRecordType"
              >
                <option value="A">
                  A
                </option>

                <option value="AAAA">
                  AAAA
                </option>

                <option value="CNAME">
                  CNAME
                </option>

                <option value="MX">
                  MX
                </option>

                <option value="TXT">
                  TXT
                </option>
              </select>
            </div>
          </div>
        </template>

        <template v-else-if="monitorType === 'tls'">
          <div class="form-grid">
            <div class="form-field">
              <label for="tls-host">
                Host
              </label>

              <input
                id="tls-host"
                v-model.trim="tlsHost"
                type="text"
                maxlength="253"
                placeholder="example.com"
                required
              >
            </div>

            <div class="form-field">
              <label for="tls-port">
                Port
              </label>

              <input
                id="tls-port"
                v-model.number="tlsPort"
                type="number"
                min="1"
                max="65535"
                required
              >
            </div>
          </div>

          <div class="form-field">
            <label for="tls-expiry-threshold">
              Expiry threshold
            </label>

            <input
              id="tls-expiry-threshold"
              v-model.number="tlsExpiryThresholdDays"
              type="number"
              min="0"
              max="365"
              required
            >

            <small>
              Days before certificate expiration.
            </small>
          </div>
        </template>

        <template v-else-if="monitorType === 'icmp'">
          <div class="form-field">
            <label for="icmp-host">
              Host
            </label>

            <input
              id="icmp-host"
              v-model.trim="icmpHost"
              type="text"
              maxlength="253"
              placeholder="example.com"
              required
            >
          </div>
        </template>
      </div>

      <div class="form-section">
        <h2>Check settings</h2>

        <div class="form-grid">
          <div class="form-field">
            <label for="interval">
              Interval
            </label>

            <input
              id="interval"
              v-model.number="intervalSeconds"
              type="number"
              min="10"
              max="3600"
              required
            >

            <small>Seconds between checks.</small>
          </div>

          <div class="form-field">
            <label for="timeout">
              Timeout
            </label>

            <input
              id="timeout"
              v-model.number="timeoutSeconds"
              type="number"
              min="1"
              max="60"
              required
            >

            <small>Maximum check duration in seconds.</small>
          </div>

          <div class="form-field">
            <label for="failure-threshold">
              Failure threshold
            </label>

            <input
              id="failure-threshold"
              v-model.number="failureThreshold"
              type="number"
              min="1"
              max="10"
              required
            >

            <small>
              Consecutive failures before marking the monitor down.
            </small>
          </div>

          <div class="form-field">
            <label for="recovery-threshold">
              Recovery threshold
            </label>

            <input
              id="recovery-threshold"
              v-model.number="recoveryThreshold"
              type="number"
              min="1"
              max="10"
              required
            >

            <small>
              Consecutive successful checks before recovery.
            </small>
          </div>
        </div>
      </div>

      <p
        v-if="errorMessage"
        class="form-error"
        role="alert"
      >
        {{ errorMessage }}
      </p>

      <div class="monitor-form__actions">
        <RouterLink
          class="button-secondary"
          to="/monitors"
        >
          Cancel
        </RouterLink>

        <button
          class="button-primary"
          type="submit"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? 'Creating...' : 'Create monitor' }}
        </button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.monitor-create {
  max-width: 860px;
}

.monitor-create__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 24px;
}

.monitor-create__header h1 {
  margin: 0 0 8px;

  color: #0f172a;
  font-size: 28px;
}

.monitor-create__header p {
  margin: 0;

  color: #64748b;
}

.monitor-create__back {
  color: #2563eb;
  font-size: 14px;
  text-decoration: none;
}

.monitor-create__back:hover {
  text-decoration: underline;
}

.monitor-create__forbidden {
  padding: 20px;

  border: 1px solid #fde68a;
  border-radius: 8px;

  color: #854d0e;
  background: #fffbeb;
}

.monitor-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  padding: 24px;

  border: 1px solid #e2e8f0;
  border-radius: 8px;

  background: #ffffff;
}

.form-section h2 {
  margin: 0 0 20px;

  color: #0f172a;
  font-size: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;

  margin-bottom: 20px;
}

.form-field:last-child {
  margin-bottom: 0;
}

.form-field label {
  color: #334155;
  font-size: 14px;
  font-weight: 500;
}

.form-field input,
.form-field select {
  width: 100%;
  padding: 10px 12px;

  border: 1px solid #cbd5e1;
  border-radius: 6px;

  color: #0f172a;
  background: #ffffff;

  outline: none;
}

.form-field input:focus,
.form-field select:focus {
  border-color: #2563eb;
}

.form-field small {
  color: #64748b;
  font-size: 12px;
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;

  margin-top: 12px;

  color: #334155;
  font-size: 14px;
}

.form-checkbox input {
  width: auto;
}

.form-error {
  margin: 0;
  padding: 12px 16px;

  border: 1px solid #fecaca;
  border-radius: 6px;

  color: #991b1b;
  background: #fef2f2;
}

.monitor-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

@media (max-width: 700px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .monitor-create__header {
    flex-direction: column;
  }
}
</style>
