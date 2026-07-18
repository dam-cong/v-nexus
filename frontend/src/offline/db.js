import { openDB } from 'idb';

const DB_NAME = 'vnexus-offline';
const DB_VERSION = 1;

const STORES = {
  QUESTIONS: 'questions',
  PLACEMENT_TESTS: 'placementTests',
  TEST_QUESTIONS: 'testQuestions',
  PENDING_RESULTS: 'pendingResults',
};

async function getDb() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORES.QUESTIONS)) {
        db.createObjectStore(STORES.QUESTIONS, { keyPath: 'question_id' });
      }
      if (!db.objectStoreNames.contains(STORES.PLACEMENT_TESTS)) {
        db.createObjectStore(STORES.PLACEMENT_TESTS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.TEST_QUESTIONS)) {
        db.createObjectStore(STORES.TEST_QUESTIONS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.PENDING_RESULTS)) {
        db.createObjectStore(STORES.PENDING_RESULTS, { keyPath: 'id', autoIncrement: true });
      }
    },
  });
}

// ── Save data ───────────────────────────────────────────────────────────────

export async function saveQuestions(questions) {
  const db = await getDb();
  const tx = db.transaction(STORES.QUESTIONS, 'readwrite');
  for (const q of questions) await tx.store.put(q);
  await tx.done;
}

export async function savePlacementTests(tests) {
  const db = await getDb();
  const tx = db.transaction(STORES.PLACEMENT_TESTS, 'readwrite');
  for (const t of tests) await tx.store.put(t);
  await tx.done;
}

export async function saveTestQuestions(testId, questions) {
  const db = await getDb();
  const tx = db.transaction(STORES.TEST_QUESTIONS, 'readwrite');
  await tx.store.put({ id: testId, questions });
  await tx.done;
}

export async function savePendingResult(result) {
  const db = await getDb();
  const id = await db.add(STORES.PENDING_RESULTS, {
    ...result,
    synced: false,
    created_at: new Date().toISOString(),
  });
  return id;
}

// ── Read data ───────────────────────────────────────────────────────────────

export async function getQuestions() {
  const db = await getDb();
  return db.getAll(STORES.QUESTIONS);
}

export async function getPlacementTests() {
  const db = await getDb();
  return db.getAll(STORES.PLACEMENT_TESTS);
}

export async function getTestQuestions(testId) {
  const db = await getDb();
  const record = await db.get(STORES.TEST_QUESTIONS, testId);
  return record ? record.questions : [];
}

export async function getPendingResults() {
  const db = await getDb();
  return db.getAll(STORES.PENDING_RESULTS);
}

// ── Mark synced ─────────────────────────────────────────────────────────────

export async function markResultSynced(id) {
  const db = await getDb();
  const record = await db.get(STORES.PENDING_RESULTS, id);
  if (record) {
    record.synced = true;
    await db.put(STORES.PENDING_RESULTS, record);
  }
}

// ── Clear all (for re-download) ─────────────────────────────────────────────

export async function clearOfflineData() {
  const db = await getDb();
  for (const store of Object.values(STORES)) {
    await db.clear(store);
  }
}

export { STORES };
