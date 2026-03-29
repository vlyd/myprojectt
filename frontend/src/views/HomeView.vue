<template>
  <div class="home">
    <AppCard>
      <h1>Добро пожаловать!</h1>
      <p class="subtitle">Выберите действие</p>

      <div class="actions">
        <router-link to="/login" class="btn btn-primary">Войти</router-link>
        <router-link to="/register" class="btn btn-secondary">Регистрация</router-link>
      </div>
    </AppCard>
  </div>
</template>

<script>
import AppCard from '@/components/AppCard.vue'

export default {
  name: 'HomeView',
  components: { AppCard }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 1rem;
}

.subtitle {
  text-align: center;
  color: var(--gray-500);
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .actions {
    flex-direction: column;
  }

  .actions .btn {
    text-align: center;
  }
}
</style>
