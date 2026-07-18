# Plan: Tính năng "Lộ trình học cá nhân" (2 đợt)

## Mục tiêu
1. Trang "Lộ trình của em" tổng hợp kế hoạch AI (`training_plan`) từ TẤT CẢ bài đánh giá của học sinh.
2. Mini-test đánh giá nhanh (lọc theo `gaps` bài gần nhất) để đo lại mastery.
3. Lưu DB trạng thái "hoàn thành lộ trình" + hiển thị badge ✓ khi pass đánh giá nhanh.
4. Smart button "Xem lộ trình của em" ở màn Kết quả bài khảo sát.

## Quyết định
- Mini-test: lọc câu theo `gaps` bài gần nhất (option b).
- Tổng hợp lộ trình: danh sách tất cả bài có plan (option b).
- Chia 2 đợt: A = lộ trình tổng hợp + smart button + lưu completed; B = mini-test đánh giá nhanh.

---

## ĐỢT A — Lộ trình tổng hợp + Smart button + lưu hoàn thành

### A1. Backend: trường DB
- `db/models.py` (StudentTestResult): thêm `roadmap_completed`, `quick_check_passed` (Boolean, default False).
- `db/connector.py` (`init_db` ALTER): thêm 2 cột `IF NOT EXISTS`.

### A2. Backend: schema + endpoint mark completed
- `crud.py` `TestResultResponse`: thêm `roadmap_completed`, `quick_check_passed`.
- Endpoint `PATCH /api/test-results/{id}/complete` (body `{ completed: bool }`): cập nhật `roadmap_completed`, trả result.

### A3. Frontend: component `StudentRoadmap.jsx` (mới)
- Prop: `results`, `questions`, `onStartSurvey`.
- Tổng hợp mọi bài có `training_plan` → card (ngày, CEFR, nội dung `.history-training-plan`), badge "Đã hoàn thành ✓" nếu `roadmap_completed`.
- Bài mới nhất nổi bật trên đầu. Rỗng → hướng dẫn làm Khảo sát.

### A4. App.jsx: gắn roadmap
- Thay placeholder bằng `<StudentRoadmap ... />`. Khi vào tab roadmap gọi `fetchStudentTestResults()`.

### A5. Frontend: Smart button ở màn Kết quả
- `StudentSurvey.jsx`: `function StudentSurvey({ user, onTabChange })`.
- Thêm nút "Xem lộ trình của em" gọi `onTabChange?.('roadmap')`.

### A6. CSS + deploy
- Style card lộ trình + badge. Build/up gateway + frontend.

---

## ĐỢT B — Mini-test đánh giá nhanh (lọc theo gaps)

### B1. Backend
- `GET /api/test-results/{id}/quick-check-questions`: lọc `questions` theo `gaps[].skill_id` bài, trả ~5 câu.
- `POST /api/test-results/{id}/quick-check` (body `answers`): chạy BKT → so sánh gaps gốc; nếu mọi gap `probability >= 0.7` → `quick_check_passed` + `roadmap_completed` = True. Trả `{ passed, remaining_gaps, mastery }`.

### B2. Frontend: component `QuickCheck` (trong StudentRoadmap)
- Nút "Đánh giá nhanh" → modal mini-test. Pass → badge ✓; fail → "Cần ôn thêm: ...".

### B3. Deploy + verify

---

## Trạng thái
- [x] Đợt A triển khai
- [ ] Đợt B triển khai
