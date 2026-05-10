import { useNavigate } from 'react-router-dom'
import useAuthStore from '../stores/useAuthStore'

export function useNavigateWithRedirect() {
  const navigate = useNavigate()
  const token = useAuthStore((s) => s.token)

  return (destino: string) => {
    if (!token) {
      sessionStorage.setItem('redirectAfterLogin', destino)
      navigate('/login')
    } else {
      navigate(destino)
    }
  }
}
