<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon-wrapper">
          <span class="login-icon">🎙️</span>
        </div>
        <h1 class="login-title">Voice Word</h1>
        <p class="login-subtitle">Конвертация голоса в текстовые документы</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="error" class="alert alert-error mb-xl">
          {{ error }}
        </div>

        <div class="form-group">
          <label for="username" class="form-label">👤 Логин</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-input"
            placeholder="Введите ваш логин"
            autocomplete="username"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password" class="form-label">🔐 Пароль</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            placeholder="Введите ваш пароль"
            autocomplete="current-password"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="btn btn-primary btn-lg login-btn" :disabled="loading">
          <span v-if="loading" class="loader" style="width: 28px; height: 28px; border-width: 3px;"></span>
          <span v-else>Войти в систему →</span>
        </button>
      </form>
      
      <div class="login-features">
        <div class="feature">
          <span class="feature-icon">🎤</span>
          <span class="feature-text">Загрузка аудио</span>
        </div>
        <div class="feature">
          <span class="feature-icon">✨</span>
          <span class="feature-text">AI обработка</span>
        </div>
        <div class="feature">
          <span class="feature-icon">📄</span>
          <span class="feature-text">Word документ</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

const { login } = useAuth()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'Пожалуйста, заполните все поля'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await login(username.value, password.value)
    router.push('/')
  } catch (e: any) {
    error.value = e.data?.detail || 'Неверный логин или пароль'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  position: relative;
}

.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.login-card {
  width: 100%;
  max-width: 520px;
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: var(--spacing-3xl);
  box-shadow: var(--shadow-xl);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.login-icon-wrapper {
  width: 100px;
  height: 100px;
  margin: 0 auto var(--spacing-xl);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, #fae8ff 100%);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
}

.login-icon {
  font-size: 3.5rem;
}

.login-title {
  font-size: var(--font-2xl);
  margin-bottom: var(--spacing-sm);
  background: linear-gradient(135deg, var(--color-primary) 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  font-size: var(--font-base);
  color: var(--color-text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
}

.login-btn {
  width: 100%;
  margin-top: var(--spacing-lg);
}

.login-features {
  display: flex;
  justify-content: center;
  gap: var(--spacing-xl);
  margin-top: var(--spacing-2xl);
  padding-top: var(--spacing-2xl);
  border-top: 2px solid var(--color-border);
  flex-wrap: wrap;
}

.feature {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.feature-icon {
  font-size: 2rem;
}

.feature-text {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  font-weight: 500;
}

@media (max-width: 480px) {
  .login-card {
    padding: var(--spacing-xl);
  }
  
  .login-features {
    gap: var(--spacing-lg);
  }
}
</style>
