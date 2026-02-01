<template>
  <div class="layout">
    <header class="header">
      <div class="container">
        <div class="header-content">
          <NuxtLink to="/" class="logo">
            <span class="logo-icon">🎙️</span>
            <span class="logo-text">Voice Word</span>
          </NuxtLink>
          
          <nav class="nav" v-if="isAuthenticated">
            <NuxtLink to="/" class="nav-link">
              <span class="nav-icon">📋</span>
              <span>Записи</span>
            </NuxtLink>
            <NuxtLink to="/upload" class="nav-link nav-link-primary">
              <span class="nav-icon">➕</span>
              <span>Новая запись</span>
            </NuxtLink>
            <button @click="logout" class="nav-link nav-logout">
              <span class="nav-icon">🚪</span>
              <span>Выйти</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
    
    <main class="main">
      <div class="container">
        <slot />
      </div>
    </main>
    
    <footer class="footer">
      <div class="container">
        <p class="footer-text">Voice Word © {{ new Date().getFullYear() }} — Конвертация голоса в текст</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const { isAuthenticated, logout } = useAuth()
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.header {
  background: var(--color-bg-card);
  border-bottom: 2px solid var(--color-border);
  padding: var(--spacing-lg) 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-xl);
  flex-wrap: wrap;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: var(--font-xl);
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
  transition: all var(--transition-normal);
}

.logo:hover {
  text-decoration: none;
  color: var(--color-primary);
  transform: scale(1.02);
}

.logo-icon {
  font-size: var(--font-2xl);
}

.logo-text {
  background: linear-gradient(135deg, var(--color-primary) 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);
  background: transparent;
  border: 2px solid transparent;
  cursor: pointer;
  font-family: inherit;
}

.nav-link:hover {
  color: var(--color-primary);
  background: var(--color-primary-light);
  text-decoration: none;
}

.nav-link.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.nav-link-primary {
  background: var(--color-primary);
  color: #ffffff !important;
  border-color: var(--color-primary);
}

.nav-link-primary:hover {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.nav-icon {
  font-size: 1.3em;
}

.nav-logout {
  color: var(--color-error);
}

.nav-logout:hover {
  background: var(--color-error-light);
  color: var(--color-error);
}

.main {
  flex: 1;
  padding: var(--spacing-3xl) 0;
}

.footer {
  background: var(--color-bg-card);
  border-top: 2px solid var(--color-border);
  padding: var(--spacing-xl) 0;
}

.footer-text {
  text-align: center;
  font-size: var(--font-sm);
  color: var(--color-text-muted);
}

@media (max-width: 640px) {
  .header-content {
    flex-direction: column;
    gap: var(--spacing-lg);
  }
  
  .nav {
    width: 100%;
    justify-content: center;
  }
  
  .nav-link span:not(.nav-icon) {
    display: none;
  }
  
  .nav-link {
    padding: var(--spacing-md);
  }
  
  .nav-icon {
    font-size: 1.5em;
  }
}
</style>
