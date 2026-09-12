<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const organizationName = ref('')
const email = ref('')
const password = ref('')
const passwordConfirmation = ref('')

const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

async function submitRegistration(): Promise<void> {
  errorMessage.value = null

  if (password.value !== passwordConfirmation.value) {
    errorMessage.value = 'Passwords do not match'
    return
  }

  isSubmitting.value = true

  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      organization_name: organizationName.value,
    })

    await router.push('/login')
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        errorMessage.value = detail
      } else {
        errorMessage.value = 'Unable to create account'
      }
    } else {
      errorMessage.value = 'Unable to create account'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="register-page">
    <div class="register-card">
      <div class="register-card__header">
        <h1>Create account</h1>

        <p>Create your Uptime Platform account</p>
      </div>

      <form
        class="register-form"
        @submit.prevent="submitRegistration"
      >
        <div class="form-field">
          <label for="organization-name">
            Organization name
          </label>

          <input
            id="organization-name"
            v-model.trim="organizationName"
            type="text"
            autocomplete="organization"
            maxlength="100"
            required
          >
        </div>

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
            autocomplete="new-password"
            minlength="8"
            maxlength="128"
            required
          >
        </div>

        <div class="form-field">
          <label for="password-confirmation">
            Confirm password
          </label>

          <input
            id="password-confirmation"
            v-model="passwordConfirmation"
            type="password"
            autocomplete="new-password"
            minlength="8"
            maxlength="128"
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
          {{ isSubmitting ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <p class="register-card__footer">
        Already have an account?

        <RouterLink to="/login">
          Sign in
        </RouterLink>
      </p>
    </div>
  </main>
</template>

<style scoped>
.register-page {
  display: flex;
  align-items: center;
  justify-content: center;

  min-height: 100vh;
  padding: 24px;
}

.register-card {
  width: 100%;
  max-width: 420px;
  padding: 32px;

  border: 1px solid #e2e8f0;
  border-radius: 12px;

  background: #ffffff;
}

.register-card__header {
  margin-bottom: 24px;
}

.register-card__header h1 {
  margin: 0 0 8px;

  color: #0f172a;
  font-size: 24px;
}

.register-card__header p {
  margin: 0;

  color: #64748b;
}

.register-form {
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

.register-form button {
  padding: 10px 16px;

  border: 0;
  border-radius: 6px;

  color: #ffffff;
  background: #2563eb;

  font-weight: 600;
  cursor: pointer;
}

.register-form button:hover:not(:disabled) {
  background: #1d4ed8;
}

.register-form button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.form-error {
  margin: 0;

  color: #dc2626;
  font-size: 14px;
}

.register-card__footer {
  margin: 24px 0 0;

  color: #64748b;
  font-size: 14px;
  text-align: center;
}

.register-card__footer a {
  color: #2563eb;
  text-decoration: none;
}

.register-card__footer a:hover {
  text-decoration: underline;
}
</style>
