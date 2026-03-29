<template>
  <div class="login">
    <AppCard>
      <h1>Вход в систему</h1>

      <div v-if="error" class="message message-error">
        {{ error }}
      </div>

      <div v-if="success" class="message message-success">
        {{ success }}
      </div>

      <form @submit.prevent="handleLogin">
        <AppInput v-model="form.email" type="email" label="Email" required />
        <AppInput v-model="form.password" type="password" label="Пароль" required />

        <label class="checkbox">
          <input v-model="form.rememberMe" type="checkbox" />
          <span>Запомнить меня</span>
        </label>

        <AppButton :disabled="loading" variant="primary" block>
          {{ loading ? 'Вход...' : 'Войти' }}
        </AppButton>
      </form>

      <div class="links">
        <router-link to="/register">Регистрация</router-link>
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
  name: 'LoginView',
  components: { AppCard, AppInput, AppButton },
  setup() {
    const { loading, error, post } = useApi()
    return { loading, error, post }
  },
  data() {
    return {
      form: {
        email: '',
        password: '',
        rememberMe: false
      },
      success: ''
    }
  },
  mounted() {
    const saved = localStorage.getItem('userEmail')
    if (saved) {
      this.form.email = saved
      this.form.rememberMe = true
    }
  },
  methods: {
    async handleLogin() {
      if (!this.form.email || !this.form.password) {
        this.error = 'Заполните все поля'
        return
      }

      try {
        const data = await this.post('/login/', {
          email: this.form.email,
          password: this.form.password
        })

        const userData = {
          id: data.user.id,
          username: data.user.username,
          email: data.user.email,
          lastLogin: new Date().toLocaleString()
        }

        if (this.form.rememberMe) {
          localStorage.setItem('userEmail', this.form.email)
          localStorage.setItem('userData', JSON.stringify(userData))
        } else {
          sessionStorage.setItem('userData', JSON.stringify(userData))
        }

        this.success = 'Вход выполнен! Перенаправление...'
        setTimeout(() => this.$router.push('/profile'), 1000)
      } catch (err) {
        this.error = err.message
      }
    }
  }
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}
</style>
