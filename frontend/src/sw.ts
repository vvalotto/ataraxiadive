/// <reference lib="webworker" />
import { clientsClaim } from 'workbox-core'
import { precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'

interface SyncEvent extends Event {
  tag: string
  waitUntil(fn: Promise<unknown>): void
}

declare const self: ServiceWorkerGlobalScope & {
  __WB_MANIFEST: Array<{
    revision: string | null
    url: string
  }>
}

clientsClaim()
self.skipWaiting()

precacheAndRoute(self.__WB_MANIFEST)

registerRoute(
  ({ url }) => url.pathname.startsWith('/competencia') || url.pathname.startsWith('/torneos'),
  new NetworkFirst({
    cacheName: 'api-cache',
    networkTimeoutSeconds: 3,
  }),
)

self.addEventListener('sync', (event: Event) => {
  const syncEvent = event as SyncEvent
  if (syncEvent.tag !== 'ataraxia-sync-queue') return

  syncEvent.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        client.postMessage({ type: 'SYNC_QUEUE_REQUEST' })
      }
    }),
  )
})
