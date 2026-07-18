const fs = require('fs');
const path = require('path');

const GATEWAY = process.env.GATEWAY_URL || 'http://gateway:8000';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'admin@vnexus.vn';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '123456';
const DIST_DIR = path.join(__dirname, '..', 'dist');

let TOKEN = null;

async function login() {
  const res = await fetch(`${GATEWAY}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: ADMIN_EMAIL, password: ADMIN_PASSWORD }),
  });
  if (!res.ok) throw new Error(`Login failed: HTTP ${res.status}`);
  const data = await res.json();
  TOKEN = data.access_token;
  console.log(`  Logged in as ${data.user.email} (${data.user.role})`);
}

async function fetchJSON(url) {
  const headers = TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {};
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`HTTP ${res.status} from ${url}`);
  return res.json();
}

async function main() {
  const dataDir = path.join(DIST_DIR, 'data');
  fs.mkdirSync(dataDir, { recursive: true });

  console.log(`Exporting offline data from ${GATEWAY}...`);

  await login();

  // 1. Questions
  const questions = await fetchJSON(`${GATEWAY}/api/questions`);
  fs.writeFileSync(path.join(dataDir, 'questions.json'), JSON.stringify(questions));
  console.log(`  questions.json: ${questions.length} items`);

  // 2. Placement tests
  const tests = await fetchJSON(`${GATEWAY}/api/placement-tests`);
  fs.writeFileSync(path.join(dataDir, 'placement-tests.json'), JSON.stringify(tests));
  console.log(`  placement-tests.json: ${tests.length} items`);

  // 3. Test questions per test
  const tqDir = path.join(dataDir, 'test-questions');
  fs.mkdirSync(tqDir, { recursive: true });
  for (const test of tests) {
    try {
      const tq = await fetchJSON(`${GATEWAY}/api/placement-tests/${test.id}/questions`);
      fs.writeFileSync(path.join(tqDir, `${test.id}.json`), JSON.stringify(tq));
      console.log(`  test-questions/${test.id}.json: ${Array.isArray(tq) ? tq.length : 'obj'}`);
    } catch (e) {
      console.warn(`  test-questions/${test.id}.json: SKIP (${e.message})`);
    }
  }

  console.log('Offline data export done.');
}

main().catch(e => {
  console.error('Export failed:', e.message);
  process.exit(1);
});
