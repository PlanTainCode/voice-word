export default defineNuxtRouteMiddleware(async (to) => {
  const { checkAuth, isAuthenticated } = useAuth()
  
  // Пропускаем страницу логина
  if (to.path === '/login') {
    // Если уже авторизован, редиректим на главную
    await checkAuth()
    if (isAuthenticated.value) {
      return navigateTo('/')
    }
    return
  }
  
  // Проверяем авторизацию
  await checkAuth()
  
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})

