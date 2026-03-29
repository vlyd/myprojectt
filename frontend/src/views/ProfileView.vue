<template>
  <div class="profile">
    <AppCard>
      <h1>Профиль пользователя</h1>

      <div v-if="!user" class="loading">
        Загрузка...
      </div>

      <div v-else>
        <div class="info-row">
          <span class="label">Имя:</span>
          <span class="value">{{ user.username }}</span>
        </div>

        <div class="info-row">
          <span class="label">Email:</span>
          <span class="value">{{ user.email }}</span>
        </div>

        <div class="token-section">
          <AppButton :disabled="loading" variant="primary" block @click="getToken">
            {{ loading ? 'Получение...' : 'Получить токен' }}
          </AppButton>

          <div v-if="token" class="token-result">
            <div class="token-value">
              <code>{{ token }}</code>
              <button class="copy-btn" @click="copyToken">📋</button>
            </div>
            <p class="token-info">Токен скопирован в буфер обмена</p>
          </div>

          <div v-if="error" class="message message-error">
            {{ error }}
          </div>
        </div>

        <AppButton variant="danger" block @click="logout">
          Выйти
        </AppButton>
      </div>
    </AppCard>
  </div>
</template>

<script>
import AppCard from '@/components/AppCard.vue'
import AppButton from '@/components/AppButton.vue'
import { useApi } from '@/composables/useApi'

export default {
  name: 'ProfileView',
  components: { AppCard, AppButton },
  setup() {
    const { loading, error, post } = useApi()
    return { loading, error, post }
  },
  data() {
    return {
      user: null,
      token: null
    }
  },
  mounted() {
    this.loadUser()
  },
  methods: {
    loadUser() {
      const userData = localStorage.getItem('userData') || sessionStorage.getItem('userData')
      if (userData) {
        this.user = JSON.parse(userData)
      } else {
        this.$router.push('/login')
      }
    },

    async getToken() {
      try {
        const data = await this.post('/tokens/create/', {})
        this.token = data.token
        await this.copyToken()
      } catch (err) {
        this.error = err.message
      }
    },

    async copyToken() {
      if (!this.token) return

      try {
        await navigator.clipboard.writeText(this.token)
        const info = document.querySelector('.token-info')
        if (info) {
          info.style.opacity = '1'
          setTimeout(() => info.style.opacity = '0', 2000)
        }
      } catch {
        this.error = 'Ошибка при копировании'
      }
    },

    logout() {
      localStorage.removeItem('userData')
      localStorage.removeItem('userEmail')
      sessionStorage.removeItem('userData')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.profile {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--gray-500);
}

.token-section {
  margin: 1.5rem 0;
}

.token-result {
  margin-top: 1rem;
  padding: 0.75rem;
  background: var(--gray-50);
  border-radius: var(--radius-md);
  border: 1px solid var(--gray-200);
}

.token-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.token-value code {
  font-family: monospace;
  font-size: 0.75rem;
  background: white;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  word-break: break-all;
  flex: 1;
  color: var(--primary);
}

.copy-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}

.copy-btn:hover {
  background: var(--gray-200);
}

.token-info {
  font-size: 0.75rem;
  color: var(--success);
  margin-top: 0.5rem;
  text-align: center;
  opacity: 0;
  transition: opacity 0.3s;
}
</style>
