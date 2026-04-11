import { HealthCheck } from './components/HealthCheck'
import { useConnectionSync } from './stores/useConnectionStore'

function App() {
  useConnectionSync()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-3xl font-bold text-gray-800">AtaraxiaDive</h1>
      <p className="text-gray-500">Plataforma de gestión de torneos de apnea</p>
      <HealthCheck />
    </div>
  )
}

export default App
