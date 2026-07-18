# Kế hoạch: Offline Mode PoC — Hệ thống hoạt động khi mất mạng

> Kế hoạch triển khai đầy đủ 4 mảng. Cập nhật 2026-07-18. Dùng `vite-plugin-pwa` (generateSW).

## Bối cảnh

Thiết bị học sinh không có bất kỳ kết nối mạng nào (kể cả LAN). Web app hiện tại hoàn toàn
phụ thuộc server: mọi tính toán (BKT, câu hỏi, kết quả) đều qua network call. **0% offline
đã được hiện thực hóa** (không SW, không PWA manifest, không IndexedDB).

## Tổng quan 4 mảng

| Mảng | Nội dung | Files mới/chính |
|---|---|---|
| 0 | Chuẩn bị: relative API, self-host fonts, proxy | `api.js`, `AuthContext.jsx`, `vite.config.js`, `index.html` |
| 1 | Port BKT engine sang JS chạy tại chỗ | `offline/bkt.js` (MỚI) |
| 2 | Nút "Tải app" + SW precache app shell | `vite-plugin-pwa` + `App.jsx` |
| 3 | IndexedDB + đánh dấu "chưa đồng bộ" | `offline/db.js` (MỚI) |
| 4 | Nhãn "Offline" trên Header + toast khi click online features | `offline/useOnlineStatus.js` (MỚI) |

## Mảng 0 — Chuẩn bị (tiền đề bắt buộc)

### 0a. Relative API base
- `api.js:1`: `API_BASE = "http://localhost:8000"` → `import.meta.env.VITE_API_BASE || ""`
- `AuthContext.jsx:14`: login URL → `${import.meta.env.VITE_API_BASE || ""}/api/auth/login`
- SW chỉ intercept được relative path; hardcoded `localhost:8000` sẽ fail offline.

### 0b. Vite proxy (dev)
- `vite.config.js`: thêm `proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } }`
- `vite.config.js`: thêm `define: { 'import.meta.env.VITE_API_BASE': JSON.stringify('') }`
- Tạo `.env` với `VITE_API_BASE=` (relative) cho prod.

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
  1. `navigator.serviceWorker.ready`
  2. Fetch `/api/questions`, `/api/placement-tests`, `/api/placement-tests/{id}/questions`
  3. Ghi IndexedDB (dùng `db.js` ở Mảng 3)
  4. Hiển thị tiến trình (`.survey-progress-bar`) + toast `triggerNotification`
  5. Lưu `localStorage.vnexus_offline_ready` + timestamp

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
- Triển khai bằng wrapper `requireOnline(isOnline, fn)` bọc các apiFetch/submit calls.

## Files thay đổi

| File | Thay đổi |
|---|---|
| `frontend/package.json` | + `vite-plugin-pwa`, `idb` |
| `frontend/vite.config.js` | + PWA plugin + proxy |
| `frontend/index.html` | self-host fonts |
| `frontend/src/api.js` | relative base |
| `frontend/src/context/AuthContext.jsx` | relative login URL |
| `frontend/src/App.jsx` | nút Tải app, badge Offline, bọc API calls |
| `frontend/src/StudentSurvey.jsx` | dùng `bkt.js`, submit queue, offline plan |
| `frontend/src/StudentHistory.jsx` | nhãn "chưa đồng bộ" |
| `frontend/src/offline/bkt.js` | **MỚI** |
| `frontend/src/offline/db.js` | **MỚI** |
| `frontend/src/offline/useOnlineStatus.js` | **MỚI** |

## Không làm trong hackathon
- Đồng bộ hai chiều an toàn (xung đột, retry phức tạp).
- PWA install prompt/icon hoàn chỉnh.
- Offline cho admin/dashboard giáo viên.
- Model LLM cục bộ.

## Kiểm tra
1. Bấm "Tải app" có mạng → thanh tiến trình + toast + đổi trạng thái.
2. Tắt mạng → mở lại app → shell mở được. Header hiện "Offline".
3. Làm bài offline → mastery/gaps/lộ trình hiện đúng (JS). Kết quả gắn "chưa đồng bộ".
4. Click tính năng online offline → toast "Hệ thống đang offline...".
5. Bật mạng → pending tự đồng bộ. Badge Offline biến mất.
