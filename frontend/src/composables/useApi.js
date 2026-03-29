import { ref } from 'vue'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const getCsrfToken = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/csrf/', {
        credentials: 'include'
      })
      const data = await response.json()
      return data.csrfToken
    } catch (err) {
      console.error('Failed to get CSRF token:', err)
      return null
    }
  }

  const request = async (url, options = {}) => {
    loading.value = true
    error.value = null

    try {
      // Добавляем credentials для отправки cookies
      const defaultOptions = {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      }

      // Для методов, кроме GET, добавляем CSRF токен
      if (options.method && options.method !== 'GET') {
        const csrfToken = await getCsrfToken()
        if (csrfToken) {
          defaultOptions.headers['X-CSRFToken'] = csrfToken
        }
      }

      const mergedOptions = { ...defaultOptions, ...options }

      const response = await fetch(`${API_BASE_URL}${url}`, mergedOptions)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Ошибка запроса')
      }

      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const get = (url) => {
    return request(url, { method: 'GET' })
  }

  const post = (url, data) => {
    return request(url, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  const put = (url, data) => {
    return request(url, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  const del = (url) => {
    return request(url, { method: 'DELETE' })
  }

  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del
  }
}
