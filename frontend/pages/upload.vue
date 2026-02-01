<template>
  <div class="upload-page">
    <div class="page-header">
      <NuxtLink to="/" class="back-link">
        ← Назад к записям
      </NuxtLink>
      <h1 class="page-title">➕ Новая запись</h1>
      <p class="page-subtitle">Загрузите аудио файл для обработки</p>
    </div>

    <form @submit.prevent="handleSubmit" class="upload-form card">
      <div v-if="error" class="alert alert-error mb-xl">
        {{ error }}
      </div>

      <div class="form-group">
        <label for="title" class="form-label">📝 Название записи</label>
        <input
          id="title"
          v-model="title"
          type="text"
          class="form-input"
          placeholder="Например: Интервью от 15 января"
          required
          :disabled="loading"
        />
      </div>

      <div class="form-group">
        <label class="form-label">🎵 Аудио файл</label>
        <div
          class="dropzone"
          :class="{ dragover: isDragging }"
          @click="openFileDialog"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
        >
          <input
            ref="fileInput"
            type="file"
            accept="audio/*,.mp3,.wav,.m4a,.ogg,.flac,.webm"
            hidden
            @change="handleFileSelect"
          />
          
          <div v-if="selectedFile" class="selected-file">
            <div class="file-icon-wrapper">
              <span class="file-icon">🎵</span>
            </div>
            <div class="file-info">
              <p class="file-name">{{ selectedFile.name }}</p>
              <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button 
              type="button" 
              class="file-remove" 
              @click.stop="removeFile"
              :disabled="loading"
              title="Удалить файл"
            >
              ✕
            </button>
          </div>
          
          <template v-else>
            <div class="dropzone-icon-wrapper">
              <span class="dropzone-icon">📁</span>
            </div>
            <p class="dropzone-text">
              Перетащите аудио файл сюда<br />
              или <span class="dropzone-link">нажмите для выбора</span>
            </p>
            <p class="dropzone-formats">
              Поддерживаемые форматы: MP3, WAV, M4A, OGG, FLAC, WEBM
            </p>
          </template>
        </div>
      </div>

      <div class="form-actions">
        <NuxtLink to="/" class="btn">
          Отмена
        </NuxtLink>
        <button
          type="submit"
          class="btn btn-primary btn-lg"
          :disabled="loading || !title || !selectedFile"
        >
          <span v-if="loading" class="loader" style="width: 28px; height: 28px; border-width: 3px;"></span>
          <span v-else>🚀 Начать обработку</span>
        </button>
      </div>
    </form>

    <div class="info-card card mt-2xl">
      <h3 class="info-title">ℹ️ Как это работает</h3>
      <div class="info-steps">
        <div class="info-step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>Загрузка</h4>
            <p>Загрузите аудио файл с голосовой записью</p>
          </div>
        </div>
        <div class="info-step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>Распознавание</h4>
            <p>Whisper AI преобразует речь в текст</p>
          </div>
        </div>
        <div class="info-step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>Обработка</h4>
            <p>GPT проверит и отформатирует текст</p>
          </div>
        </div>
        <div class="info-step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h4>Результат</h4>
            <p>Получите готовый Word документ</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const store = useRecordsStore()
const router = useRouter()

const title = ref('')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const loading = ref(false)
const error = ref('')

const openFileDialog = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files?.length) {
    selectedFile.value = input.files[0]
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files?.length) {
    const file = files[0]
    if (file.type.startsWith('audio/') || /\.(mp3|wav|m4a|ogg|flac|webm)$/i.test(file.name)) {
      selectedFile.value = file
    } else {
      error.value = 'Пожалуйста, выберите аудио файл'
    }
  }
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' Б'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' КБ'
  return (bytes / (1024 * 1024)).toFixed(1) + ' МБ'
}

const handleSubmit = async () => {
  if (!title.value || !selectedFile.value) {
    error.value = 'Заполните все обязательные поля'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const record = await store.createRecord(title.value, selectedFile.value)
    router.push(`/records/${record.id}`)
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка при создании записи'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 750px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--spacing-2xl);
}

.back-link {
  display: inline-flex;
  align-items: center;
  font-size: var(--font-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
  font-weight: 500;
}

.back-link:hover {
  color: var(--color-primary);
}

.page-title {
  font-size: var(--font-2xl);
  margin-bottom: var(--spacing-xs);
}

.page-subtitle {
  font-size: var(--font-base);
  color: var(--color-text-secondary);
}

.upload-form {
  padding: var(--spacing-2xl);
}

.selected-file {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  background: var(--color-success-light);
  border: 2px solid var(--color-success);
  border-radius: var(--radius-md);
  width: 100%;
}

.file-icon-wrapper {
  width: 60px;
  height: 60px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon {
  font-size: 2rem;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: var(--font-base);
  font-weight: 600;
  color: var(--color-text);
  word-break: break-all;
}

.file-size {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.file-remove {
  width: 48px;
  height: 48px;
  font-size: var(--font-lg);
  color: var(--color-text-muted);
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-remove:hover {
  color: var(--color-error);
  border-color: var(--color-error);
  background: var(--color-error-light);
}

.dropzone-icon-wrapper {
  width: 100px;
  height: 100px;
  background: var(--color-primary-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dropzone-icon {
  font-size: 3rem;
}

.dropzone-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: underline;
}

.dropzone-formats {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  margin-top: var(--spacing-sm);
}

.form-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: flex-end;
  margin-top: var(--spacing-xl);
  flex-wrap: wrap;
}

.info-card {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, #fae8ff 100%);
  border-color: var(--color-primary);
}

.info-title {
  font-size: var(--font-lg);
  margin-bottom: var(--spacing-xl);
}

.info-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-xl);
}

.info-step {
  display: flex;
  gap: var(--spacing-md);
}

.step-number {
  width: 40px;
  height: 40px;
  background: var(--color-primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--font-base);
  flex-shrink: 0;
}

.step-content h4 {
  font-size: var(--font-base);
  margin-bottom: var(--spacing-xs);
}

.step-content p {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
}

@media (max-width: 640px) {
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .form-actions .btn {
    width: 100%;
  }
  
  .info-steps {
    grid-template-columns: 1fr;
  }
}
</style>
