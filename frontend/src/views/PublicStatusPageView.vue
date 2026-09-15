<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { useStatusPageStore } from '@/stores/status-pages'
import type { PublicStatusPage, StatusPageStatus } from '@/types/status-page'

const route = useRoute()
const statusPageStore = useStatusPageStore()

const page = ref<PublicStatusPage | null>(null)
const loading = ref(true)
const loadError = ref<string | null>(null)

const overallLabel = computed(() => {
  if (!page.value) {
    return ''
  }

  const labels: Record<StatusPageStatus, string> = {
    operational: 'All systems operational',
    partial_outage: 'Partial outage',
    major_outage: 'Major outage',
    unknown: 'Status unknown',
  }

  return labels[page.value.status]
})

function getSlug(): string | null {
  const slug = route.params.slug

  return typeof slug === 'string' ? slug : null
}

async function loadPage(): Promise<void> {
  const slug = getSlug()

  if (!slug) {
    loadError.value = 'Invalid status page'
    loading.value = false
    return
  }

  loading.value = true
  loadError.value = null

  try {
    page.value = await statusPageStore.getPublicPage(slug)
  } catch {
    page.value = null
    loadError.value = 'Status page not found or is not published'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadPage()
})

watch(
  () => route.params.slug,
  async () => {
    await loadPage()
  },
)
</script>

<template>
  <main class="public-status">
    <div class="public-status__container">
      <p v-if="loading" class="text-muted">Loading status...</p>

      <div v-else-if="loadError" class="public-status__error">
        <h1>Status page unavailable</h1>
        <p>{{ loadError }}</p>
      </div>

      <template v-else-if="page">
        <header class="public-status__header">
          <h1>{{ page.name }}</h1>
        </header>

        <div class="public-status__overall" :class="`public-status__overall--${page.status}`">
          {{ overallLabel }}
        </div>

        <div v-if="page.monitors.length === 0" class="public-status__empty">
          No services have been added.
        </div>

        <div v-else class="public-status__services">
          <div v-for="monitor in page.monitors" :key="monitor.id" class="public-status-service">
            <strong>{{ monitor.name }}</strong>

            <span class="monitor-status" :class="`monitor-status--${monitor.status}`">
              {{ monitor.status }}
            </span>
          </div>
        </div>
      </template>
    </div>
  </main>
</template>

<style lang="scss">
@use '@/assets/scss/pages/status-pages';
</style>
