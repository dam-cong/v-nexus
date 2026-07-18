# Kế hoạch: Offline Mode PoC — Hệ thống hoạt động khi mất mạng

> Kế hoạch triển khai đầy đủ 4 mảng. Cập nhật 2026-07-18. Dùng `vite-plugin-pwa` (generateSW).
> **Phương án A đã chốt**: Dockerfile chạy production build + `vite preview`.

## Bối cảnh

Thiết bị học sinh không có bất kỳ kết nối mạng nào (kể cả LAN). Web app hiện tại hoàn toàn
phụ thuộc server: mọi tính toán (BKT, câu hỏi, kết quả) đều qua network call. **0% offline
đã được hiện thực hóa** (không SW, không PWA manifest, không IndexedDB).

## Tổng quan 4 mảng

| Mảng | Nội dung | Files mới/chính | Trạng thái |
|---|---|---|---|
| 0 | Chuẩn bị: relative API, self-host fonts, proxy | `api.js`, `AuthContext.jsx`, `vite.config.js`, `index.html` | ✅ |
| 1 | Port BKT engine sang JS chạy tại chỗ | `offline/bkt.js` | ✅ |
| 2 | Nút "Tải app" + SW precache app shell | `vite-plugin-pwa` + `App.jsx` | ✅ |
| 3 | IndexedDB + đánh dấu "chưa đồng bộ" | `offline/db.js` | ✅ |
| 4 | Nhãn "Offline" trên Header + toast khi click online features | `offline/useOnlineStatus.js` | ✅ |
| 5 | **PWA Production Build** — Dockerfile + preview proxy + icons | `Dockerfile`, `vite.config.js`, `public/icons/` | ✅ |

## Mảng 0 — Chuẩn bị (tiền đề bắt buộc)

### 0a. Relative API base
- `api.js:1`: `API_BASE = "http://localhost:8000"` → `import.meta.env.VITE_API_BASE || ""`
- `AuthContext.jsx:14`: login URL → `${import.meta.env.VITE_API_BASE || ""}/api/auth/login`
- SW chỉ intercept được relative path; hardcoded `localhost:8000` sẽ fail offline.

### 0b. Vite proxy (dev + preview)
- `vite.config.js`: thêm `server.proxy` + `preview.proxy` (cả hai đều proxy `/api` → gateway).
- `vite.config.js`: thêm `define: { 'import.meta.env.VITE_API_BASE': JSON.stringify('') }`
- Tạo `.env` với `VITE_API_BASE=` (relative) cho prod.
- **Quan trọng**: `server.proxy` chỉ hoạt động ở dev; `preview.proxy` cần riêng cho production preview.

### 0c. Self-host Google Fonts
- Tải Outfit + Material Symbols về `public/fonts/`.
- Đổi 2 thẻ `<link>` trong `index.html:7-8` sang local `fonts/`.
- Tránh request treo khi mất mạng hoàn toàn.

## Mảng 1 — Port BKT engine sang JS

### Mới: `frontend/src/offline/bkt.js`
- Port `SKILLS` (16 entries) + `PREREQUISITES` (15 entries) từ `knowledge_graph.py:20-64`.
- Port helpers: `get_skill_name`, `get_prerequisites`, `has_skill`, `trace_root_causes`.
- Port BKT constants: `PRIOR=0.3`, `TRANSIT=0.3`, `GUESS=0.2`, `SLIP=0.1`.
- Port `THRESHOLD_MASTERED=0.7`, `THRESHOLD_DEVELOPING=0.45`, `ROOT_THRESHOLD=0.5`.
- Port `_status`, `update_probability`, `compute_mastery`, `diagnose_gaps`, `run_assessment`.
- Port `generate_learning_steps` + offline `training_plan` fallback (theo `_offline_fallback_student`).
- **Giữ nguyên logic 1:1** — pure math, không I/O, ~150 dòng.

### Thay đổi `StudentSurvey.jsx`
- `computeResult` (69-141): thay ratio-based bằng `run_assessment(answers)` từ `bkt.js`.
- Khi offline, nút "Xem lộ trình" dùng fallback JS (không cần LLM).

## Mảng 2 — Nút "Tải app" (SW precache)

### Cài đặt PWA
- `package.json`: + `vite-plugin-pwa`, `idb`
- `vite.config.js`: thêm `VitePWA({ registerType: 'autoUpdate', ... })` precache app shell.

### Nút "Tải app" (`App.jsx:872-875`)
- Thêm icon `Download` trong `.icon-buttons` (chỉ render khi role học sinh).
- Luồng bấm:
  1. Fetch `/api/questions`, `/api/placement-tests`, `/api/placement-tests/{id}/questions`
  2. Ghi IndexedDB (dùng `db.js` ở Mảng 3)
  3. Hiển thị tiến trình (`.survey-progress-bar`) + toast `triggerNotification`
  4. Lưu `localStorage.vnexus_offline_ready` + timestamp

## Mảng 3 — IndexedDB + "chưa đồng bộ"

### Mới: `frontend/src/offline/db.js`
- IndexedDB wrapper qua `idb`: stores `questions`, `placementTests`, `testQuestions`, `pendingResults`.

### Thay đổi
- `useQuestions` (StudentSurvey.jsx:143) + `fetchQuestions` (App.jsx:246):
  offline → đọc IndexedDB.
- `handleSubmit` (StudentSurvey.jsx:824): offline → lưu `pendingResults` + nhãn "chưa đồng bộ".
  Có mạng → tự POST retry.
- `StudentHistory.jsx`: hiển thị nhãn "chưa đồng bộ" cho results chưa sync.

## Mảng 4 — Nhãn "Offline" (đơn giản)

### Mới: `frontend/src/offline/useOnlineStatus.js`
- `navigator.onLine` + listen `online`/`offline` events.
- Return `{ isOnline }`.

### Thay đổi `App.jsx`
- Import `useOnlineStatus` + icon `WifiOff` từ lucide-react.
- Hiển thị badge "Offline" trên Header khi `!isOnline`.
- **Không ẩn** tính năng nào — vẫn hiển thị bình thường.
- Khi click tính năng cần mạng (submit/sync/API) mà offline:
  → `triggerNotification("Hệ thống đang offline, vui lòng kết nối mạng", "error")`

## Mảng 5 — PWA Production Build (Phương án A) ✅

### Vấn đề
`vite-plugin-pwa` **chỉ sinh `sw.js` ở production build** (`vite build`).
Dockerfile cũ chạy `npm run dev` → không có SW → app không offline được.

### Giải pháp: Đổi sang production build trong Docker

**Dockerfile** (đã cập nhật):
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build          # sinh dist/ + sw.js + manifest.webmanifest
EXPOSE 8501
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "8501"]
```

**vite.config.js** (đã cập nhật):
```js
preview: {
  port: 8501,
  host: '0.0.0.0',
  proxy: {
    '/api': {
      target: process.env.GATEWAY_URL || 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

**Icon PNG** (đã tạo):
- `frontend/public/icons/icon-192.png` (192×192)
- `frontend/public/icons/icon-512.png` (512×512)
- `manifest.icons` cập nhật: thêm PNG icons ngoài SVG favicon.

### Rủi ro / lưu ý
- SW chỉ register trên **localhost hoặc HTTPS**. Nếu demo qua IP LAN (http), SW không hoạt động.
  → Cần truy cập `localhost:8081` hoặc domain HTTPS.
- Mỗi lần sửa frontend phải `docker compose up -d --build frontend` (vì build trong image).
- `vite preview` không live-reload — phải rebuild để thấy thay đổi.

## Files thay đổi (tổng hợp)

| File | Thay đổi | Trạng thái |
|---|---|---|
| `frontend/package.json` | + `vite-plugin-pwa`, `idb` | ✅ |
| `frontend/vite.config.js` | + PWA plugin + server.proxy + preview.proxy + icons | ✅ |
| `frontend/Dockerfile` | build production + `vite preview` | ✅ |
| `frontend/index.html` | self-host fonts | ✅ |
| `frontend/public/icons/icon-192.png` | PWA icon 192×192 | ✅ |
| `frontend/public/icons/icon-512.png` | PWA icon 512×512 | ✅ |
| `frontend/src/api.js` | relative base | ✅ |
| `frontend/src/context/AuthContext.jsx` | relative login URL | ✅ |
| `frontend/src/App.jsx` | nút Tải app, badge Offline | ✅ |
| `frontend/src/StudentSurvey.jsx` | dùng `bkt.js`, submit queue, offline plan | ✅ |
| `frontend/src/offline/bkt.js` | **MỚI** — BKT engine JS | ✅ |
| `frontend/src/offline/db.js` | **MỚI** — IndexedDB wrapper | ✅ |
| `frontend/src/offline/useOnlineStatus.js` | **MỚI** — online/offline hook | ✅ |

## Mảng 6 — Live-site sống sót offline (chốt 2026-07-18)

> Website live (`localhost:8081`) hoạt động khi mất mạng: reload vẫn mở, tắt máy bật lại vẫn dùng.
> **Bỏ zip download** — tập trung vào live-site offline.
> Login offline = tài khoản học sinh demo; đã login trước đó → giữ nguyên phiên.

### 6a. Bảo vệ token — `api.js`
- `apiFetch`: nếu `!navigator.onLine` → throw `OfflineError` ngay (không gọi network).
- Online gặp 401 → giữ `removeToken()` + reload (như cũ).
- Không xóa token khi gặp response HTML (SW trả cache lỗi).

### 6b. Auth offline — `AuthContext.jsx` + `Login.jsx`
- `AuthContext`: thêm `loginOfflineDemo()` → set user học sinh demo `{id:0, name:'Học sinh', email:'offline@vnexus.vn', role:'hoc_sinh'}` + token giả vào localStorage.
- `Login.jsx`: khi `!navigator.onLine` → hiện nút **"Dùng offline (học sinh)"** gọi `loginOfflineDemo()`.
- Session cũ: `getUser()/getToken()` restore từ localStorage → reload/máy restart giữ nguyên phiên.

### 6c. Seed IndexedDB từ `/data` — `db.js` + `App.jsx` + `StudentSurvey.jsx`
- `seedFromStaticData()` (đã có ở `db.js:110`) fetch `/data/questions.json`, `/data/placement-tests.json`, `/data/test-questions/{id}.json` → save IndexedDB.
- `App.jsx`: gọi `seedFromStaticData()` trong `useEffect` mount → nếu seeded → fetch lại questions/placement tests.
- `StudentSurvey.jsx`: gọi `seedFromStaticData()` khi mount offline trước khi đọc IndexedDB.
- `/data/*.json` được sinh bởi `export-offline-data.cjs` khi container start (login admin → query API).

### 6d. Offline fallback cho data hiển thị — `App.jsx`
- `fetchStudents/Teachers/AllUsers/Rankings/TestResults/StudentProfile`: khi offline → catch `OfflineError` → state giữ nguyên (mảng rỗng). Với user học sinh demo, dashboard vẫn chạy nhờ IndexedDB + BKT.
- `fetchQuestions/fetchPlacementTests`: đã có fallback offline (lines 266-298). Đảm bảo seed trước.

### 6e. Xóa zip download
- Xóa nút "Tải app" (Download button) + `handleDownloadApp` + `offlineReady` state.
- Xóa `public/start.sh`, `public/start.bat`, `public/README.txt`.
- `start-offline.sh`: chỉ export data + preview (không zip).
- `Dockerfile`: giữ obfuscation + export, bỏ zip.

### 6f. Mã hóa code — `javascript-obfuscator` (giữ)
- `obfuscator.config.cjs`: RC4 string encoding + mangled-shuffled identifiers.
- Sau `vite build`, chạy `javascript-obfuscator` trên `dist/assets/*.js`.
- Kết quả: app logic bị obfuscate; React library names vẫn visible (không tránh được).

## Files thay đổi (tổng hợp)

| File | Thay đổi | Trạng thái |
|---|---|---|
| `frontend/package.json` | + `vite-plugin-pwa`, `idb`, `javascript-obfuscator` | ✅ |
| `frontend/vite.config.js` | + PWA plugin + server.proxy + preview.proxy + icons | ✅ |
| `frontend/Dockerfile` | build → obfuscate → export data → preview | ✅ |
| `frontend/start-offline.sh` | entrypoint: export data + preview | ✅ |
| `frontend/obfuscator.config.cjs` | **MỚI** — config obfuscation | ✅ |
| `frontend/scripts/export-offline-data.cjs` | **MỚI** — login admin → export → dist/data/ | ✅ |
| `frontend/index.html` | self-host fonts | ✅ |
| `frontend/public/icons/icon-192.png` | PWA icon 192×192 | ✅ |
| `frontend/public/icons/icon-512.png` | PWA icon 512×512 | ✅ |
| `frontend/src/api.js` | OfflineError + offline guard | ✅ |
| `frontend/src/context/AuthContext.jsx` | + loginOfflineDemo() | ✅ |
| `frontend/src/pages/Login.jsx` | nút "Dùng offline" khi mất mạng | ✅ |
| `frontend/src/App.jsx` | xóa Tải app; seed /data; fallback offline; gate Login | ✅ |
| `frontend/src/StudentSurvey.jsx` | seedFromStaticData khi mount offline | ✅ |
| `frontend/src/offline/bkt.js` | **MỚI** — BKT engine JS | ✅ |
| `frontend/src/offline/db.js` | **MỚI** — IndexedDB + seedFromStaticData | ✅ |
| `frontend/src/offline/useOnlineStatus.js` | **MỚI** — online/offline hook | ✅ |

## Không làm trong hackathon
- Đồng bộ hai chiều an toàn (xung đột, retry phức tạp).
- Offline cho admin/dashboard giáo viên.
- Model LLM cục bộ.
- Mã hóa runtime (browser JS không thể mã hóa thật sự — chỉ obfuscate).

## Kiểm tra (sau rebuild)
1. `docker compose up -d --build frontend`
2. Login bình thường (online) → reload → vẫn vào được.
3. **Tắt mạng** → reload → app vẫn mở (SW precache), badge "Offline", vào được Dashboard.
4. Logout → tắt mạng → Login hiện nút "Dùng offline" → bấm → vào được bằng học sinh demo.
5. Làm bài khảo sát offline → BKT chạy từ JS, data từ IndexedDB (seeded từ `/data`).
6. Tắt máy → bật lại → mở `localhost:8081` (offline) → vẫn dùng được.

## Kiểm tra (sau rebuild)
1. `docker compose up -d --build frontend`
2. Truy cập `http://localhost:8081` (SW cần secure context: localhost hoặc HTTPS).
3. DevTools → Application → Service Workers: thấy `sw.js` **active/running**, `manifest` hợp lệ.
4. Bấm "Tải app" → toast "Đã tải xong", badge xanh.
5. **Tắt hẳn WiFi/LAN**, reload trình duyệt → app vẫn mở được (SW cache). Header hiện "Offline".
6. Làm bài khảo sát offline → mastery/gaps/lộ trình tính bằng JS (BKT), kết quả lưu IndexedDB.
7. Bật mạng lại → badge "Online" hiện lại.
