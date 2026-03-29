<template>
  <div class="register">
    <AppCard>
      <h1>Регистрация</h1>

      <div v-if="successMessage" class="message message-success">
        <p>{{ successMessage }}</p>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem">
          <router-link to="/login" class="btn btn-primary">Войти</router-link>
          <button @click="resetForm" class="btn btn-secondary">Еще</button>
        </div>
      </div>

      <form v-else @submit.prevent="handleRegister">
        <div v-if="serverStatus" :class="['server-status', serverStatusClass]">
          {{ serverStatus }}
        </div>

        <div v-if="error" class="message message-error">
          {{ error }}
        </div>

        <AppInput v-model="form.username" label="Логин" required />
        <AppInput v-model="form.email" type="email" label="Email" required />
        <AppInput v-model="form.password" type="password" label="Пароль" required />
        <AppInput v-model="form.password2" type="password" label="Повторите пароль" required />

        <label class="checkbox">
          <input v-model="form.acceptTerms" type="checkbox" required />
          <span>Я принимаю условия</span>
        </label>

        <AppButton :disabled="loading" variant="primary" block>
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </AppButton>
      </form>

      <div class="links">
        <router-link to="/login">Уже есть аккаунт? Войти</router-link>
        <span>|</span>
        <router-link to="/">На главную</router-link>
      </div>
    </AppCard>
  </div>
</template>

<script>
import AppCard from '@/components/AppCard.vue'
import AppInput from '@/components/AppInput.vue'
import AppButton from '@/components/AppButton.vue'
import { useApi } from '@/composables/useApi'

export default {
  name: 'RegisterView',
  components: { AppCard, AppInput, AppButton },
  setup() {
    const { loading, error, post } = useApi()
    return { loading, error, post }
  },
  data() {
    return {
      form: {
        username: '',
        email: '',
        password: '',
        password2: '',
        acceptTerms: false
      },
      successMessage: '',
      serverStatus: '',
      serverStatusClass: ''
    }
  },
  mounted() {
    this.checkServerConnection()
  },
  methods: {
    async checkServerConnection() {
      this.serverStatus = 'Проверка подключения...'
      this.serverStatusClass = 'status-checking'

      try {
        await fetch('http://127.0.0.1:8000/api/login/', { method: 'OPTIONS', signal: AbortSignal.timeout(3000) })
        this.serverStatus = 'Сервер доступен'
        this.serverStatusClass = 'status-success'
        setTimeout(() => this.serverStatus = '', 3000)
      } catch {
        this.serverStatus = 'Сервер недоступен! Запустите Django'
        this.serverStatusClass = 'status-error'
      }
    },

    isValidEmail(email) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    },

    async handleRegister() {
      if (!this.form.username || !this.form.email || !this.form.password || !this.form.password2) {
        this.error = 'Заполните все поля'
        return
      }
      if (this.form.password !== this.form.password2) {
        this.error = 'Пароли не совпадают'
        return
      }
      if (!this.form.acceptTerms) {
        this.error = 'Примите условия'
        return
      }
      if (!this.isValidEmail(this.form.email)) {
        this.error = 'Некорректный email'
        return
      }
      if (this.form.password.length < 6) {
        this.error = 'Пароль должен быть не менее 6 символов'
        return
      }

      try {
        await this.post('/register/', {
          username: this.form.username,
          email: this.form.email,
          password: this.form.password,
          password_confirm: this.form.password2
        })
        this.successMessage = `Аккаунт ${this.form.username} создан! Теперь вы можете войти.`
      } catch (err) {
        this.error = err.message
      }
    },

    resetForm() {
      this.form = { username: '', email: '', password: '', password2: '', acceptTerms: false }
      this.successMessage = ''
      this.error = ''
      this.serverStatus = ''
    }
  }
}
</script>

<style scoped>
.register {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}
</style>
