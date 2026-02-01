import { defineStore } from 'pinia'

interface Record {
  id: number
  title: string
  original_text: string | null
  processed_text: string | null
  audio_file_path: string | null
  word_file_path: string | null
  status: 'pending' | 'processing' | 'completed' | 'error'
  error_message: string | null
  created_at: string
  updated_at: string
}

interface RecordListItem {
  id: number
  title: string
  status: string
  created_at: string
}

export const useRecordsStore = defineStore('records', {
  state: () => ({
    records: [] as RecordListItem[],
    currentRecord: null as Record | null,
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchRecords() {
      const { request } = useApi()
      this.loading = true
      this.error = null

      try {
        this.records = await request<RecordListItem[]>('/records/')
      } catch (e: any) {
        this.error = e.message || 'Ошибка загрузки записей'
      } finally {
        this.loading = false
      }
    },

    async fetchRecord(id: number) {
      const { request } = useApi()
      this.loading = true
      this.error = null

      try {
        this.currentRecord = await request<Record>(`/records/${id}`)
        return this.currentRecord
      } catch (e: any) {
        this.error = e.message || 'Ошибка загрузки записи'
        return null
      } finally {
        this.loading = false
      }
    },

    async createRecord(title: string, audioFile: File) {
      const { uploadFile } = useApi()
      this.loading = true
      this.error = null

      try {
        const formData = new FormData()
        formData.append('title', title)
        formData.append('audio_file', audioFile)

        const record = await uploadFile<Record>('/records/', formData)
        await this.fetchRecords()
        return record
      } catch (e: any) {
        this.error = e.message || 'Ошибка создания записи'
        throw e
      } finally {
        this.loading = false
      }
    },

    async updateRecord(id: number, data: { title?: string; processed_text?: string }) {
      const { request } = useApi()
      this.loading = true
      this.error = null

      try {
        const record = await request<Record>(`/records/${id}`, {
          method: 'PATCH',
          body: data,
        })
        this.currentRecord = record
        await this.fetchRecords()
        return record
      } catch (e: any) {
        this.error = e.message || 'Ошибка обновления записи'
        throw e
      } finally {
        this.loading = false
      }
    },

    async deleteRecord(id: number) {
      const { request } = useApi()
      this.loading = true
      this.error = null

      try {
        await request(`/records/${id}`, { method: 'DELETE' })
        this.records = this.records.filter(r => r.id !== id)
        if (this.currentRecord?.id === id) {
          this.currentRecord = null
        }
      } catch (e: any) {
        this.error = e.message || 'Ошибка удаления записи'
        throw e
      } finally {
        this.loading = false
      }
    },

    async regenerateWord(id: number) {
      const { request } = useApi()
      this.loading = true
      this.error = null

      try {
        const record = await request<Record>(`/records/${id}/regenerate-word`, {
          method: 'POST',
        })
        this.currentRecord = record
        return record
      } catch (e: any) {
        this.error = e.message || 'Ошибка генерации документа'
        throw e
      } finally {
        this.loading = false
      }
    },

    getDownloadUrl(id: number, type: 'audio' | 'word') {
      const config = useRuntimeConfig()
      const token = useCookie('auth_token')
      return `${config.public.apiBase}/records/${id}/download/${type}?token=${token.value}`
    },
  },
})

