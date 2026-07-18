import { apiFetch } from '../api';
import { getPendingResults, markResultSynced } from './db';

export async function flushPendingResults() {
  const pending = await getPendingResults();
  let syncedCount = 0;

  for (const item of pending) {
    if (item.synced) continue; // Skip already synced items
    try {
      const res = await apiFetch(item.endpoint, {
        method: item.method,
        headers: { 'Content-Type': 'application/json' },
        body: item.body,
      });
      if (res.ok) {
        await markResultSynced(item.id);
        syncedCount++;
      }
    } catch (e) {
      console.warn(`[Offline Sync] Failed to sync ${item.kind || 'item'} ${item.id}:`, e);
      // Keep in queue for next attempt
    }
  }

  return syncedCount;
}
