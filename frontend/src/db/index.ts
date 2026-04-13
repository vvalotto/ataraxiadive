import Dexie, { type EntityTable } from 'dexie'
import type { ComandoQueueRecord, GrillaCacheRecord } from './schema'

class AtaraxiaDiveDB extends Dexie {
  grilla_cache!: EntityTable<GrillaCacheRecord, 'id'>
  comando_queue!: EntityTable<ComandoQueueRecord, 'id'>

  constructor() {
    super('AtaraxiaDiveDB')
    this.version(1).stores({
      grilla_cache: '++id, [competencia_id+disciplina], cached_at',
      comando_queue: '++id, estado, creado_at',
    })
  }
}

// Singleton de IndexedDB para evitar múltiples conexiones por sesión.
export const db = new AtaraxiaDiveDB()
