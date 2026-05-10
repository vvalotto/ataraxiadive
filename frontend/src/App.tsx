import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useConnectionSync } from './stores/useConnectionStore'
import { useSyncQueue } from './hooks/useSyncQueue'
import useAuthStore from './stores/useAuthStore'
import { LoginPage } from './pages/LoginPage'
import { RegistroPage } from './pages/RegistroPage'
import { CambiarPasswordPage } from './pages/CambiarPasswordPage'
import { RecuperarPasswordPage } from './pages/RecuperarPasswordPage'
import { ResetPasswordPage } from './pages/ResetPasswordPage'
import { RequireAuth } from './components/RequireAuth'
import { RequireRole } from './components/RequireRole'
import { DisciplinasPage } from './pages/juez/DisciplinasPage'
import { GrillaPage } from './pages/juez/GrillaPage'
import { PerformanceFlowPage } from './pages/juez/PerformanceFlowPage'
import { AtletaHomePage } from './pages/atleta/AtletaHomePage'
import { AtletaTorneosPage } from './pages/atleta/AtletaTorneosPage'
import { AtletaTorneoDetallePage } from './pages/atleta/AtletaTorneoDetallePage'
import { AtletaInscripcionPage } from './pages/atleta/AtletaInscripcionPage'
import { AtletaMisInscripcionesPage } from './pages/atleta/AtletaMisInscripcionesPage'
import { AtletaDeclararAPPage } from './pages/atleta/AtletaDeclararAPPage'
import { AtletaMiGrillaPage } from './pages/atleta/AtletaMiGrillaPage'
import { AtletaResultadosPage } from './pages/atleta/AtletaResultadosPage'
import { DashboardPage } from './pages/organizador/DashboardPage'
import { DashboardOperativoPage } from './pages/organizador/DashboardOperativoPage'
import { CrearTorneoPage } from './pages/organizador/CrearTorneoPage'
import { DetalleTorneoPage } from './pages/organizador/DetalleTorneoPage'
import { OrganizadorInscriptosPage } from './pages/organizador/OrganizadorInscriptosPage'
import { OrganizadorGrillaPage } from './pages/organizador/OrganizadorGrillaPage'
import { OrganizadorJuecesPage } from './pages/organizador/OrganizadorJuecesPage'
import { TorneoCompetenciasPage } from './pages/organizador/TorneoCompetenciasPage'
import { UsuariosPage } from './pages/organizador/UsuariosPage'
import { AuditoriaCompetenciaPage } from './pages/organizador/AuditoriaCompetenciaPage'
import { AuditoriaPerformancePage } from './pages/organizador/AuditoriaPerformancePage'
import { ResultadosPage } from './pages/organizador/ResultadosPage'
import { PodiosPage } from './pages/organizador/PodiosPage'
import { PublicTorneosPage } from './pages/PublicTorneosPage'
import { HealthCheck } from './components/HealthCheck'

function RootRedirect() {
  const rol = useAuthStore((s) => s.rol)
  if (rol === 'juez') return <Navigate to="/juez/disciplinas" replace />
  if (rol === 'organizador') return <Navigate to="/organizador/torneo" replace />
  if (rol === 'atleta') return <Navigate to="/atleta" replace />
  return <Navigate to="/portalapnea" replace />
}

function GlobalHealthCheck() {
  const location = useLocation()

  if (
    location.pathname.startsWith('/organizador') ||
    location.pathname.startsWith('/juez') ||
    location.pathname.startsWith('/portalapnea')
  ) {
    return null
  }

  return (
    <div className="fixed top-3 right-3 z-50">
      <HealthCheck />
    </div>
  )
}

function App() {
  useConnectionSync()
  useSyncQueue()

  return (
    <>
      <GlobalHealthCheck />
      <Routes>
        <Route path="/portalapnea" element={<PublicTorneosPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegistroPage />} />
        <Route path="/recuperar-password" element={<RecuperarPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route
          path="/cambiar-password"
          element={
            <RequireAuth>
              <CambiarPasswordPage />
            </RequireAuth>
          }
        />
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
          path="/atleta"
          element={
            <RequireRole role="atleta">
              <AtletaHomePage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/dashboard"
          element={<Navigate to="/atleta" replace />}
        />
        <Route
          path="/atleta/torneos"
          element={
            <RequireRole role="atleta">
              <AtletaTorneosPage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/torneos/:torneoId"
          element={
            <RequireRole role="atleta">
              <AtletaTorneoDetallePage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/torneos/:torneoId/inscripcion"
          element={
            <RequireRole role="atleta">
              <AtletaInscripcionPage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/mis-inscripciones"
          element={
            <RequireRole role="atleta">
              <AtletaMisInscripcionesPage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/ap/:torneoId/:disciplina"
          element={
            <RequireRole role="atleta">
              <AtletaDeclararAPPage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/grilla/:competenciaId"
          element={
            <RequireRole role="atleta">
              <AtletaMiGrillaPage />
            </RequireRole>
          }
        />
        <Route
          path="/atleta/resultados"
          element={
            <RequireRole role="atleta">
              <AtletaResultadosPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador"
          element={<Navigate to="/organizador/torneo" replace />}
        />
        <Route
          path="/organizador/dashboard"
          element={<Navigate to="/organizador/torneo" replace />}
        />
        <Route
          path="/organizador/torneo"
          element={
            <RequireRole role="organizador">
              <DashboardPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/panel"
          element={
            <RequireRole role="organizador">
              <DashboardOperativoPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/inscriptos"
          element={
            <RequireRole role="organizador">
              <OrganizadorInscriptosPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/grilla"
          element={
            <RequireRole role="organizador">
              <OrganizadorGrillaPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/jueces"
          element={
            <RequireRole role="organizador">
              <OrganizadorJuecesPage />
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
          path="/organizador/torneos/:torneoId/disciplinas"
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
          path="/organizador/audit-log"
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
        <Route
          path="/organizador/resultados"
          element={
            <RequireRole role="organizador">
              <ResultadosPage />
            </RequireRole>
          }
        />
        <Route
          path="/organizador/podios"
          element={
            <RequireRole role="organizador">
              <PodiosPage />
            </RequireRole>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
