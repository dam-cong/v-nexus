import { openDB } from 'idb';

const DB_NAME = 'vnexus-offline';
const DB_VERSION = 1;

const STORES = {
  QUESTIONS: 'questions',
  PLACEMENT_TESTS: 'placementTests',
  TEST_QUESTIONS: 'testQuestions',
  PENDING_RESULTS: 'pendingResults',
  STUDENTS: 'students',
  TEACHERS: 'teachers',
  RANKINGS: 'rankings',
  TEST_RESULTS: 'testResults',
  STUDENT_PROFILES: 'studentProfiles',
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
      if (!db.objectStoreNames.contains(STORES.STUDENTS)) {
        db.createObjectStore(STORES.STUDENTS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.TEACHERS)) {
        db.createObjectStore(STORES.TEACHERS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.RANKINGS)) {
        db.createObjectStore(STORES.RANKINGS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.TEST_RESULTS)) {
        db.createObjectStore(STORES.TEST_RESULTS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.STUDENT_PROFILES)) {
        db.createObjectStore(STORES.STUDENT_PROFILES, { keyPath: 'id' });
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

export async function saveStudents(students) {
  const db = await getDb();
  const tx = db.transaction(STORES.STUDENTS, 'readwrite');
  for (const s of students) await tx.store.put(s);
  await tx.done;
}

export async function saveTeachers(teachers) {
  const db = await getDb();
  const tx = db.transaction(STORES.TEACHERS, 'readwrite');
  for (const t of teachers) await tx.store.put(t);
  await tx.done;
}

export async function saveRankings(rankings) {
  const db = await getDb();
  const tx = db.transaction(STORES.RANKINGS, 'readwrite');
  for (const r of rankings) await tx.store.put(r);
  await tx.done;
}

export async function saveTestResults(results) {
  const db = await getDb();
  const tx = db.transaction(STORES.TEST_RESULTS, 'readwrite');
  for (const r of results) await tx.store.put(r);
  await tx.done;
}

export async function saveStudentProfile(profile) {
  const db = await getDb();
  await db.put(STORES.STUDENT_PROFILES, profile);
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

export async function getStudents() {
  const db = await getDb();
  return db.getAll(STORES.STUDENTS);
}

export async function getTeachers() {
  const db = await getDb();
  return db.getAll(STORES.TEACHERS);
}

export async function getRankings() {
  const db = await getDb();
  return db.getAll(STORES.RANKINGS);
}

export async function getTestResults() {
  const db = await getDb();
  return db.getAll(STORES.TEST_RESULTS);
}

export async function getStudentProfile(userId) {
  const db = await getDb();
  return db.get(STORES.STUDENT_PROFILES, userId);
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

// ── Seed from static /data/ (for offline zip first-run) ─────────────────────

// Trình duyệt/nginx có thể trả về index.html (200 OK) thay vì 404 thật cho
// đường dẫn tĩnh không tồn tại (SPA fallback catch-all). Không được tin
// `res.ok` một mình — phải xác nhận content-type là JSON thật trước khi parse,
// nếu không `.json()` sẽ throw SyntaxError khó hiểu (đã gặp trong production).
async function safeJsonOrNull(res, label) {
  if (!res.ok) {
    console.warn(`[offline] ${label}: HTTP ${res.status}`);
    return null;
  }
  const contentType = res.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    console.warn(`[offline] ${label}: không phải JSON (content-type: ${contentType || 'unknown'}) — có thể do server trả về index.html thay vì file tĩnh chưa được sinh ra.`);
    return null;
  }
  try {
    return await res.json();
  } catch (e) {
    console.warn(`[offline] ${label}: JSON parse lỗi`, e);
    return null;
  }
}

export async function seedFromStaticData() {
  const db = await getDb();
  // Check if any data exists to prevent re-seeding
  const studentCount = await db.count(STORES.STUDENTS);
  if (studentCount > 0) return false;

  try {
    const [qRes, ptRes, sRes, tRes, rRes, trRes] = await Promise.all([
      fetch('/data/questions.json'),
      fetch('/data/placement-tests.json'),
      fetch('/data/students.json'),
      fetch('/data/teachers.json'),
      fetch('/data/rankings.json'),
      fetch('/data/test-results.json'),
    ]);

    const [questions, tests, students, teachers, rankings, testResults] = await Promise.all([
      safeJsonOrNull(qRes, 'questions.json'),
      safeJsonOrNull(ptRes, 'placement-tests.json'),
      safeJsonOrNull(sRes, 'students.json'),
      safeJsonOrNull(tRes, 'teachers.json'),
      safeJsonOrNull(rRes, 'rankings.json'),
      safeJsonOrNull(trRes, 'test-results.json'),
    ]);

    if (!questions || !tests || !students || !teachers || !rankings || !testResults) {
      console.error('[offline] Thiếu dữ liệu tĩnh để seed offline — bỏ qua, app vẫn chạy được nhưng chưa có dữ liệu offline sẵn.');
      return false;
    }

    // Seed Questions
    const txQ = db.transaction(STORES.QUESTIONS, 'readwrite');
    for (const q of questions) await txQ.store.put(q);
    await txQ.done;

    // Seed Placement Tests
    const txPT = db.transaction(STORES.PLACEMENT_TESTS, 'readwrite');
    for (const t of tests) await txPT.store.put(t);
    await txPT.done;

    // Seed Test Questions per Test
    for (const t of tests) {
      try {
        const tqRes = await fetch(`/data/test-questions/${t.id}.json`);
        if (tqRes.ok) {
          const tqData = await tqRes.json();
          const txTQ = db.transaction(STORES.TEST_QUESTIONS, 'readwrite');
          await txTQ.store.put({ id: t.id, questions: tqData });
          await txTQ.done;
        }
      } catch (_) { /* skip if file missing */ }
    }

    // Seed Dashboard Data
    const txS = db.transaction(STORES.STUDENTS, 'readwrite');
    for (const s of students) await txS.store.put(s);
    await txS.done;

    const txT = db.transaction(STORES.TEACHERS, 'readwrite');
    for (const t of teachers) await txT.store.put(t);
    await txT.done;

    const txR = db.transaction(STORES.RANKINGS, 'readwrite');
    for (const r of rankings) await txR.store.put(r);
    await txR.done;

    const txTR = db.transaction(STORES.TEST_RESULTS, 'readwrite');
    for (const tr of testResults) await txTR.store.put(tr);
    await txTR.done;

    return true;
  } catch (e) {
    console.error('Error during static data seeding:', e);
    return false;
  }
}

export { STORES };
