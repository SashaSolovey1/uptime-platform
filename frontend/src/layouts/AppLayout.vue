<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<template>
  <div class="app-layout">
    <AppHeader />

    <main class="app-layout__content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.app-layout__content {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px;
}
</style>
