<template>
  <div class="records-page">
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">📋 Мои записи</h1>
        <p class="page-subtitle">Все ваши голосовые записи и документы</p>
      </div>
      <NuxtLink to="/upload" class="btn btn-primary btn-lg">
        ➕ Новая запись
      </NuxtLink>
    </div>

    <div v-if="store.loading && !store.records.length" class="loading-state card">
      <div class="loader"></div>
      <p class="loading-text">Загружаем ваши записи...</p>
    </div>

    <div v-else-if="store.error" class="alert alert-error">
      {{ store.error }}
    </div>

    <div v-else-if="!store.records.length" class="empty-state card">
      <div class="empty-illustration">
        <span class="empty-icon">🎤</span>
      </div>
      <h2 class="empty-title">Записей пока нет</h2>
      <p class="empty-text">Загрузите аудио файл с голосовой записью,<br>и мы преобразуем его в текстовый документ</p>
      <NuxtLink to="/upload" class="btn btn-primary btn-lg mt-xl">
        ➕ Создать первую запись
      </NuxtLink>
    </div>

    <div v-else class="records-grid">
      <NuxtLink
        v-for="record in store.records"
        :key="record.id"
        :to="`/records/${record.id}`"
        class="record-card card card-clickable"
      >
        <div class="record-icon">
          {{ getStatusIcon(record.status) }}
        </div>
        <div class="record-content">
          <h3 class="record-title">{{ record.title }}</h3>
          <div class="record-meta">
            <span :class="['status-badge', `status-${record.status}`]">
              {{ getStatusText(record.status) }}
            </span>
            <span class="record-date">
              {{ formatDate(record.created_at) }}
            </span>
          </div>
        </div>
        <div class="record-arrow">→</div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const store = useRecordsStore()

onMounted(() => {
  store.fetchRecords()
})

// Обновляем каждые 5 секунд если есть записи в обработке
const refreshInterval = ref<NodeJS.Timeout | null>(null)

watch(
  () => store.records,
  (records) => {
    const hasProcessing = records.some(
      (r) => r.status === 'pending' || r.status === 'processing'
    )
    
    if (hasProcessing && !refreshInterval.value) {
      refreshInterval.value = setInterval(() => {
        store.fetchRecords()
      }, 5000)
    } else if (!hasProcessing && refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})

const getStatusIcon = (status: string) => {
  const icons: Record<string, string> = {
    pending: '⏳',
    processing: '⚙️',
    completed: '✅',
    error: '❌',
  }
  return icons[status] || '📄'
}

const getStatusText = (status: string) => {
  const statuses: Record<string, string> = {
    pending: 'Ожидание',
    processing: 'Обработка',
    completed: 'Готово',
    error: 'Ошибка',
  }
  return statuses[status] || status
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.records-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-2xl);
  flex-wrap: wrap;
}

.page-header-content {
  flex: 1;
}

.page-title {
  font-size: var(--font-2xl);
  margin-bottom: var(--spacing-xs);
}

.page-subtitle {
  font-size: var(--font-base);
  color: var(--color-text-secondary);
}

.loading-state {
  text-align: center;
  padding: var(--spacing-3xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xl);
}

.loading-text {
  font-size: var(--font-lg);
  color: var(--color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-3xl);
}

.empty-illustration {
  width: 140px;
  height: 140px;
  margin: 0 auto var(--spacing-xl);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, #fae8ff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 4rem;
}

.empty-title {
  font-size: var(--font-xl);
  margin-bottom: var(--spacing-md);
}

.empty-text {
  font-size: var(--font-base);
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.records-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.record-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
  text-decoration: none;
  color: inherit;
  padding: var(--spacing-xl);
}

.record-card:hover {
  text-decoration: none;
}

.record-icon {
  width: 70px;
  height: 70px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.record-content {
  flex: 1;
  min-width: 0;
}

.record-title {
  font-size: var(--font-lg);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.record-date {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
}

.record-arrow {
  font-size: var(--font-xl);
  color: var(--color-text-muted);
  transition: all var(--transition-normal);
}

.record-card:hover .record-arrow {
  color: var(--color-primary);
  transform: translateX(4px);
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  
  .page-header .btn {
    width: 100%;
  }
  
  .record-card {
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-md);
  }
  
  .record-meta {
    justify-content: center;
  }
  
  .record-arrow {
    display: none;
  }
  
  .record-title {
    white-space: normal;
  }
}
</style>
