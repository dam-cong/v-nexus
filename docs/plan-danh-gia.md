# Plan Triển khai Chức năng Đánh giá

## Flow tổng thể (7 bước từ mockup)

```
code-01: Trang chào Welcome
    ↓ "Bắt đầu khảo sát"
code-02: Chọn cấp độ (Pre-A1 / A1 / A2)
    ↓ "Tiếp tục"
code-03: Hướng dẫn (4 bước làm bài)
    ↓ "Vào làm bài"
code-05: Làm bài (câu hỏi + chọn đáp án + navigator)
    ↓ Chọn đáp án
code-04: Trả lời đúng → Feedback xanh
code-06: Trả lời sai → Feedback đỏ + giải thích
    ↓ "Tiếp tục" qua 14 câu
code-07: Kiểm tra lại + Nộp bài
    ↓ "Nộp bài"
Kết quả (điểm, mastery, gaps, recommendations)
```

## Files thay đổi

| File | Thay đổi |
|------|----------|
| `frontend/src/App.jsx` | Thêm sidebar cho học sinh + 7 screen components + state management |
| `frontend/src/App.css` | Thêm CSS cho các screen mới |

## Chi tiết từng screen

### Screen 1: SurveyLanding (code-01)
- Hero card với mascot Medi Bee
- Info grid 4 cards: 14 câu hỏi, Đọc & Nghe, 10-15 phút, Lưu bài tự động
- Notes: "Đây không phải là cuộc thi" + "Bài làm được lưu nếu mất kết nối"
- Buttons: "Bắt đầu khảo sát" + "Xem hướng dẫn"

### Screen 2: SurveyLevelSelect (code-02)
- Stepper 4 bước
- 3 level cards: Pre-A1, A1, A2
- Buttons: "Quay lại" + "Tiếp tục"

### Screen 3: SurveyInstructions (code-03)
- 4 steps: Đọc/nghe → Chọn đáp án → Kiểm tra → Đọc giải thích
- Audio guide card
- Status card: "Bài làm được lưu tự động"
- Button: "Vào làm bài"

### Screen 4: SurveyTestTaking (code-04/05/06)
- Stepper: Thông tin → Làm bài → Kết quả
- Progress bar + question counter
- Question card + options grid
- Question navigator grid (14 ô)
- Action buttons: "Đánh dấu xem lại" + "Kiểm tra đáp án"
- Feedback panel: đúng (xanh) / sai (đỏ)

### Screen 5: SurveyReview (code-07)
- Warning banner (nếu còn câu chưa trả lời)
- Summary grid: Đã trả lời, Chưa trả lời, Xem lại
- Question navigator grid
- Legend
- Confirmation dialog: "Nộp bài ngay?"
- Buttons: "Quay lại làm bài" + "Nộp bài"

### Screen 6: SurveyResults
- Summary cards: Điểm, Tỷ lệ, CEFR, Thời gian
- Mastery bars theo skill
- Gaps list
- Recommendations list

## Data từ DB

### 14 câu hỏi (placement_test_en_2026)
| question_id | skill_name | difficulty | prompt |
|-------------|------------|------------|--------|
| qb_001 | Present Simple vs Continuous | easy | I ___ to school every day. |
| qb_004 | Adverbs of Frequency | easy | I ___ brush my teeth before bed. |
| qb_007 | To Be (Present and Past) | easy | They ___ happy yesterday. |
| qb_040 | School Vocabulary | easy | What subject do you study with numbers? |
| qb_041 | Places Around Town | easy | Where do you go to borrow books? |
| qb_010 | Some/Any | easy | I have ___ apples in my bag. |
| qb_014 | Past Simple Regular | medium | She ___ (play) piano at the concert yesterday. |
| qb_016 | Comparatives | easy | An elephant is ___ than a mouse. |
| qb_023 | There Was/Were | medium | There ___ many students in the classroom yesterday. |
| qb_042 | Food and Tableware | easy | Which one is a vegetable? |
| qb_019 | Past Simple Irregular | easy | Yesterday I ___ to the zoo. |
| qb_032 | Past Simple Questions | medium | Where ___ she ___ (live) before she moved here? |
| qb_034 | Verbs with To + Infinitive | easy | I want ___ (go) to the park. |
| qb_038 | Must/Mustn't | medium | We ___ be quiet in the library. |

### Level mapping
- 0-29% → starter (Pre-A1)
- 30-59% → beginner (A1)
- 60-100% → elementary (A2)

### State management
```javascript
const [survey, setSurvey] = useState({
  screen: 'landing',
  selectedLevel: null,
  currentQuestion: 0,
  answers: {},
  marked: new Set(),
  showFeedback: false,
  lastCorrect: null,
  startTime: null,
  questions: [],
  result: null,
});
```

## Thứ tự triển khai

| # | Bước | Priority |
|---|------|----------|
| 1 | State management + Sidebar cho học sinh | HIGH |
| 2 | SurveyLanding (code-01) | HIGH |
| 3 | SurveyLevelSelect (code-02) | HIGH |
| 4 | SurveyInstructions (code-03) | HIGH |
| 5 | SurveyTestTaking (code-04/05/06) | HIGH |
| 6 | SurveyReview (code-07) | HIGH |
| 7 | SurveyResults | HIGH |
| 8 | CSS responsive + animations | HIGH |
| 9 | Load data từ API | HIGH |
