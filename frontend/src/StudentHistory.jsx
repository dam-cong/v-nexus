import React, { useState, useEffect } from 'react';
import { ClipboardCheck, AlertTriangle, Lightbulb, ArrowLeft, Clock, BookOpen } from 'lucide-react';

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
};

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

function formatTime(sec) {
  const s = Number(sec) || 0;
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

function levelClass(level) {
  if (level === 'starter') return 'starter';
  if (level === 'elementary') return 'elementary';
  return 'beginner';
}

function ResultDetail({ result, questions, onBack }) {
  if (!result) return null;
  const masteryArr = Array.isArray(result.mastery)
    ? result.mastery
    : Object.entries(result.mastery || {}).map(([k, v]) => ({ ...v, id: k }));

  const qMap = {};
  (questions || []).forEach((q) => { qMap[q.question_id] = q; });
  const answers = Array.isArray(result.answers) ? result.answers : [];

  return (
    <div className="history-detail animate-fade-in">
      <button className="history-back-btn" onClick={onBack}>
        <ArrowLeft size={18} />
        <span>Quay lại danh sách</span>
      </button>

      <div className="survey-results">
        <div className="survey-results-header">
          <h1>Chi tiết bài đánh giá</h1>
          <p>{formatDate(result.test_date)}</p>
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
            <span className="survey-result-value">{formatTime(result.time_total_sec)}</span>
            <span className="survey-result-label">Thời gian</span>
          </div>
        </div>

        {masteryArr.length > 0 && (
          <div className="survey-results-section">
            <h3>Mastery theo kỹ năng</h3>
            <div className="survey-mastery-list">
              {masteryArr.map((m) => (
                <div key={m.id} className="survey-mastery-item">
                  <div className="survey-mastery-info">
                    <span className="survey-mastery-name">{m.skill_name || m.id}</span>
                    <span className={`survey-mastery-status ${m.status}`}>
                      {m.status === 'mastered' ? 'Thành thạo' : m.status === 'developing' ? 'Đang phát triển' : 'Yếu'}
                    </span>
                  </div>
                  <div className="survey-mastery-bar">
                    <div
                      className={`survey-mastery-fill ${m.status}`}
                      style={{ width: `${Math.round((m.probability || 0) * 100)}%` }}
                    />
                  </div>
                  <span className="survey-mastery-pct">{Math.round((m.probability || 0) * 100)}%</span>
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
                  <AlertTriangle size={18} />
                  <div>
                    <span className="survey-gap-skill">{SKILL_LABELS[g.skill_id] || g.skill_id}</span>
                    <span className="survey-gap-reason">{g.reason}</span>
                  </div>
                  <span className={`survey-gap-severity ${g.severity}`}>
                    {g.severity === 'high' ? 'Mức cao' : 'Mức trung bình'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {result.recommendations?.length > 0 && (
          <div className="survey-results-section">
            <h3>Đề xuất học tập</h3>
            <div className="survey-rec-list">
              {result.recommendations.map((r, i) => (
                <div key={i} className="survey-rec-item">
                  <Lightbulb size={18} />
                  <span className="survey-rec-action">{r.action}</span>
                  <span className={`survey-rec-priority ${r.priority}`}>
                    {r.priority === 'high' ? 'Ưu tiên cao' : 'Ưu tiên thấp'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {result.training_plan && (
          <div className="survey-results-section">
            <h3>
              <Lightbulb size={18} style={{ verticalAlign: '-3px', marginRight: 6, color: '#a43c20' }} />
              Kế hoạch đào tạo cá nhân hóa (AI)
            </h3>
            <div className="history-training-plan">{result.training_plan}</div>
          </div>
        )}

        {answers.length > 0 && (
          <div className="survey-results-section">
            <h3>Câu đã trả lời ({answers.length})</h3>
            <div className="history-answers-list">
              {answers.map((a, i) => {
                const q = qMap[a.question_id];
                const selectedOpt = q?.options?.find((o) => o.option_id === a.selected);
                const correctOpt = q?.options?.find((o) => o.option_id === q.correct_option_id);
                return (
                  <div key={a.question_id || i} className={`history-answer-item ${a.correct ? 'correct' : 'wrong'}`}>
                    <div className="history-answer-head">
                      <span className="history-answer-index">{i + 1}</span>
                      <span className={`history-answer-badge ${a.correct ? 'correct' : 'wrong'}`}>
                        {a.correct ? 'Đúng' : 'Sai'}
                      </span>
                      {q?.skill_name && <span className="history-answer-skill">{q.skill_name}</span>}
                    </div>
                    <p className="history-answer-prompt">
                      {q?.prompt?.text || a.question_id}
                    </p>
                    <div className="history-answer-options">
                      {(q?.options || []).map((o) => {
                        const isSelected = o.option_id === a.selected;
                        const isCorrect = o.option_id === q?.correct_option_id;
                        let cls = 'history-answer-opt';
                        if (isCorrect) cls += ' is-correct';
                        else if (isSelected && !isCorrect) cls += ' is-selected-wrong';
                        return (
                          <div key={o.option_id} className={cls}>
                            <span className="history-answer-opt-label">{o.label}</span>
                            {isCorrect && <span className="history-answer-mark">✓ Đáp án đúng</span>}
                            {isSelected && !isCorrect && <span className="history-answer-mark">Em chọn</span>}
                            {isSelected && isCorrect && <span className="history-answer-mark">Em chọn ✓</span>}
                          </div>
                        );
                      })}
                    </div>
                    {!a.correct && q?.explanation && (
                      <p className="history-answer-explain">
                        <strong>Giải thích:</strong> {q.explanation}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function StudentHistory({ user, results, questions, onStartSurvey, onRetry }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    Promise.resolve(onRetry && onRetry())
      .catch(() => { if (active) setError('load'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const hasResults = Array.isArray(results) && results.length > 0;

  if (selected) {
    return <ResultDetail result={selected} questions={questions} onBack={() => setSelected(null)} />;
  }

  return (
    <div className="student-history animate-fade-in">
      <div className="history-toolbar">
        <p className="history-subtitle">
          Xem lại các bài khảo sát đầu vào mà em đã hoàn thành.
        </p>
        <button className="btn btn-ghost" onClick={() => onRetry && onRetry()}>
          Làm mới
        </button>
      </div>

      {loading && (
        <div className="history-empty">
          <p>Đang tải kết quả...</p>
        </div>
      )}

      {!loading && error && (
        <div className="history-empty">
          <p style={{ color: '#ba1a1a' }}>Không thể tải lịch sử bài đánh giá.</p>
        </div>
      )}

      {!loading && !error && !hasResults && (
        <div className="history-empty">
          <ClipboardCheck size={48} style={{ color: 'var(--text-muted)' }} />
          <h3>Em chưa có bài đánh giá nào</h3>
          <p>Hãy bắt đầu bài khảo sát đầu vào để xem kết quả và lộ trình học tập.</p>
          <button className="btn btn-primary" onClick={onStartSurvey}>
            <BookOpen size={18} />
            <span>Bắt đầu khảo sát</span>
          </button>
        </div>
      )}

      {!loading && !error && hasResults && (
        <div className="history-list">
          {results.map((r) => (
            <div key={r.id} className={`history-card ${levelClass(r.result_level)}`}>
              <div className="history-card-main">
                <div className={`history-card-badge ${levelClass(r.result_level)}`}>
                  {r.cefr}
                </div>
                <div className="history-card-info">
                  <span className="history-card-level">
                    {LEVEL_LABELS[r.result_level] || r.result_level}
                  </span>
                  <span className="history-card-date">
                    <Clock size={14} /> {formatDate(r.test_date)}
                  </span>
                </div>
              </div>
              <div className="history-card-stats">
                <div className="history-stat">
                  <span className="history-stat-val">{r.score}/{r.max_score}</span>
                  <span className="history-stat-label">Điểm</span>
                </div>
                <div className="history-stat">
                  <span className="history-stat-val">{r.percentage}%</span>
                  <span className="history-stat-label">Tỷ lệ đúng</span>
                </div>
                <div className="history-stat">
                  <span className="history-stat-val">{formatTime(r.time_total_sec)}</span>
                  <span className="history-stat-label">Thời gian</span>
                </div>
              </div>
              <button className="btn btn-primary history-detail-btn" onClick={() => setSelected(r)}>
                Xem chi tiết
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
