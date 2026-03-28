import api from './axios'

export const tokensAPI = {
  // Создание токена
  createToken: async (daysValid = 30, trafficLimitMb = 1024) => {
    const response = await api.post('/tokens/create/', {
      days_valid: daysValid,
      traffic_limit_mb: trafficLimitMb
    })
    return response.data
  },

  // Получение всех токенов пользователя
  getTokens: async () => {
    const response = await api.get('/tokens/')
    return response.data
  },

  // Проверка статуса токена
  checkTokenStatus: async (token) => {
    const response = await api.get(`/token/${token}/status/`)
    return response.data
  },

  // Отзыв токена
  revokeToken: async (tokenId) => {
    const response = await api.post(`/tokens/${tokenId}/revoke/`)
    return response.data
  },

  // Подключение к прокси (для десктоп клиента, не для фронта)
  connectToProxy: async (token, clientInfo = 'Web Interface') => {
    const response = await api.post('/connect/', {
      token: token,
      client_info: clientInfo
    })
    return response.data
  },

  // Отключение от прокси
  disconnect: async (connectionId = null, token = null) => {
    const payload = connectionId ? { connection_id: connectionId } : { token: token }
    const response = await api.post('/disconnect/', payload)
    return response.data
  },

  // Получить мои активные подключения
  getMyConnections: async () => {
    const response = await api.get('/my-connections/')
    return response.data
  },

  // Получить список серверов
  getServers: async () => {
    const response = await api.get('/servers/')
    return response.data
  }
}
