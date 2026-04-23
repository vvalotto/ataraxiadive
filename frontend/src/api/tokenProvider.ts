let _provider: () => string | null = () => null
const AUTH_STORAGE_KEY = 'ataraxiadive-auth'

export function setTokenProvider(fn: () => string | null): void {
  _provider = fn
}

export function getToken(): string | null {
  return _provider()
}

export function handleUnauthorized(): void {
  window.localStorage.removeItem(AUTH_STORAGE_KEY)
  if (window.location.pathname !== '/login') {
    window.location.assign('/login')
  }
}
