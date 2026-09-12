<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()

const email = ref('')
const password = ref('')

const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

async function submitLogin(): Promise<void> {
  errorMessage.value = null
  isSubmitting.value = true

  try {
    await authStore.login({
      email: email.value,
      password: password.value,
    })

    const redirect = route.query.redirect

    if (typeof redirect === 'string') {
      await router.push(redirect)
    } else {
      await router.push('/dashboard')
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        errorMessage.value = detail
      } else {
        errorMessage.value = 'Unable to sign in'
      }
    } else {
      errorMessage.value = 'Unable to sign in'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <div class="login-card">
      <div class="login-card__header">
        <h1>Sign in</h1>
        <p>Sign in to Uptime Platform</p>
      </div>

      <form
        class="login-form"
        @submit.prevent="submitLogin"
      >
        <div class="form-field">
          <label for="email">
            Email
          </label>

          <input
            id="email"
            v-model.trim="email"
            type="email"
            autocomplete="email"
            required
          >
        </div>

        <div class="form-field">
          <label for="password">
            Password
          </label>

          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
          >
        </div>

        <p
          v-if="errorMessage"
          class="form-error"
          role="alert"
        >
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <p class="login-card__footer">
        Don't have an account?
        <RouterLink to="/register">
          Create one
        </RouterLink>
      </p>
    </div>
  </main>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;

  min-height: 100vh;
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 32px;

  border: 1px solid #e2e8f0;
  border-radius: 12px;

  background: #ffffff;
}

.login-card__header {
  margin-bottom: 24px;
}

.login-card__header h1 {
  margin: 0 0 8px;

  color: #0f172a;
  font-size: 24px;
}

.login-card__header p {
  margin: 0;

  color: #64748b;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-field label {
  color: #334155;
  font-size: 14px;
  font-weight: 500;
}

.form-field input {
  width: 100%;
  padding: 10px 12px;

  border: 1px solid #cbd5e1;
  border-radius: 6px;

  color: #0f172a;
  background: #ffffff;

  outline: none;
}

.form-field input:focus {
  border-color: #2563eb;
}

.login-form button {
  padding: 10px 16px;

  border: 0;
  border-radius: 6px;

  color: #ffffff;
  background: #2563eb;

  font-weight: 600;
  cursor: pointer;
}

.login-form button:hover:not(:disabled) {
  background: #1d4ed8;
}

.login-form button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.form-error {
  margin: 0;

  color: #dc2626;
  font-size: 14px;
}

.login-card__footer {
  margin: 24px 0 0;

  color: #64748b;
  font-size: 14px;
  text-align: center;
}

.login-card__footer a {
  color: #2563eb;
  text-decoration: none;
}

.login-card__footer a:hover {
  text-decoration: underline;
}
</style>
