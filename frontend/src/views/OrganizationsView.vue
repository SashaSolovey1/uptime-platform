<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'

import { useOrganizationStore } from '@/stores/organizations'

const organizationStore = useOrganizationStore()

const name = ref('')
const isCreating = ref(false)
const createError = ref<string | null>(null)

function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) {
    return fallback
  }

  const detail = error.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  return fallback
}

async function handleCreate(): Promise<void> {
  createError.value = null

  const trimmedName = name.value.trim()

  if (!trimmedName) {
    createError.value = 'Organization name is required'
    return
  }

  isCreating.value = true

  try {
    await organizationStore.createOrganization({
      name: trimmedName,
    })

    name.value = ''
  } catch (error) {
    createError.value = getApiErrorMessage(error, 'Unable to create organization')
  } finally {
    isCreating.value = false
  }
}

function handleSelectOrganization(organizationId: string): void {
  organizationStore.selectOrganization(organizationId)
}
</script>

<template>
  <section class="organizations-page">
    <div class="organizations-page__header">
      <div>
        <h1>Organizations</h1>

        <p>Create organizations and switch between your workspaces.</p>
      </div>
    </div>

    <div class="section-card">
      <div class="section-header">
        <div>
          <h2>Create organization</h2>

          <p>Create a separate workspace for monitors, incidents and integrations.</p>
        </div>
      </div>

      <form class="organization-form" @submit.prevent="handleCreate">
        <div class="form-field">
          <label for="organization-name"> Name </label>

          <input
            id="organization-name"
            v-model="name"
            maxlength="100"
            placeholder="Production"
            required
          />
        </div>

        <p v-if="createError" class="form-error">
          {{ createError }}
        </p>

        <div class="organization-form__actions">
          <button class="button-primary" type="submit" :disabled="isCreating">
            {{ isCreating ? 'Creating...' : 'Create organization' }}
          </button>
        </div>
      </form>
    </div>

    <div class="section-card">
      <div class="section-header">
        <div>
          <h2>Your organizations</h2>

          <p>Select the organization you want to work in.</p>
        </div>
      </div>

      <p v-if="organizationStore.organizations.length === 0" class="text-muted">
        No organizations found.
      </p>

      <div v-else class="organization-list">
        <div
          v-for="organization in organizationStore.organizations"
          :key="organization.id"
          class="organization-card"
          :class="{
            'organization-card--current':
              organization.id === organizationStore.currentOrganizationId,
          }"
        >
          <div class="organization-card__info">
            <div class="organization-card__title">
              <strong>{{ organization.name }}</strong>

              <span
                v-if="organization.id === organizationStore.currentOrganizationId"
                class="organization-card__current"
              >
                Current
              </span>
            </div>

            <div class="organization-card__meta">
              <span>
                Role:
                <strong>{{ organization.role }}</strong>
              </span>

              <span>
                Created:
                {{ new Date(organization.created_at).toLocaleDateString() }}
              </span>
            </div>
          </div>

          <button
            v-if="organization.id !== organizationStore.currentOrganizationId"
            class="button-secondary"
            type="button"
            @click="handleSelectOrganization(organization.id)"
          >
            Switch
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
@use '@/assets/scss/pages/organizations';
</style>
