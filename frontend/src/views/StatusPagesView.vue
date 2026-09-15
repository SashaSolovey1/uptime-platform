<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { useOrganizationStore } from '@/stores/organizations'
import { useStatusPageStore } from '@/stores/status-pages'
import type { StatusPageCreate } from '@/types/status-page'

const statusPageStore = useStatusPageStore()
const organizationStore = useOrganizationStore()

const name = ref('')
const slug = ref('')
const published = ref(true)

const isCreating = ref(false)
const createError = ref<string | null>(null)

const canManageStatusPages = computed(() => {
  const role = organizationStore.currentOrganization?.role

  return role === 'owner' || role === 'admin'
})

function resetForm(): void {
  name.value = ''
  slug.value = ''
  published.value = true
  createError.value = null
}

function normalizeSlug(): void {
  slug.value = slug.value
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

async function handleCreate(): Promise<void> {
  createError.value = null

  const trimmedName = name.value.trim()

  if (!trimmedName) {
    createError.value = 'Name is required'
    return
  }

  normalizeSlug()

  if (!slug.value) {
    createError.value = 'Slug is required'
    return
  }

  const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/

  if (!slugPattern.test(slug.value)) {
    createError.value = 'Slug may contain lowercase letters, numbers and hyphens'
    return
  }

  const payload: StatusPageCreate = {
    name: trimmedName,
    slug: slug.value,
    published: published.value,
  }

  isCreating.value = true

  try {
    await statusPageStore.createPage(payload)
    resetForm()
  } catch {
    createError.value = 'Unable to create status page. The slug may already exist.'
  } finally {
    isCreating.value = false
  }
}

onMounted(async () => {
  await statusPageStore.loadPages()
})

watch(
  () => organizationStore.currentOrganizationId,
  async (currentOrganizationId, previousOrganizationId) => {
    if (previousOrganizationId && currentOrganizationId !== previousOrganizationId) {
      resetForm()
      await statusPageStore.loadPages()
    }
  },
)
</script>

<template>
  <section class="status-pages">
    <div class="status-pages__header">
      <div>
        <h1>Status Pages</h1>

        <p>Publish the current state of selected monitors.</p>
      </div>
    </div>

    <div v-if="canManageStatusPages" class="section-card">
      <div class="section-header">
        <div>
          <h2>Create status page</h2>
          <p>Create a public service status page.</p>
        </div>
      </div>

      <form class="status-page-form" @submit.prevent="handleCreate">
        <div class="form-grid">
          <div class="form-field">
            <label for="status-page-name"> Name </label>

            <input id="status-page-name" v-model="name" maxlength="100" required />
          </div>

          <div class="form-field">
            <label for="status-page-slug"> Slug </label>

            <input
              id="status-page-slug"
              v-model="slug"
              maxlength="100"
              placeholder="production-status"
              required
              @blur="normalizeSlug"
            />

            <small> Public URL: /status/{{ slug || 'your-slug' }} </small>
          </div>
        </div>

        <label class="form-checkbox">
          <input v-model="published" type="checkbox" />

          Published
        </label>

        <p v-if="createError" class="form-error">
          {{ createError }}
        </p>

        <div class="status-page-form__actions">
          <button class="button-primary" type="submit" :disabled="isCreating">
            {{ isCreating ? 'Creating...' : 'Create status page' }}
          </button>
        </div>
      </form>
    </div>

    <div v-if="statusPageStore.error" class="message-error">
      {{ statusPageStore.error }}
    </div>

    <p v-else-if="statusPageStore.loading" class="text-muted">Loading status pages...</p>

    <div v-else-if="statusPageStore.pages.length === 0" class="status-pages__empty">
      <h2>No status pages</h2>
      <p>Create your first public status page.</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Slug</th>
            <th>Published</th>
            <th>Public page</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="page in statusPageStore.pages" :key="page.id">
            <td>
              <strong>{{ page.name }}</strong>
            </td>

            <td>
              <code>{{ page.slug }}</code>
            </td>

            <td>
              <span
                class="publication-status"
                :class="{
                  'publication-status--published': page.published,
                  'publication-status--draft': !page.published,
                }"
              >
                {{ page.published ? 'Published' : 'Draft' }}
              </span>
            </td>

            <td>
              <RouterLink
                v-if="page.published"
                class="text-link"
                :to="`/status/${page.slug}`"
                target="_blank"
              >
                Open
              </RouterLink>

              <span v-else class="text-muted"> Not public </span>
            </td>

            <td>
              <RouterLink class="text-link" :to="`/status-pages/${page.id}`"> Manage </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style lang="scss">
@use '@/assets/scss/pages/status-pages';
</style>
