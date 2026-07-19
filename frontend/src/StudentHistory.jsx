import React, { useState, useEffect } from 'react';
import { ClipboardCheck, AlertTriangle, Lightbulb, ArrowLeft, Clock, BookOpen } from 'lucide-react';
import BeautifulRoadmap from './BeautifulRoadmap';

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

        {/* ===== 2 SECTION QUAN TRỌNG NHẤT ===== */}
        <div className="detail-highlight-grid">
          {/* Lỗ hổng kiến thức */}
          <div className="detail-highlight-card detail-gaps">
            <div className="detail-highlight-header">
              <div className="detail-highlight-icon gaps">
                <AlertTriangle size={22} />
              </div>
              <div>
                <h3>Lỗ hổng kiến thức</h3>
                <p className="detail-highlight-sub">{result.gaps?.length || 0} vấn đề cần khắc phục</p>
              </div>
            </div>
            {result.gaps?.length > 0 ? (
              <div className="detail-gaps-list">
                {result.gaps.map((g, i) => (
                  <div key={i} className={`detail-gap-item ${g.severity}`}>
                    <div className="detail-gap-left">
                      <span className="detail-gap-skill">{SKILL_LABELS[g.skill_id] || g.skill_id}</span>
                      <span className="detail-gap-reason">{g.reason}</span>
                    </div>
                    <span className={`detail-gap-severity ${g.severity}`}>
                      {g.severity === 'high' ? 'Ưu tiên cao' : 'Trung bình'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="detail-highlight-empty">
                <p>Không phát hiện lỗ hổng nào. Tiếp tục phát huy!</p>
              </div>
            )}
          </div>

          {/* Kế hoạch đào tạo cá nhân hóa */}
          <div className="detail-highlight-card detail-plan">
            <div className="detail-highlight-header">
              <div className="detail-highlight-icon plan">
                <Lightbulb size={22} />
              </div>
              <div>
                <h3>Kế hoạch đào tạo cá nhân hóa</h3>
                <p className="detail-highlight-sub">AI phân tích và gợi ý học tập</p>
              </div>
            </div>
            {result.training_plan ? (
              <BeautifulRoadmap planText={result.training_plan} studentKey={"history_" + result.id} />
            ) : (
              <div className="detail-highlight-empty">
                <p>Chưa có kế hoạch. Hãy hoàn thành bài khảo sát để nhận kế hoạch từ AI.</p>
              </div>
            )}
          </div>
        </div>

        {/* Kỹ năng cần ôn */}
        {result.recommendations?.length > 0 && (
          <div className="survey-results-section">
            <h3>
              <Lightbulb size={18} style={{ verticalAlign: '-3px', marginRight: 6, color: '#4d44b5' }} />
              Kỹ năng cần ôn (BKT)
            </h3>
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

        {/* Mastery */}
        {masteryArr.length > 0 && (
          <div className="survey-results-section">
            <h3>Mastery theo kỹ năng</h3>
            <table className="survey-table mastery-table">
              <thead>
                <tr>
                  <th>Kỹ năng</th>
                  <th>Xác suất (%)</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {masteryArr.map((m) => (
                  <tr key={m.id}>
                    <td>{m.skill_name || m.id}</td>
                    <td>{Math.round((m.probability || 0) * 100)}%</td>
                    <td>
                      <span className={`survey-mastery-status ${m.status}`}>
                        {m.status === 'mastered' ? 'Thành thạo' : m.status === 'developing' ? 'Đang phát triển' : 'Yếu'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Chi tiết câu trả lời */}
        {answers.length > 0 && (
          <div className="survey-results-section">
            <h3>Chi tiết câu trả lời ({answers.length})</h3>
            <table className="survey-table answers-table">
              <thead>
                <tr>
                  <th>STT</th>
                  <th>Câu hỏi</th>
                  <th>Đáp án em chọn</th>
                  <th>Đáp án đúng</th>
                  <th>Đúng/Sai</th>
                  <th>Giải thích</th>
                </tr>
              </thead>
              <tbody>
                {answers.map((a, i) => {
                  const q = qMap[a.question_id];
                  const promptText = typeof q?.prompt === 'string'
                    ? q.prompt
                    : (q?.prompt?.text || q?.prompt?.audio_transcript || a.question_id);
                  const selectedOpt = q?.options?.find((o) => o.option_id === a.selected);
                  const correctOpt = q?.options?.find((o) => o.option_id === q.correct_option_id);
                  return (
                    <tr key={a.question_id || i} className={a.correct ? 'row-correct' : 'row-wrong'}>
                      <td>{i + 1}</td>
                      <td>{promptText}</td>
                      <td>{selectedOpt?.label || a.selected || '—'}</td>
                      <td>{correctOpt?.label || q?.correct_option_id || '—'}</td>
                      <td>
                        <span className={`history-answer-badge ${a.correct ? 'correct' : 'wrong'}`}>
                          {a.correct ? 'Đúng' : 'Sai'}
                        </span>
                      </td>
                      <td>
                        {!a.correct && q?.explanation ? (
                          <span className="history-answer-explain">{q.explanation}</span>
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
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
          {[...results]
            .sort((a, b) => new Date(b.test_date || 0) - new Date(a.test_date || 0))
            .map((r) => (
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
