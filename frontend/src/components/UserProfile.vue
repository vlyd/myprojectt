<template>
  <div class="profile-container">
    <div class="profile-card">
      <h1>Личный кабинет</h1>

      <div v-if="!isAuthenticated" class="auth-section">
        <h2>Вход в систему</h2>
        <p class="info-text">Для получения токена введите свои учетные данные</p>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">Email:</label>
            <input
              type="email"
              id="email"
              v-model="loginForm.email"
              placeholder="example@mail.com"
              required
            >
          </div>

          <div class="form-group">
            <label for="password">Пароль:</label>
            <input
              type="password"
              id="password"
              v-model="loginForm.password"
              placeholder="Введите пароль"
              required
            >
          </div>

          <button type="submit" :disabled="isLoading" class="btn-primary">
            {{ isLoading ? 'Получение токена...' : 'Получить токен' }}
          </button>
        </form>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>

      <div v-else class="profile-section">
        <div class="user-info">
          <h2>Добро пожаловать!</h2>
          <p><strong>Email:</strong> {{ userEmail }}</p>
        </div>

        <div class="token-section">
          <h3>Ваш токен доступа:</h3>
          <div class="token-display">
            <code>{{ authToken }}</code>
            <button @click="copyToken" class="btn-copy" title="Копировать токен">
              📋
            </button>
          </div>
          <p class="token-hint">Токен действителен в течение текущей сессии</p>
        </div>

        <button @click="logout" class="btn-secondary">
          Выйти
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      loginForm: {
        email: '',
        password: ''
      },
      isAuthenticated: false,
      authToken: '',
      userEmail: '',
      isLoading: false,
      errorMessage: ''
    }
  },
  methods: {
    async handleLogin() {
      this.isLoading = true
      this.errorMessage = ''

      try {
        // Имитация запроса к API для получения токена
        const response = await this.mockLoginRequest(
          this.loginForm.email,
          this.loginForm.password
        )

        this.authToken = response.token
        this.userEmail = this.loginForm.email
        this.isAuthenticated = true

        // Очищаем форму
        this.loginForm.email = ''
        this.loginForm.password = ''
      } catch (error) {
        this.errorMessage = error.message || 'Ошибка при получении токена'
      } finally {
        this.isLoading = false
      }
    },

    // Имитация запроса к серверу
    mockLoginRequest(email, password) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          // Простая валидация для демонстрации
          if (email && password) {
            resolve({
              token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
            })
          } else {
            reject(new Error('Неверный email или пароль'))
          }
        }, 1000)
      })
    },

    logout() {
      this.isAuthenticated = false
      this.authToken = ''
      this.userEmail = ''
    },

    async copyToken() {
      try {
        await navigator.clipboard.writeText(this.authToken)
        alert('Токен скопирован в буфер обмена')
      } catch (err) {
        console.error('Ошибка при копировании:', err)
      }
    }
  }
}
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.profile-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 1.5rem;
}

.info-text {
  text-align: center;
  color: #666;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.btn-primary {
  width: 100%;
  padding: 0.75rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-secondary {
  width: 100%;
  padding: 0.75rem;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 1rem;
}

.btn-secondary:hover {
  background-color: #da190b;
}

.btn-copy {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  transition: background-color 0.3s;
}

.btn-copy:hover {
  background-color: #f0f0f0;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 5px;
  border-left: 4px solid #c62828;
}

.user-info {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1.5rem;
}

.user-info p {
  margin: 0.5rem 0 0;
  color: #555;
}

.token-section {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.token-section h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #333;
}

.token-display {
  display: flex;
  align-items: center;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 0.5rem;
  word-break: break-all;
}

.token-display code {
  flex: 1;
  font-family: monospace;
  font-size: 0.85rem;
  color: #333;
}

.token-hint {
  font-size: 0.85rem;
  color: #666;
  margin: 0.5rem 0 0;
  font-style: italic;
}

@media (max-width: 600px) {
  .profile-card {
    margin: 1rem;
    padding: 1.5rem;
  }
}
</style>
