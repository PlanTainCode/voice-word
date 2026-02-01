<template>
  <div class="record-page">
    <div class="page-header">
      <NuxtLink to="/" class="back-link">
        ← Назад к записям
      </NuxtLink>
    </div>

    <div v-if="store.loading && !store.currentRecord" class="loading-state card">
      <div class="loader"></div>
      <p class="loading-text">Загружаем запись...</p>
    </div>

    <div v-else-if="store.error" class="alert alert-error">
      {{ store.error }}
    </div>

    <template v-else-if="record">
      <div class="record-header card">
        <div class="record-title-row">
          <div v-if="!isEditingTitle" class="title-display">
            <h1 class="record-title">{{ record.title }}</h1>
            <button 
              class="btn-edit" 
              @click="startEditingTitle"
              title="Редактировать название"
            >
              ✏️
            </button>
          </div>
          <div v-else class="title-edit">
            <input
              v-model="editedTitle"
              type="text"
              class="form-input"
              @keyup.enter="saveTitle"
              @keyup.escape="cancelEditingTitle"
              autofocus
            />
            <button class="btn btn-primary" @click="saveTitle">
              Сохранить
            </button>
            <button class="btn" @click="cancelEditingTitle">
              Отмена
            </button>
          </div>
        </div>

        <div class="record-meta">
          <span :class="['status-badge', `status-${record.status}`]">
            {{ getStatusText(record.status) }}
          </span>
          <span class="record-date">
            📅 {{ formatDate(record.created_at) }}
          </span>
        </div>

        <div v-if="record.error_message" class="alert alert-error mt-xl">
          ⚠️ {{ record.error_message }}
        </div>

        <div class="record-actions mt-xl">
          <a
            v-if="record.audio_file_path"
            :href="getDownloadUrl('audio')"
            class="btn"
            target="_blank"
          >
            🎵 Скачать аудио
          </a>
          <a
            v-if="record.word_file_path"
            :href="getDownloadUrl('word')"
            class="btn btn-success"
            target="_blank"
          >
            📄 Скачать Word
          </a>
          <button
            v-if="record.processed_text && isEdited"
            class="btn btn-primary"
            @click="regenerateWord"
            :disabled="regenerating"
          >
            <span v-if="regenerating">⏳ Создание...</span>
            <span v-else>🔄 Пересоздать Word</span>
          </button>
          <button
            class="btn btn-danger"
            @click="confirmDelete"
          >
            🗑️ Удалить
          </button>
        </div>
      </div>

      <!-- Обработка в процессе -->
      <div v-if="record.status === 'pending' || record.status === 'processing'" class="processing-state card">
        <div class="processing-animation">
          <div class="loader"></div>
        </div>
        <h2 class="processing-title">
          {{ record.status === 'pending' ? '⏳ Ожидание обработки' : '⚙️ Обрабатываем запись' }}
        </h2>
        <p class="processing-text">
          Это может занять несколько минут в зависимости от длины записи.<br>
          Страница обновится автоматически.
        </p>
        <div class="processing-steps">
          <div :class="['processing-step', { active: true, done: record.status === 'processing' }]">
            <span class="step-icon">🎵</span> Загрузка файла
          </div>
          <div :class="['processing-step', { active: record.status === 'processing', done: !!record.original_text }]">
            <span class="step-icon">🎤</span> Распознавание речи
          </div>
          <div :class="['processing-step', { active: !!record.original_text }]">
            <span class="step-icon">✨</span> Обработка текста
          </div>
          <div class="processing-step">
            <span class="step-icon">📄</span> Создание документа
          </div>
        </div>
      </div>

      <!-- Текст -->
      <div v-if="record.processed_text || record.original_text" class="text-section">
        <div class="text-tabs">
          <button
            :class="['tab-btn', { active: activeTab === 'processed' }]"
            @click="activeTab = 'processed'"
            :disabled="!record.processed_text"
          >
            ✨ Обработанный текст
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'original' }]"
            @click="activeTab = 'original'"
            :disabled="!record.original_text"
          >
            📝 Оригинал от Whisper
          </button>
        </div>

        <div class="text-content card">
          <template v-if="activeTab === 'processed'">
            <div v-if="!isEditingText" class="text-display">
              <div class="text-body" v-html="formatText(record.processed_text || '')"></div>
              <button class="btn mt-xl" @click="startEditingText">
                ✏️ Редактировать текст
              </button>
            </div>
            <div v-else class="text-edit">
              <textarea
                v-model="editedText"
                class="form-textarea"
                rows="15"
              ></textarea>
              <div class="text-edit-actions">
                <button class="btn btn-primary" @click="saveText">
                  💾 Сохранить изменения
                </button>
                <button class="btn" @click="cancelEditingText">
                  Отмена
                </button>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="text-body text-original">
              {{ record.original_text }}
            </div>
          </template>
        </div>
      </div>
    </template>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal-card card" @click.stop>
        <div class="modal-icon">⚠️</div>
        <h2 class="modal-title">Удалить запись?</h2>
        <p class="modal-text">
          Вы уверены, что хотите удалить эту запись?<br>
          Это действие нельзя отменить.
        </p>
        <div class="modal-actions">
          <button class="btn" @click="showDeleteModal = false">
            Отмена
          </button>
          <button class="btn btn-danger" @click="deleteRecord">
            🗑️ Да, удалить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const store = useRecordsStore()
const config = useRuntimeConfig()

const recordId = computed(() => Number(route.params.id))
const record = computed(() => store.currentRecord)

const activeTab = ref<'processed' | 'original'>('processed')
const isEditingTitle = ref(false)
const isEditingText = ref(false)
const editedTitle = ref('')
const editedText = ref('')
const originalText = ref('')
const isEdited = ref(false)
const regenerating = ref(false)
const showDeleteModal = ref(false)

// Загрузка записи
const loadRecord = async () => {
  await store.fetchRecord(recordId.value)
  if (record.value?.processed_text) {
    originalText.value = record.value.processed_text
  }
}

onMounted(loadRecord)

// Автообновление при обработке
const refreshInterval = ref<NodeJS.Timeout | null>(null)

watch(
  () => record.value?.status,
  (status) => {
    if (status === 'pending' || status === 'processing') {
      if (!refreshInterval.value) {
        refreshInterval.value = setInterval(loadRecord, 3000)
      }
    } else {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})

// Редактирование названия
const startEditingTitle = () => {
  editedTitle.value = record.value?.title || ''
  isEditingTitle.value = true
}

const cancelEditingTitle = () => {
  isEditingTitle.value = false
}

const saveTitle = async () => {
  if (!editedTitle.value.trim()) return
  await store.updateRecord(recordId.value, { title: editedTitle.value })
  isEditingTitle.value = false
}

// Редактирование текста
const startEditingText = () => {
  editedText.value = record.value?.processed_text || ''
  isEditingText.value = true
}

const cancelEditingText = () => {
  isEditingText.value = false
}

const saveText = async () => {
  await store.updateRecord(recordId.value, { processed_text: editedText.value })
  isEditingText.value = false
  isEdited.value = editedText.value !== originalText.value
}

// Перегенерация Word
const regenerateWord = async () => {
  regenerating.value = true
  try {
    await store.regenerateWord(recordId.value)
    isEdited.value = false
    originalText.value = record.value?.processed_text || ''
  } finally {
    regenerating.value = false
  }
}

// Удаление
const confirmDelete = () => {
  showDeleteModal.value = true
}

const deleteRecord = async () => {
  await store.deleteRecord(recordId.value)
  router.push('/')
}

// Утилиты
const getDownloadUrl = (type: 'audio' | 'word') => {
  const token = useCookie('auth_token')
  return `${config.public.apiBase}/records/${recordId.value}/download/${type}?token=${token.value}`
}

const getStatusText = (status: string) => {
  const statuses: Record<string, string> = {
    pending: '⏳ Ожидание',
    processing: '⚙️ Обработка',
    completed: '✅ Готово',
    error: '❌ Ошибка',
  }
  return statuses[status] || status
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatText = (text: string) => {
  return text
    .split('\n\n')
    .map((p) => `<p>${p.replace(/\n/g, '<br>')}</p>`)
    .join('')
}
</script>

<style scoped>
.record-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--spacing-lg);
}

.back-link {
  display: inline-flex;
  align-items: center;
  font-size: var(--font-base);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.back-link:hover {
  color: var(--color-primary);
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

.record-header {
  margin-bottom: var(--spacing-xl);
}

.record-title-row {
  margin-bottom: var(--spacing-lg);
}

.title-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.record-title {
  font-size: var(--font-2xl);
  word-break: break-word;
}

.btn-edit {
  width: 50px;
  height: 50px;
  font-size: var(--font-lg);
  background: var(--color-bg);
  border: 2px solid var(--color-border);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-edit:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.title-edit {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.title-edit .form-input {
  flex: 1;
  min-width: 250px;
}

.record-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
  flex-wrap: wrap;
}

.record-date {
  font-size: var(--font-base);
  color: var(--color-text-secondary);
}

.record-actions {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.processing-state {
  text-align: center;
  padding: var(--spacing-3xl);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, #fae8ff 100%);
  border-color: var(--color-primary);
}

.processing-animation {
  margin-bottom: var(--spacing-xl);
}

.processing-title {
  font-size: var(--font-xl);
  margin-bottom: var(--spacing-md);
}

.processing-text {
  font-size: var(--font-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2xl);
}

.processing-steps {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.processing-step {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-card);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--color-text-muted);
  border: 2px solid var(--color-border);
}

.processing-step.active {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.processing-step.done {
  color: var(--color-success);
  border-color: var(--color-success);
  background: var(--color-success-light);
}

.step-icon {
  font-size: 1.2em;
}

.text-section {
  margin-top: var(--spacing-xl);
}

.text-tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
}

.tab-btn {
  padding: var(--spacing-md) var(--spacing-xl);
  font-family: inherit;
  font-size: var(--font-base);
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.tab-btn:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.tab-btn.active {
  color: #ffffff;
  border-color: var(--color-primary);
  background: var(--color-primary);
}

.tab-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-content {
  padding: var(--spacing-2xl);
}

.text-body {
  font-size: var(--font-base);
  line-height: 2;
  color: var(--color-text);
}

.text-body :deep(p) {
  margin-bottom: var(--spacing-xl);
  text-indent: 2em;
}

.text-body :deep(p:last-child) {
  margin-bottom: 0;
}

.text-original {
  white-space: pre-wrap;
  color: var(--color-text-secondary);
  background: var(--color-bg);
  padding: var(--spacing-xl);
  border-radius: var(--radius-md);
}

.text-edit-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  flex-wrap: wrap;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-card {
  max-width: 480px;
  width: 100%;
  padding: var(--spacing-2xl);
  text-align: center;
}

.modal-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
}

.modal-title {
  font-size: var(--font-xl);
  margin-bottom: var(--spacing-md);
}

.modal-text {
  font-size: var(--font-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2xl);
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .record-actions,
  .text-edit-actions,
  .modal-actions {
    flex-direction: column;
  }
  
  .record-actions .btn,
  .text-edit-actions .btn,
  .modal-actions .btn {
    width: 100%;
  }
  
  .processing-steps {
    flex-direction: column;
    align-items: center;
  }
}
</style>
