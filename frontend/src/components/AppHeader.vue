<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useOrganizationStore } from '@/stores/organizations'

const router = useRouter()

const authStore = useAuthStore()
const organizationStore = useOrganizationStore()

const isLoggingOut = ref(false)
const logoutError = ref<string | null>(null)

function handleOrganizationChange(event: Event): void {
  const select = event.target as HTMLSelectElement

  organizationStore.selectOrganization(select.value)
}

async function handleLogout(): Promise<void> {
  logoutError.value = null
  isLoggingOut.value = true

  try {
    await authStore.logout()

    organizationStore.clear()

    await router.push('/login')
  } catch {
    logoutError.value = 'Unable to sign out'
  } finally {
    isLoggingOut.value = false
  }
}
</script>

<template>
  <header class="app-header">
    <div class="app-header__content">
      <RouterLink class="app-header__logo" to="/dashboard"> Uptime Platform </RouterLink>

      <nav class="app-header__nav">
        <RouterLink class="app-header__link" to="/dashboard"> Dashboard </RouterLink>

        <RouterLink class="app-header__link" to="/monitors"> Monitors </RouterLink>

        <RouterLink class="app-header__link" to="/incidents"> Incidents </RouterLink>

        <RouterLink class="app-header__link" to="/maintenance"> Maintenance </RouterLink>

        <RouterLink class="app-header__link" to="/notifications"> Notifications </RouterLink>

        <RouterLink class="app-header__link" to="/status-pages"> Status Pages </RouterLink>
      </nav>

      <div class="app-header__user">
        <select
          v-if="organizationStore.organizations.length > 0"
          class="app-header__organization"
          :value="organizationStore.currentOrganizationId ?? ''"
          @change="handleOrganizationChange"
        >
          <option
            v-for="organization in organizationStore.organizations"
            :key="organization.id"
            :value="organization.id"
          >
            {{ organization.name }}
          </option>
        </select>

        <span v-if="organizationStore.currentOrganization" class="app-header__role">
          {{ organizationStore.currentOrganization.role }}
        </span>

        <span v-if="authStore.user" class="app-header__email">
          {{ authStore.user.email }}
        </span>

        <button
          class="app-header__logout"
          type="button"
          :disabled="isLoggingOut"
          @click="handleLogout"
        >
          {{ isLoggingOut ? 'Signing out...' : 'Sign out' }}
        </button>
      </div>
    </div>

    <p v-if="logoutError" class="app-header__error" role="alert">
      {{ logoutError }}
    </p>
  </header>
</template>

<style scoped>
.app-header {
  border-bottom: 1px solid #e2e8f0;
  background: #ffffff;
}

.app-header__content {
  display: flex;
  align-items: center;
  gap: 32px;

  width: 100%;
  max-width: 1280px;
  height: 64px;
  margin: 0 auto;
  padding: 0 24px;
}

.app-header__logo {
  color: #0f172a;
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
}

.app-header__nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-header__link {
  padding: 8px 12px;

  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;

  border-radius: 6px;
}

.app-header__link:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.app-header__link.router-link-active {
  color: #2563eb;
  background: #eff6ff;
}

.app-header__user {
  display: flex;
  align-items: center;
  gap: 12px;

  margin-left: auto;
}

.app-header__organization {
  min-width: 160px;
  padding: 7px 10px;

  border: 1px solid #cbd5e1;
  border-radius: 6px;

  color: #334155;
  background: #ffffff;

  font-size: 14px;
}

.app-header__role {
  padding: 4px 8px;

  border-radius: 999px;

  color: #475569;
  background: #f1f5f9;

  font-size: 12px;
}

.app-header__email {
  color: #64748b;
  font-size: 14px;
}

.app-header__logout {
  padding: 8px 12px;

  border: 1px solid #cbd5e1;
  border-radius: 6px;

  color: #334155;
  background: #ffffff;

  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.app-header__logout:hover:not(:disabled) {
  background: #f8fafc;
}

.app-header__logout:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.app-header__error {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px 8px;

  color: #dc2626;
  font-size: 13px;
  text-align: right;
}
</style>
