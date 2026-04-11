import { Navigate, Route, Routes } from 'react-router-dom'
import { useConnectionSync } from './stores/useConnectionStore'
import useAuthStore from './stores/useAuthStore'
import { LoginPage } from './pages/LoginPage'
import { RequireRole } from './components/RequireRole'
import { DisciplinasPage } from './pages/juez/DisciplinasPage'
import { DashboardPage } from './pages/organizador/DashboardPage'
import { HealthCheck } from './components/HealthCheck'

function RootRedirect() {
  const rol = useAuthStore((s) => s.rol)
  if (rol === 'juez') return <Navigate to="/juez/disciplinas" replace />
  if (rol === 'organizador') return <Navigate to="/organizador/dashboard" replace />
  return <Navigate to="/login" replace />
}

function App() {
  useConnectionSync()

  return (
    <>
      <div className="fixed top-3 right-3 z-50">
        <HealthCheck />
      </div>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<RootRedirect />} />
        <Route
          path="/juez/disciplinas"
          element={
            <RequireRole role="juez">
              <DisciplinasPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/dashboard"
          element={
            <RequireRole role="organizador">
              <DashboardPage />
            </RequireRole>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
