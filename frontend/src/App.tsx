import { Navigate, Route, Routes } from 'react-router-dom'
import { useConnectionSync } from './stores/useConnectionStore'
import { useSyncQueue } from './hooks/useSyncQueue'
import useAuthStore from './stores/useAuthStore'
import { LoginPage } from './pages/LoginPage'
import { RegistroPage } from './pages/RegistroPage'
import { RequireRole } from './components/RequireRole'
import { DisciplinasPage } from './pages/juez/DisciplinasPage'
import { GrillaPage } from './pages/juez/GrillaPage'
import { PerformanceFlowPage } from './pages/juez/PerformanceFlowPage'
import { AtletaDashboardPage } from './pages/atleta/AtletaDashboardPage'
import { DashboardPage } from './pages/organizador/DashboardPage'
import { CrearTorneoPage } from './pages/organizador/CrearTorneoPage'
import { DetalleTorneoPage } from './pages/organizador/DetalleTorneoPage'
import { TorneoCompetenciasPage } from './pages/organizador/TorneoCompetenciasPage'
import { UsuariosPage } from './pages/organizador/UsuariosPage'
import { AuditoriaCompetenciaPage } from './pages/organizador/AuditoriaCompetenciaPage'
import { AuditoriaPerformancePage } from './pages/organizador/AuditoriaPerformancePage'
import { HealthCheck } from './components/HealthCheck'

function RootRedirect() {
  const rol = useAuthStore((s) => s.rol)
  if (rol === 'juez') return <Navigate to="/juez/disciplinas" replace />
  if (rol === 'organizador') return <Navigate to="/organizador/dashboard" replace />
  if (rol === 'atleta') return <Navigate to="/atleta/dashboard" replace />
  return <Navigate to="/login" replace />
}

function App() {
  useConnectionSync()
  useSyncQueue()

  return (
    <>
      <div className="fixed top-3 right-3 z-50">
        <HealthCheck />
      </div>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegistroPage />} />
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
          path="/juez/grilla"
          element={
            <RequireRole role="juez">
              <GrillaPage />
            </RequireRole>
          }
        />
        <Route
          path="/juez/performance"
          element={
            <RequireRole role="juez">
              <PerformanceFlowPage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/dashboard"
          element={
            <RequireRole role="atleta">
              <AtletaDashboardPage />
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
        <Route
          path="/organizador/torneos/nuevo"
          element={
            <RequireRole role="organizador">
              <CrearTorneoPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/usuarios"
          element={
            <RequireRole role="organizador">
              <UsuariosPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/torneo/:torneoId"
          element={
            <RequireRole role="organizador">
              <DetalleTorneoPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/torneos/:torneoId/competencias"
          element={
            <RequireRole role="organizador">
              <TorneoCompetenciasPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/competencias/:competenciaId/auditoria"
          element={
            <RequireRole role="organizador">
              <AuditoriaCompetenciaPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/competencias/:competenciaId/auditoria/:atletaId"
          element={
            <RequireRole role="organizador">
              <AuditoriaPerformancePage />
            </RequireRole>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
