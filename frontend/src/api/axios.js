// src/api/axios.js
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000/api'  // ← используйте 127.0.0.1

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true,  // ← ОБЯЗАТЕЛЬНО для отправки cookies!
})

export default api
