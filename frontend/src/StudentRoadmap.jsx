import React, { useState } from 'react';
import { Sparkles, CheckCircle2, Circle, BookOpen, ClipboardCheck, X, CheckCircle, XCircle } from 'lucide-react';
import { apiFetch } from './api';

const LEVEL_LABELS = {
  starter: 'Mới bắt đầu',
  beginner: 'Cơ bản',
  elementary: 'Sơ cấp',
};

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return '—';
  return d.toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function QuickCheckModal({ result, onClose, onDone }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [outcome, setOutcome] = useState(null); // { passed, remaining_gaps }

  React.useEffect(() => {
    let active = true;
    setLoading(true);
    apiFetch(`/api/test-results/${result.id}/quick-check-questions`)
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => { if (active) setQuestions(data); })
      .catch(() => { if (active) setQuestions([]); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [result.id]);

  const choose = (qid, oid) => setAnswers((prev) => ({ ...prev, [qid]: oid }));

  const submit = async () => {
    setSubmitting(true);
    try {
      const res = await apiFetch(`/api/test-results/${result.id}/quick-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          answers: Object.entries(answers).map(([question_id, selected]) => ({ question_id, selected })),
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setOutcome(data);
        if (onDone) onDone(data);
      }
    } catch (e) {
      console.error('quick check failed', e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="qc-overlay" onClick={onClose}>
      <div className="qc-modal" onClick={(e) => e.stopPropagation()}>
        <div className="qc-head">
          <h3><Sparkles size={18} style={{ verticalAlign: '-3px', marginRight: 6 }} />Đánh giá nhanh</h3>
          <button className="qc-close" onClick={onClose}><X size={18} /></button>
        </div>

        {loading && <p className="qc-loading">Đang tải câu hỏi...</p>}

        {!loading && !outcome && (
          <>
            <p className="qc-sub">Trả lời {questions.length} câu liên quan lỗ hổng của bài này để kiểm tra lộ trình.</p>
            <div className="qc-questions">
              {questions.map((q, idx) => (
                <div key={q.question_id} className="qc-q">
                  <p className="qc-q-prompt"><strong>{idx + 1}.</strong> {q.prompt?.text || q.question_id}</p>
                  <div className="qc-opts">
                    {(q.options || []).map((o) => (
                      <button
                        key={o.option_id}
                        className={`qc-opt ${answers[q.question_id] === o.option_id ? 'selected' : ''}`}
                        onClick={() => choose(q.question_id, o.option_id)}
                      >
                        <span className="qc-opt-label">{o.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <div className="qc-actions">
              <button className="btn btn-ghost" onClick={onClose}>Hủy</button>
              <button className="btn btn-primary" onClick={submit} disabled={submitting || Object.keys(answers).length < questions.length}>
                {submitting ? 'Đang chấm...' : 'Nộp đánh giá'}
              </button>
            </div>
          </>
        )}

        {outcome && (
          <div className="qc-result">
            {outcome.passed ? (
              <>
                <div className="qc-result-badge pass"><CheckCircle size={28} /> Em đã hoàn thành lộ trình!</div>
                <p>Lộ trình của bài này được đánh dấu <strong>Đã hoàn thành ✓</strong>.</p>
              </>
            ) : (
              <>
                <div className="qc-result-badge fail"><XCircle size={28} /> Cần ôn thêm một số kỹ năng</div>
                <p>Em cần ôn thêm:</p>
                <ul className="qc-remaining">
                  {outcome.remaining_gaps.map((g, i) => (
                    <li key={i}>{g.skill_name || g.skill_id} ({Math.round((g.probability || 0) * 100)}%)</li>
                  ))}
                </ul>
              </>
            )}
            <div className="qc-actions">
              <button className="btn btn-primary" onClick={onClose}>Đóng</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function RoadmapCard({ result, isLatest, onQuickCheck }) {
  return (
    <div className={`roadmap-card ${isLatest ? 'latest' : ''} ${result.roadmap_completed ? 'completed' : ''}`}>
      <div className="roadmap-card-head">
        <div>
          <span className="roadmap-card-level">{LEVEL_LABELS[result.result_level] || result.result_level}</span>
          <span className="roadmap-card-cefr">{result.cefr}</span>
        </div>
        <div className="roadmap-card-badge">
          {result.roadmap_completed ? (
            <span className="roadmap-badge done">
              <CheckCircle2 size={16} /> Đã hoàn thành
            </span>
          ) : (
            <span className="roadmap-badge todo">
              <Circle size={16} /> Chưa hoàn thành
            </span>
          )}
        </div>
      </div>

      <p className="roadmap-card-date">
        <ClipboardCheck size={14} /> {formatDate(result.test_date)} {isLatest && <em>(mới nhất)</em>}
      </p>

      {result.training_plan ? (
        <div className="history-training-plan">{result.training_plan}</div>
      ) : (
        <p className="roadmap-empty-plan">Bài này chưa có kế hoạch AI.</p>
      )}

      <div className="roadmap-card-actions">
        <button className="btn btn-primary" onClick={() => onQuickCheck && onQuickCheck(result)}>
          <Sparkles size={16} />
          <span>Đánh giá nhanh</span>
        </button>
      </div>
    </div>
  );
}

export default function StudentRoadmap({ results, questions, onStartSurvey, onQuickCheck }) {
  const [filter, setFilter] = useState('all');
  const [activeResult, setActiveResult] = useState(null);

  const list = Array.isArray(results) ? results : [];
  const withPlan = list.filter((r) => r.training_plan);
  const visible = filter === 'completed'
    ? withPlan.filter((r) => r.roadmap_completed)
    : filter === 'todo'
      ? withPlan.filter((r) => !r.roadmap_completed)
      : withPlan;

  const handleQuickCheck = (result) => {
    if (onQuickCheck) onQuickCheck(result);
    setActiveResult(result);
  };

  const handleDone = () => {
    // reload để cập nhật badge hoàn thành
    if (typeof window !== 'undefined') {
      const ev = new CustomEvent('vnexus:refresh-roadmap');
      window.dispatchEvent(ev);
    }
  };

  if (list.length === 0) {
    return (
      <div className="student-roadmap animate-fade-in">
        <div className="roadmap-empty">
          <Sparkles size={48} style={{ color: 'var(--text-muted)' }} />
          <h3>Em chưa có lộ trình học tập nào</h3>
          <p>Hãy hoàn thành bài Khảo sát đầu vào để nhận kế hoạch học tập cá nhân hóa từ AI.</p>
          <button className="btn btn-primary" onClick={onStartSurvey}>
            <BookOpen size={18} />
            <span>Bắt đầu khảo sát</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="student-roadmap animate-fade-in">
      <div className="roadmap-toolbar">
        <p className="roadmap-subtitle">
          Tổng hợp kế hoạch học tập cá nhân hóa từ {withPlan.length} bài đánh giá của em.
        </p>
        <div className="roadmap-filter">
          <button className={`chip ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>Tất cả</button>
          <button className={`chip ${filter === 'todo' ? 'active' : ''}`} onClick={() => setFilter('todo')}>Chưa hoàn thành</button>
          <button className={`chip ${filter === 'completed' ? 'active' : ''}`} onClick={() => setFilter('completed')}>Đã hoàn thành</button>
        </div>
      </div>

      {visible.length === 0 ? (
        <div className="roadmap-empty">
          <p>Không có bài nào trong bộ lọc này.</p>
        </div>
      ) : (
        <div className="roadmap-list">
          {visible.map((r, i) => (
            <RoadmapCard
              key={r.id}
              result={r}
              isLatest={i === 0}
              onQuickCheck={handleQuickCheck}
            />
          ))}
        </div>
      )}

      {activeResult && (
        <QuickCheckModal result={activeResult} onClose={() => setActiveResult(null)} onDone={handleDone} />
      )}
    </div>
  );
}
