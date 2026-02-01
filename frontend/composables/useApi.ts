export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const getAuthHeaders = () => {
    const token = useCookie('auth_token')
    return token.value ? { Authorization: `Bearer ${token.value}` } : {}
  }

  const request = async <T>(
    endpoint: string,
    options: {
      method?: string
      body?: any
      headers?: Record<string, string>
    } = {}
  ): Promise<T> => {
    const { method = 'GET', body, headers = {} } = options

    const response = await $fetch<T>(`${apiBase}${endpoint}`, {
      method,
      body,
      headers: {
        ...getAuthHeaders(),
        ...headers,
      },
    })

    return response
  }

  const uploadFile = async <T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> => {
    const response = await $fetch<T>(`${apiBase}${endpoint}`, {
      method: 'POST',
      body: formData,
      headers: getAuthHeaders(),
    })

    return response
  }

  return {
    request,
    uploadFile,
    apiBase,
    getAuthHeaders,
  }
}

