import React, { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle, Bookmark, ListOrdered, Mic, Clock, Cloud, Info, WifiOff,
  ArrowRight, ListTodo, Volume2, RefreshCw, XCircle, Star, AlertTriangle,
  Flag, Send, CircleHelp, CheckCheck, Lightbulb, RotateCcw, Smile,
  GraduationCap, BookOpen, Sparkles
} from 'lucide-react';
import { apiFetch } from './api';
import './StudentSurvey.css';

const ICON_MAP = {
  check_circle: CheckCircle,
  bookmark: Bookmark,
  format_list_numbered: ListOrdered,
  record_voice_over: Mic,
  timer: Clock,
  cloud_done: Cloud,
  info: Info,
  wifi_off: WifiOff,
  arrow_forward: ArrowRight,
  list_alt: ListTodo,
  volume_up: Volume2,
  cloud_sync: RefreshCw,
  cancel: XCircle,
  star: Star,
  error: AlertTriangle,
  flag: Flag,
  send: Send,
  help_outline: CircleHelp,
  task_alt: CheckCheck,
  lightbulb: Lightbulb,
  replay: RotateCcw,
  sentiment_satisfied: Smile,
  school: GraduationCap,
  import_contacts: BookOpen,
  sparkles: Sparkles,
};

function Icon({ name, size = 24, className = '', style = {} }) {
  const Comp = ICON_MAP[name];
  if (!Comp) return null;
  return <Comp size={size} className={className} style={style} />;
}

const LEVELS = [
  { id: 'starter', label: 'Mới bắt đầu', cefr: 'Pre-A1', icon: 'sentiment_satisfied', desc: 'Em mới làm quen với Tiếng Anh. Bắt đầu từ những từ vựng cơ bản nhất.' },
  { id: 'beginner', label: 'Cơ bản', cefr: 'A1', icon: 'school', desc: 'Em đã biết một số từ vựng và câu đơn giản quen thuộc.' },
  { id: 'elementary', label: 'Sơ cấp', cefr: 'A2', icon: 'import_contacts', desc: 'Em sử dụng được ngữ pháp cơ bản và giao tiếp trong các tình huống quen thuộc.' },
];

const SKILL_LABELS = {
  'as3.u1.l3': 'Present Simple vs Present Continuous',
  'as3.u2.l3': 'Adverbs of Frequency',
  'as3.u3.l3': 'To Be (Present and Past)',
  'as3.u4.l3': 'Some/Any with Countable/Uncountable Nouns',
  'as3.u5.l3': 'Past Simple Regular Verbs',
  'as3.u6.l3': 'Comparatives',
  'as3.u7.l3': 'Past Simple Irregular Verbs',
  'as3.u8.l3': 'There Was / There Were',
  'as3.u1.l1': 'School Vocabulary',
  'as3.u3.l1': 'Places Around Town',
  'as3.u4.l1': 'Food and Tableware',
  'as4.u1.l3': 'Past Simple Question Forms',
  'as4.u2.l3': 'Verbs with To + Infinitive',
  'as4.u3.l3': 'Must / Mustn\'t',
};

function computeResult(answers, questions) {
  let score = 0;
  const answersArr = [];
  const mastery = {};

  questions.forEach(q => {
    const skillId = q.skill_id;
    if (!skillId) return;
    if (!mastery[skillId]) {
      mastery[skillId] = { probability: 0.5, correct: 0, total: 0, skill_name: q.skill_name || SKILL_LABELS[skillId] || skillId };
    }
    mastery[skillId].total += 1;
  });

  questions.forEach(q => {
    const selected = answers[q.question_id] || null;
    const correct = selected === q.correct_option_id;
    if (correct) score += 1;

    const skillId = q.skill_id;
    if (mastery[skillId]) {
      mastery[skillId].correct += 1;
      mastery[skillId].probability = mastery[skillId].correct / mastery[skillId].total;
    }

    const opt = q.options?.find(o => o.option_id === selected);
    answersArr.push({
      question_id: q.question_id,
      selected: selected || '',
      correct,
      skill_id: skillId,
      time_spent_sec: Math.floor(Math.random() * 15) + 5,
      error_tag: correct ? null : opt?.error_tag || null,
    });
  });

  const maxScore = questions.length;
  const percentage = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;
  let resultLevel = 'starter';
  let cefr = 'Pre-A1';
  if (percentage >= 60) { resultLevel = 'elementary'; cefr = 'A2'; }
  else if (percentage >= 30) { resultLevel = 'beginner'; cefr = 'A1'; }

  Object.keys(mastery).forEach(k => {
    const m = mastery[k];
    if (m.probability >= 0.7) m.status = 'mastered';
    else if (m.probability >= 0.3) m.status = 'developing';
    else m.status = 'weak';
  });

  const gaps = Object.entries(mastery)
    .filter(([, m]) => m.probability < 0.3)
    .map(([skillId, m]) => ({
      skill_id: skillId,
      severity: m.probability < 0.15 ? 'high' : 'medium',
      reason: `Chưa nắm vững ${m.skill_name}`,
    }));

  const recommendations = Object.entries(mastery)
    .filter(([, m]) => m.probability < 0.7)
    .map(([skillId, m]) => ({
      skill_id: skillId,
      action: `Luyện tập ${m.skill_name}`,
      priority: m.probability < 0.3 ? 'high' : 'low',
    }));

  return {
    score, max_score: maxScore, percentage, result_level: resultLevel, cefr,
    time_total_sec: answersArr.reduce((s, a) => s + a.time_spent_sec, 0),
    mastery, gaps, recommendations, training_plan: null, answers: answersArr,
    test_date: new Date().toISOString(),
  };
}

function useQuestions() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiFetch('/api/questions');
        if (res.ok) {
          const all = await res.json();
          const testQRes = await apiFetch('/api/placement-tests');
          let testQuestionIds = [];
          if (testQRes.ok) {
            const tests = await testQRes.json();
            const test = tests.find(t => t.test_id === 'placement-test-en-2026');
            if (test) {
              const tqRes = await apiFetch(`/api/placement-tests/${test.id}/questions`);
              if (tqRes.ok) {
                const tqData = await tqRes.json();
                testQuestionIds = tqData.map(q => q.question_id);
              }
            }
          }
          const filtered = testQuestionIds.length > 0
            ? all.filter(q => testQuestionIds.includes(q.question_id))
            : all.slice(0, 14);
          setQuestions(filtered);
        }
      } catch (e) {
        console.error('Error loading questions:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return { questions, loading };
}

function StepIndicator({ currentStep }) {
  const steps = ['Chọn cấp độ', 'Làm bài', 'Kết quả'];
  return (
    <div className="survey-stepper">
      {steps.map((label, i) => (
        <React.Fragment key={i}>
          {i > 0 && <div className={`survey-stepper-line ${i <= currentStep ? 'active' : ''}`} />}
          <div className="survey-stepper-step">
            <div className={`survey-stepper-circle ${i <= currentStep ? 'active' : ''}`}>
              {i < currentStep ? <Icon name="check_circle" size={16} /> : i + 1}
            </div>
            <span className={`survey-stepper-label ${i <= currentStep ? 'active' : ''}`}>{label}</span>
          </div>
        </React.Fragment>
      ))}
    </div>
  );
}

function ProgressBar({ current, total }) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;
  return (
    <div className="survey-progress">
      <div className="survey-progress-header">
        <span className="survey-progress-label">Câu {current}/{total}</span>
        <span className="survey-progress-pct">{pct}%</span>
      </div>
      <div className="survey-progress-bar">
        <div className="survey-progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function QuestionNavigator({ questions, answers, currentIdx, marked, onJump }) {
  return (
    <div className="survey-navigator">
      <h4 className="survey-navigator-title">Danh sách câu hỏi</h4>
      <div className="survey-navigator-grid">
        {questions.map((q, i) => {
          const answered = !!answers[q.question_id];
          const isCurrent = i === currentIdx;
          const isMarked = marked.has(q.question_id);
          let cls = 'survey-nav-item';
          if (isCurrent) cls += ' current';
          else if (answered) cls += ' answered';
          else cls += ' unanswered';
          if (isMarked) cls += ' marked';
          return (
            <button key={q.question_id} className={cls} onClick={() => onJump(i)}>
              {i + 1}
              {isMarked && <Icon name="bookmark" size={10} className="survey-nav-bookmark" />}
              {answered && !isCurrent && <span className="survey-nav-dot" />}
            </button>
          );
        })}
      </div>
      <div className="survey-nav-legend">
        <span><span className="survey-legend-dot answered" /> Đã trả lời</span>
        <span><span className="survey-legend-dot current" /> Hiện tại</span>
        <span><span className="survey-legend-dot unanswered" /> Chưa trả lời</span>
      </div>
    </div>
  );
}

function ScreenLanding({ onStart }) {
  return (
    <div className="survey-landing">
      <div className="survey-hero-card">
        <div className="survey-hero-bg" />
        <div className="survey-hero-mascot">
          <span className="survey-mascot-icon">&#x1F41D;</span>
        </div>
        <div className="survey-hero-text">
          <h2>Cùng V-Nexus Tutor khám phá trình độ Tiếng Anh của em!</h2>
          <p>Bài khảo sát giúp tìm ra những kỹ năng em đã làm tốt và những nội dung nên luyện thêm.</p>
        </div>
      </div>

      <div className="survey-info-grid">
        <div className="survey-info-card">
          <div className="survey-info-icon primary">
            <Icon name="format_list_numbered" />
          </div>
          <span className="survey-info-value">14</span>
          <span className="survey-info-label">Câu hỏi</span>
        </div>
        <div className="survey-info-card">
          <div className="survey-info-icon secondary">
            <Icon name="record_voice_over" />
          </div>
          <span className="survey-info-value">Đọc & Nghe</span>
          <span className="survey-info-label">Kỹ năng</span>
        </div>
        <div className="survey-info-card">
          <div className="survey-info-icon tertiary">
            <Icon name="timer" />
          </div>
          <span className="survey-info-value">10–15 phút</span>
          <span className="survey-info-label">Thời gian dự kiến</span>
        </div>
        <div className="survey-info-card">
          <div className="survey-info-icon muted">
            <Icon name="cloud_done" />
          </div>
          <span className="survey-info-value">Lưu bài</span>
          <span className="survey-info-label">Tự động</span>
        </div>
      </div>

      <div className="survey-notes">
        <div className="survey-note-main">
          <Icon name="info" size={20} className="survey-note-icon" />
          <div>
            <p className="survey-note-title">Ghi chú quan trọng</p>
            <p className="survey-note-desc">Đây không phải là một cuộc thi. Em chỉ cần chọn đáp án phù hợp nhất.</p>
          </div>
        </div>
        <div className="survey-note-sub">
          <Icon name="wifi_off" size={20} className="survey-note-sub-icon" />
          <p>Bài làm của em vẫn được lưu nếu kết nối bị gián đoạn.</p>
        </div>
      </div>

      <div className="survey-actions">
        <button className="survey-btn survey-btn-primary" onClick={onStart}>
          <span>Bắt đầu khảo sát</span>
          <Icon name="arrow_forward" size={20} />
        </button>
      </div>
    </div>
  );
}

function ScreenLevelSelect({ selected, onSelect, onNext, onBack }) {
  return (
    <div className="survey-level-select">
      <StepIndicator currentStep={0} />
      <div className="survey-level-content">
        <h2 className="survey-level-title">Chọn cấp độ phù hợp với em</h2>
        <p className="survey-level-subtitle">Không sao nếu em chưa chắc chắn. Kết quả cuối cùng sẽ được điều chỉnh dựa trên bài làm.</p>

        <div className="survey-level-grid">
          {LEVELS.map(level => (
            <div
              key={level.id}
              className={`survey-level-card ${selected === level.id ? 'selected' : ''}`}
              onClick={() => onSelect(level.id)}
            >
              {selected === level.id && (
                <div className="survey-level-check">
                  <Icon name="check_circle" size={18} />
                </div>
              )}
              <div className={`survey-level-icon ${selected === level.id ? 'active' : ''}`}>
                <Icon name={level.icon} size={32} />
              </div>
              <h3 className="survey-level-name">{level.label}</h3>
              <div className={`survey-level-badge ${selected === level.id ? 'active' : ''}`}>{level.cefr}</div>
              <p className="survey-level-desc">{level.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="survey-actions">
        <button className="survey-btn survey-btn-outline" onClick={onBack}>Quay lại</button>
        <button className="survey-btn survey-btn-primary" onClick={onNext} disabled={!selected}>Tiếp tục</button>
      </div>
    </div>
  );
}

function ScreenInstructions({ onNext, onBack }) {
  const steps = [
    'Đọc hoặc nghe kỹ câu hỏi.',
    'Chọn một đáp án.',
    'Nhấn "Kiểm tra đáp án".',
    'Đọc giải thích và chuyển sang câu tiếp theo.',
  ];

  return (
    <div className="survey-instructions">
      <div className="survey-instr-header">
        <h1>Trước khi bắt đầu</h1>
        <p>Hãy đọc kỹ hướng dẫn dưới đây để hoàn thành tốt bài khảo sát nhé.</p>
      </div>

      <div className="survey-instr-grid">
        <div className="survey-instr-steps">
          <div className="survey-instr-steps-header">
            <Icon name="list_alt" style={{ color: 'var(--primary)' }} />
            <h3>4 Bước Làm Bài</h3>
          </div>
          <div className="survey-instr-steps-list">
            {steps.map((step, i) => (
              <div key={i} className="survey-instr-step">
                <div className="survey-instr-step-num">{i + 1}</div>
                <p className="survey-instr-step-text">{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="survey-instr-side">
          <div className="survey-instr-audio">
            <div className="survey-instr-side-header">
              <Icon name="volume_up" size={20} className="text-secondary" />
              <h3>Lưu ý bài nghe</h3>
            </div>
            <ul className="survey-instr-audio-list">
              <li>Em có thể nghe lại trước khi trả lời.</li>
              <li>Nội dung bài nghe sẽ <strong>không hiển thị thành văn bản</strong> trong lúc làm bài.</li>
            </ul>
          </div>
          <div className="survey-instr-status">
            <div className="survey-instr-status-icon">
              <Icon name="cloud_sync" />
            </div>
            <div>
              <h4>Trạng thái</h4>
              <p className="survey-instr-status-text">Bài làm được lưu tự động.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="survey-actions">
        {onBack && <button className="survey-btn survey-btn-outline" onClick={onBack}>Quay lại</button>}
        <button className="survey-btn survey-btn-primary" onClick={onNext}>
          <span>Vào làm bài</span>
          <Icon name="arrow_forward" size={20} />
        </button>
      </div>
    </div>
  );
}

function ScreenTestTaking({ questions, answers, setAnswers, currentIdx, setCurrentIdx, marked, setMarked, onSubmit }) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastCorrect, setLastCorrect] = useState(null);
  const q = questions[currentIdx];

  const handleSelect = (optionId) => {
    if (showFeedback) return;
    setAnswers(prev => ({ ...prev, [q.question_id]: optionId }));
  };

  const handleCheck = () => {
    const selected = answers[q.question_id];
    if (!selected) return;
    const correct = selected === q.correct_option_id;
    setLastCorrect(correct);
    setShowFeedback(true);
  };

  const handleNext = () => {
    setShowFeedback(false);
    setLastCorrect(null);
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    } else if (onSubmit) {
      onSubmit();
    }
  };

  const handleReview = () => {
    setMarked(prev => {
      const next = new Set(prev);
      if (next.has(q.question_id)) next.delete(q.question_id);
      else next.add(q.question_id);
      return next;
    });
  };

  const handleJump = (idx) => {
    setShowFeedback(false);
    setLastCorrect(null);
    setCurrentIdx(idx);
  };

  const diffLabel = q?.difficulty === 'easy' ? 'Dễ' : q?.difficulty === 'medium' ? 'Trung bình' : 'Khó';
  const diffClass = q?.difficulty === 'easy' ? 'easy' : q?.difficulty === 'medium' ? 'medium' : 'hard';

  return (
    <div className="survey-testing">
      <StepIndicator currentStep={1} />
      <ProgressBar current={currentIdx + 1} total={questions.length} />

      <div className="survey-testing-layout">
        <div className="survey-testing-main">
          <div className="survey-question-card">
            <div className="survey-question-tags">
              <span className="survey-tag survey-tag-skill">{q?.skill_name || 'Ngữ pháp'}</span>
              <span className={`survey-tag survey-tag-diff ${diffClass}`}>{diffLabel}</span>
            </div>
            <div className="survey-question-text">
              {q?.prompt?.text || q?.prompt || ''}
            </div>
            <div className="survey-options">
              {q?.options?.map(opt => {
                const isSelected = answers[q.question_id] === opt.option_id;
                const isCorrect = opt.option_id === q.correct_option_id;
                let optClass = 'survey-option';
                if (showFeedback) {
                  if (isSelected && lastCorrect) optClass += ' correct selected';
                  else if (isSelected && !lastCorrect) optClass += ' wrong selected';
                  else if (isCorrect) optClass += ' correct';
                  else optClass += ' dimmed';
                } else if (isSelected) {
                  optClass += ' selected';
                }
                return (
                  <button key={opt.option_id} className={optClass} onClick={() => handleSelect(opt.option_id)}>
                    <div className="survey-option-left">
                      <span className="survey-option-letter">{opt.option_id.toUpperCase()}</span>
                      <span className="survey-option-label">{opt.label}</span>
                    </div>
                    {showFeedback && isSelected && lastCorrect && (
                      <Icon name="check_circle" size={20} className="survey-option-icon correct" />
                    )}
                    {showFeedback && isSelected && !lastCorrect && (
                      <Icon name="cancel" size={20} className="survey-option-icon wrong" />
                    )}
                    {showFeedback && isCorrect && !isSelected && (
                      <Icon name="check_circle" size={20} className="survey-option-icon correct" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {showFeedback && (
            <div className={`survey-feedback ${lastCorrect ? 'correct' : 'wrong'}`}>
              <div className="survey-feedback-header">
                {lastCorrect ? (
                  <>
                    <div className="survey-feedback-icon correct"><Icon name="star" size={24} /></div>
                    <h3 className="survey-feedback-title correct">Chính xác!</h3>
                  </>
                ) : (
                  <>
                    <div className="survey-feedback-icon wrong"><Icon name="error" size={24} /></div>
                    <h3 className="survey-feedback-title wrong">Gần đúng rồi!</h3>
                  </>
                )}
              </div>
              <p className="survey-feedback-desc">
                {lastCorrect
                  ? `Tuyệt vời! Em đã trả lời đúng câu hỏi về ${q?.skill_name || 'kiến thức này'}.`
                  : (() => {
                      const correctOpt = q?.options?.find(o => o.option_id === q.correct_option_id);
                      const wrongOpt = q?.options?.find(o => o.option_id === answers[q.question_id]);
                      const errTag = wrongOpt?.error_tag || '';
                      let hint = `Đáp án đúng là "${correctOpt?.label || ''}".`;
                      if (errTag) hint += ` Lỗi: ${errTag.replace(/_/g, ' ')}.`;
                      return hint;
                    })()
                }
              </p>
              <div className="survey-feedback-quote">
                <p className="survey-feedback-quote-text">
                  {lastCorrect
                    ? `"Tuyệt lắm! Em đã trả lời đúng!"`
                    : `"Đừng nản lòng nhé! Sai ở đây là bình thường, em sẽ học được nhiều điều mới."`
                  }
                </p>
                <span className="survey-feedback-quote-author">- Medi Bee</span>
              </div>
              <div className="survey-feedback-actions">
                <button className="survey-btn survey-btn-primary" onClick={handleNext}>
                  {currentIdx < questions.length - 1 ? 'Câu tiếp theo' : 'Xem kết quả'}
                  <Icon name="arrow_forward" size={20} />
                </button>
              </div>
            </div>
          )}

          {!showFeedback && (
            <div className="survey-testing-actions">
              <button className="survey-btn survey-btn-flag" onClick={handleReview}>
                <Icon name="flag" size={18} />
                {marked.has(q?.question_id) ? 'Bỏ đánh dấu' : 'Đánh dấu xem lại'}
              </button>
              <button
                className={`survey-btn survey-btn-check ${!answers[q?.question_id] ? 'disabled' : ''}`}
                onClick={handleCheck}
                disabled={!answers[q?.question_id]}
              >
                Kiểm tra đáp án
              </button>
            </div>
          )}
        </div>

        <div className="survey-testing-sidebar">
          <QuestionNavigator
            questions={questions}
            answers={answers}
            currentIdx={currentIdx}
            marked={marked}
            onJump={handleJump}
          />
          <button className="survey-btn survey-btn-submit" onClick={onSubmit} style={{ marginTop: 16, width: '100%' }}>
            <Icon name="send" size={18} />
            <span>Nộp bài</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function ScreenReview({ questions, answers, marked, onBack, onSubmit }) {
  const [showDialog, setShowDialog] = useState(false);
  const answeredCount = Object.keys(answers).length;
  const unansweredCount = questions.length - answeredCount;
  const markedCount = marked.size;

  return (
    <div className="survey-review">
      <div className="survey-review-header">
        <h1>Kiểm tra lại bài làm</h1>
        <p>Hãy dành một chút thời gian để soát lại các câu trả lời của em nhé.</p>
      </div>

      {unansweredCount > 0 && (
        <div className="survey-review-warning">
          <Icon name="error" size={20} />
          <p><strong>Em vẫn còn {unansweredCount} câu chưa trả lời.</strong> Em có thể quay lại hoàn thành trước khi nộp bài.</p>
        </div>
      )}

      <div className="survey-review-summary">
        <div className="survey-review-card answered">
          <Icon name="check_circle" size={32} />
          <span className="survey-review-count">{answeredCount}</span>
          <span className="survey-review-label">Đã trả lời</span>
        </div>
        <div className="survey-review-card unanswered">
          <Icon name="help_outline" size={32} />
          <span className="survey-review-count">{unansweredCount}</span>
          <span className="survey-review-label">Chưa trả lời</span>
        </div>
        <div className="survey-review-card marked">
          <Icon name="bookmark" size={32} />
          <span className="survey-review-count">{markedCount}</span>
          <span className="survey-review-label">Xem lại</span>
        </div>
      </div>

      <div className="survey-review-navigator">
        <h3>Danh sách câu hỏi</h3>
        <div className="survey-review-grid">
          {questions.map((q, i) => {
            const isAnswered = !!answers[q.question_id];
            const isMarked = marked.has(q.question_id);
            let cls = 'survey-review-item';
            if (isMarked) cls += ' marked';
            else if (isAnswered) cls += ' answered';
            else cls += ' unanswered';
            return (
              <button key={q.question_id} className={cls}>
                {i + 1}
                {isMarked && <Icon name="bookmark" size={12} />}
              </button>
            );
          })}
        </div>
        <div className="survey-review-legend">
          <span><span className="survey-legend-dot answered" /> Đã trả lời</span>
          <span><span className="survey-legend-dot unanswered" /> Chưa trả lời</span>
          <span><span className="survey-legend-dot marked" /> Xem lại</span>
        </div>
      </div>

      <div className="survey-actions">
        <button className="survey-btn survey-btn-outline" onClick={onBack}>Quay lại làm bài</button>
        <button className="survey-btn survey-btn-primary" onClick={() => setShowDialog(true)}>
          <span>Nộp bài</span>
          <Icon name="send" size={18} />
        </button>
      </div>

      {showDialog && (
        <div className="survey-dialog-overlay" onClick={() => setShowDialog(false)}>
          <div className="survey-dialog" onClick={e => e.stopPropagation()}>
            <div className="survey-dialog-icon">
              <Icon name="task_alt" size={32} />
            </div>
            <h2>Nộp bài ngay?</h2>
            <p>Em muốn nộp bài ngay? Sau khi nộp, Medi Bee sẽ phân tích kết quả và xây dựng lộ trình học tập riêng cho em.</p>
            {unansweredCount > 0 && (
              <div className="survey-dialog-warning">
                <Icon name="info" size={14} />
                <span>Lưu ý: Vẫn còn {unansweredCount} câu hỏi chưa được trả lời.</span>
              </div>
            )}
            <div className="survey-dialog-actions">
              <button className="survey-btn survey-btn-outline" onClick={() => setShowDialog(false)}>Kiểm tra lại</button>
              <button className="survey-btn survey-btn-primary" onClick={onSubmit}>
                <span>Nộp bài</span>
                <Icon name="send" size={18} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ScreenResults({ result, onRestart }) {
  if (!result) return null;
  const masteryArr = Object.entries(result.mastery || {}).map(([id, m]) => ({
    id, ...m,
  })).sort((a, b) => b.probability - a.probability);

  return (
    <div className="survey-results">
      <div className="survey-results-header">
        <h1>Kết quả bài khảo sát</h1>
        <p>Medi Bee đã phân tích xong bài làm của em. Đây là kết quả!</p>
      </div>

      <div className="survey-results-cards">
        <div className="survey-result-card score">
          <span className="survey-result-value">{result.score}/{result.max_score}</span>
          <span className="survey-result-label">Điểm</span>
        </div>
        <div className="survey-result-card pct">
          <span className="survey-result-value">{result.percentage}%</span>
          <span className="survey-result-label">Tỷ lệ đúng</span>
        </div>
        <div className="survey-result-card level">
          <span className="survey-result-value">{result.cefr}</span>
          <span className="survey-result-label">Trình độ CEFR</span>
        </div>
        <div className="survey-result-card time">
          <span className="survey-result-value">{Math.floor(result.time_total_sec / 60)}:{String(result.time_total_sec % 60).padStart(2, '0')}</span>
          <span className="survey-result-label">Thời gian</span>
        </div>
      </div>

      {masteryArr.length > 0 && (
        <div className="survey-results-section">
          <h3>Mastery theo kỹ năng</h3>
          <div className="survey-mastery-list">
            {masteryArr.map(m => (
              <div key={m.id} className="survey-mastery-item">
                <div className="survey-mastery-info">
                  <span className="survey-mastery-name">{m.skill_name}</span>
                  <span className={`survey-mastery-status ${m.status}`}>{m.status === 'mastered' ? 'Thành thạo' : m.status === 'developing' ? 'Đang phát triển' : 'Yếu'}</span>
                </div>
                <div className="survey-mastery-bar">
                  <div className={`survey-mastery-fill ${m.status}`} style={{ width: `${Math.round(m.probability * 100)}%` }} />
                </div>
                <span className="survey-mastery-pct">{Math.round(m.probability * 100)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.gaps?.length > 0 && (
        <div className="survey-results-section">
          <h3>Lỗ hổng kiến thức</h3>
          <div className="survey-gaps-list">
            {result.gaps.map((g, i) => (
              <div key={i} className={`survey-gap-item ${g.severity}`}>
                <Icon name="error" size={18} />
                <div>
                  <span className="survey-gap-skill">{SKILL_LABELS[g.skill_id] || g.skill_id}</span>
                  <span className="survey-gap-reason">{g.reason}</span>
                </div>
                <span className={`survey-gap-severity ${g.severity}`}>{g.severity === 'high' ? 'Mức cao' : 'Mức trung bình'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.recommendations?.length > 0 && (
        <div className="survey-results-section">
          <h3>Kỹ năng cần ôn (BKT)</h3>
          <div className="survey-rec-list">
            {result.recommendations.map((r, i) => (
              <div key={i} className="survey-rec-item">
                <Icon name="lightbulb" size={18} />
                <span className="survey-rec-action">{r.action}</span>
                <span className={`survey-rec-priority ${r.priority}`}>{r.priority === 'high' ? 'Ưu tiên cao' : 'Ưu tiên thấp'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.training_plan && (
        <div className="survey-results-section">
          <h3>Kế hoạch học tập cá nhân hóa (AI)</h3>
          <div className="history-training-plan">{result.training_plan}</div>
        </div>
      )}

      <div className="survey-actions" style={{ justifyContent: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <button className="survey-btn survey-btn-primary" onClick={() => onTabChange && onTabChange('roadmap')}>
          <Icon name="sparkles" size={20} />
          <span>Xem lộ trình của em</span>
        </button>
        <button className="survey-btn survey-btn-primary" onClick={onRestart}>
          <span>Làm lại bài test</span>
          <Icon name="replay" size={20} />
        </button>
      </div>
    </div>
  );
}

export default function StudentSurvey({ user, onTabChange }) {
  const [screen, setScreen] = useState('landing');
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [marked, setMarked] = useState(new Set());
  const [result, setResult] = useState(null);
  const { questions, loading } = useQuestions();

  const handleStart = () => setScreen('level-select');
  const handleLevelNext = () => setScreen('instructions');
  const handleInstructionsNext = () => { setCurrentIdx(0); setScreen('testing'); };
  const handleTestingDone = () => setScreen('review');
  const handleReviewBack = () => setScreen('testing');

  const handleSubmit = useCallback(async () => {
    const res = computeResult(answers, questions);
    setResult(res);
    setScreen('results');

    try {
      const placementTestRes = await apiFetch('/api/placement-tests');
      if (placementTestRes.ok) {
        const tests = await placementTestRes.json();
        const test = tests.find(t => t.test_id === 'placement-test-en-2026');
        if (test) {
          const submitRes = await apiFetch(`/api/placement-tests/${test.id}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              answers: res.answers,
              score: res.score,
              max_score: res.max_score,
              percentage: res.percentage,
              result_level: res.result_level,
              cefr: res.cefr,
              time_total_sec: res.time_total_sec,
              mastery: res.mastery,
              gaps: res.gaps,
              recommendations: res.recommendations,
              test_date: res.test_date,
            }),
          });
          if (submitRes.ok) {
            const saved = await submitRes.json();
            if (saved && saved.training_plan) {
              setResult(prev => ({ ...prev, training_plan: saved.training_plan }));
            }
          }
        }
      }
    } catch (e) {
      console.error('Failed to submit result:', e);
    }
  }, [answers, questions]);

  const handleRestart = () => {
    setScreen('landing');
    setSelectedLevel(null);
    setCurrentIdx(0);
    setAnswers({});
    setMarked(new Set());
    setResult(null);
  };

  if (loading) {
    return (
      <div className="survey-loading">
        <div className="survey-loading-spinner" />
        <p>Đang tải câu hỏi...</p>
      </div>
    );
  }

  return (
    <div className="student-survey">
      {screen === 'landing' && <ScreenLanding onStart={handleStart} />}
      {screen === 'level-select' && (
        <ScreenLevelSelect
          selected={selectedLevel}
          onSelect={setSelectedLevel}
          onNext={handleLevelNext}
          onBack={() => setScreen('landing')}
        />
      )}
      {screen === 'instructions' && (
        <ScreenInstructions
          onNext={handleInstructionsNext}
          onBack={() => setScreen('level-select')}
        />
      )}
      {screen === 'testing' && (
        <ScreenTestTaking
          questions={questions}
          answers={answers}
          setAnswers={setAnswers}
          currentIdx={currentIdx}
          setCurrentIdx={setCurrentIdx}
          marked={marked}
          setMarked={setMarked}
          onSubmit={handleTestingDone}
        />
      )}
      {screen === 'review' && (
        <ScreenReview
          questions={questions}
          answers={answers}
          marked={marked}
          onBack={handleReviewBack}
          onSubmit={handleSubmit}
        />
      )}
      {screen === 'results' && (
        <ScreenResults result={result} onRestart={handleRestart} />
      )}
    </div>
  );
}
