<script setup lang="ts">
import { onMounted, ref } from 'vue'

import apiClient from '@/api/client'

const apiStatus = ref<string>('Checking...')

onMounted(async () => {
  try {
    const response = await apiClient.get<{ status: string }>('/health')

    apiStatus.value = response.data.status
  } catch {
    apiStatus.value = 'Unavailable'
  }
})
</script>

<template>
  <section>
    <h1>Dashboard</h1>

    <p>Uptime Platform dashboard</p>

    <p>
      API status:
      <strong>{{ apiStatus }}</strong>
    </p>
  </section>
</template>
