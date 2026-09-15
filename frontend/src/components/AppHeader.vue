<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useOrganizationStore } from '@/stores/organizations'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()
const organizationStore = useOrganizationStore()

const isLoggingOut = ref(false)
const logoutError = ref<string | null>(null)

const canManageApiKeys = computed(() => {
  const role = organizationStore.currentOrganization?.role

  return role === 'owner' || role === 'admin'
})

const isOperationsActive = computed(() => {
  return (
    route.path.startsWith('/maintenance') ||
    route.path.startsWith('/notifications') ||
    route.path.startsWith('/status-pages')
  )
})

const isSettingsActive = computed(() => {
  return (
    route.path.startsWith('/members') ||
    route.path.startsWith('/organizations') ||
    route.path.startsWith('/api-keys')
  )
})

function handleOrganizationChange(event: Event): void {
  const select = event.target as HTMLSelectElement

  organizationStore.selectOrganization(select.value)
}

function closeDropdown(event: Event): void {
  const element = event.currentTarget as HTMLElement

  const details = element.closest('details')

  details?.removeAttribute('open')
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

        <details class="app-header__dropdown">
          <summary
            class="app-header__dropdown-toggle"
            :class="{
              'app-header__dropdown-toggle--active': isOperationsActive,
            }"
          >
            Operations
          </summary>

          <div class="app-header__dropdown-menu">
            <RouterLink class="app-header__dropdown-link" to="/maintenance" @click="closeDropdown">
              Maintenance
            </RouterLink>

            <RouterLink
              class="app-header__dropdown-link"
              to="/notifications"
              @click="closeDropdown"
            >
              Notifications
            </RouterLink>

            <RouterLink class="app-header__dropdown-link" to="/status-pages" @click="closeDropdown">
              Status Pages
            </RouterLink>
          </div>
        </details>

        <details class="app-header__dropdown">
          <summary
            class="app-header__dropdown-toggle"
            :class="{
              'app-header__dropdown-toggle--active': isSettingsActive,
            }"
          >
            Settings
          </summary>

          <div class="app-header__dropdown-menu">
            <RouterLink class="app-header__dropdown-link" to="/members" @click="closeDropdown">
              Members
            </RouterLink>

            <RouterLink
              class="app-header__dropdown-link"
              to="/organizations"
              @click="closeDropdown"
            >
              Organizations
            </RouterLink>

            <RouterLink
              v-if="canManageApiKeys"
              class="app-header__dropdown-link"
              to="/api-keys"
              @click="closeDropdown"
            >
              API Keys
            </RouterLink>
          </div>
        </details>
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

<style lang="scss">
@use '@/assets/scss/components/app-header';
</style>
