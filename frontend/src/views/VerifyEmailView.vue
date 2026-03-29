<template>
  <div class="verify-email">
    <div class="container">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Подтверждение email...</p>
      </div>

      <div v-else-if="success" class="success-message">
        <div class="icon">✅</div>
        <h2>Email подтвержден!</h2>
        <p>{{ successMessage }}</p>
        <button @click="goToLogin" class="btn">Перейти к входу</button>
      </div>

      <div v-else-if="error" class="error-message">
        <div class="icon">❌</div>
        <h2>Ошибка подтверждения</h2>
        <p>{{ errorMessage }}</p>
        <button v-if="needResend" @click="resendVerification" :disabled="resending" class="btn-resend">
          {{ resending ? 'Отправка...' : 'Отправить повторно' }}
        </button>
        <button @click="goToLogin" class="btn">Вернуться к входу</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VerifyEmailView',
  data() {
    return {
      token: null,
      loading: true,
      success: false,
      error: false,
      successMessage: '',
      errorMessage: '',
      needResend: false,
      resending: false,
      email: ''
    }
  },
  mounted() {
    // Получаем токен из URL
    this.token = this.$route.params.token
    if (this.token) {
      this.verifyEmail()
    } else {
      this.loading = false
      this.error = true
      this.errorMessage = 'Неверная ссылка подтверждения'
    }
  },
  methods: {
    async verifyEmail() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/verify-email/${this.token}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.success = true
          this.successMessage = data.message || 'Email успешно подтвержден!'
          // Через 3 секунды автоматически перенаправляем на логин
          setTimeout(() => {
            this.goToLogin()
          }, 3000)
        } else {
          this.error = true
          this.errorMessage = data.message || 'Ошибка подтверждения email'
          this.needResend = data.need_resend || false

          // Если нужно отправить повторно, сохраняем email
          if (data.email) {
            this.email = data.email
          }
        }
      } catch (err) {
        console.error('Ошибка:', err)
        this.error = true
        this.errorMessage = 'Ошибка подключения к серверу'
      } finally {
        this.loading = false
      }
    },

    async resendVerification() {
      if (!this.email) {
        // Если email не пришел в ответе, просим ввести
        this.email = prompt('Введите email для повторной отправки:')
        if (!this.email) return
      }

      this.resending = true

      try {
        const response = await fetch('http://127.0.0.1:8000/api/resend-verification/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: this.email })
        })

        const data = await response.json()

        if (response.ok && data.success) {
          alert('Код подтверждения отправлен повторно! Проверьте почту.')
          this.needResend = false
          this.error = false
          this.loading = true
          // Через 2 секунды показываем форму входа
          setTimeout(() => {
            this.goToLogin()
          }, 2000)
        } else {
          alert(data.message || 'Ошибка при отправке')
        }
      } catch (err) {
        console.error('Ошибка:', err)
        alert('Ошибка подключения к серверу')
      } finally {
        this.resending = false
      }
    },

    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.verify-email {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.container {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.icon {
  font-size: 64px;
  margin-bottom: 1rem;
}

h2 {
  color: #333;
  margin-bottom: 1rem;
}

p {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.loading {
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-message {
  animation: fadeIn 0.5s ease;
}

.error-message {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s;
  margin-top: 1rem;
}

.btn:hover {
  background: #5a67d8;
}

.btn-resend {
  display: inline-block;
  padding: 12px 24px;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin-right: 12px;
  transition: background 0.2s;
}

.btn-resend:hover:not(:disabled) {
  background: #38a169;
}

.btn-resend:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
