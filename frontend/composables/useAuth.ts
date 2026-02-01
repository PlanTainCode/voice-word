interface User {
  id: number
  username: string
  created_at: string
}

interface LoginResponse {
  access_token: string
  token_type: string
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const router = useRouter()
  
  const user = useState<User | null>('user', () => null)
  const isAuthenticated = computed(() => !!user.value)
  const authToken = useCookie('auth_token', {
    maxAge: 60 * 60 * 24 * 7, // 7 дней
    secure: false, // HTTP режим
    sameSite: 'lax',
  })

  const login = async (username: string, password: string) => {
    const data = await $fetch<LoginResponse>(`${config.public.apiBase}/auth/login`, {
      method: 'POST',
      body: { username, password },
    })
    
    authToken.value = data.access_token
    
    // Сразу получаем пользователя с новым токеном
    const userData = await $fetch<User>(`${config.public.apiBase}/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` }
    })
    user.value = userData
    
    return data
  }

  const logout = () => {
    authToken.value = null
    user.value = null
    router.push('/login')
  }

  const fetchUser = async () => {
    if (!authToken.value) {
      user.value = null
      return null
    }

    try {
      const data = await $fetch<User>(`${config.public.apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken.value}` }
      })
      user.value = data
      return data
    } catch (error) {
      authToken.value = null
      user.value = null
      return null
    }
  }

  const checkAuth = async () => {
    if (authToken.value && !user.value) {
      await fetchUser()
    }
    return isAuthenticated.value
  }

  return {
    user,
    isAuthenticated,
    login,
    logout,
    fetchUser,
    checkAuth,
  }
}

