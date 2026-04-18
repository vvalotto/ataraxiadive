let _provider: () => string | null = () => null

export function setTokenProvider(fn: () => string | null): void {
  _provider = fn
}

export function getToken(): string | null {
  return _provider()
}
