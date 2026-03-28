import api from './axios'

export const authAPI = {
  // Регистрация
  register: async (userData) => {
    const response = await api.post('/register/', {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      password_confirm: userData.password2,
      phone: userData.phone || ''
    })
    return response.data
  },

  // Вход
  login: async (email, password) => {
    const response = await api.post('/login/', { email, password })

    // Сохраняем данные пользователя
    if (response.data.success) {
      const userData = {
        id: response.data.user.id,
        username: response.data.user.username,
        email: response.data.user.email,
        phone: response.data.user.phone,
        balance: response.data.user.balance,
        is_verified: response.data.user.is_verified,
        lastLogin: new Date().toLocaleString()
      }

      // Сохраняем в localStorage или sessionStorage
      localStorage.setItem('userData', JSON.stringify(userData))
    }

    return response.data
  },

  // Получение текущего пользователя
  getMe: async () => {
    const response = await api.get('/me/')
    return response.data
  },

  // Выход (очищаем локальные данные)
  logout: () => {
    localStorage.removeItem('userData')
    localStorage.removeItem('userEmail')
    sessionStorage.removeItem('userData')
    // Сессия на сервере очистится при закрытии браузера
  }
}
