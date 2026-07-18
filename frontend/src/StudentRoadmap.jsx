import React, { useState } from 'react';
import { Sparkles, CheckCircle2, Circle, BookOpen, ClipboardCheck, X, CheckCircle, XCircle, ArrowRight } from 'lucide-react';
import { apiFetch } from './api';
import BeautifulRoadmap from './BeautifulRoadmap';

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

function RoadmapCard({ result, isLatest, onQuickCheck, onStartSurvey }) {
  const [completed, setCompleted] = useState(result.roadmap_completed);

  React.useEffect(() => {
    setCompleted(result.roadmap_completed);
  }, [result.roadmap_completed]);

  const handleCompletionChange = async (isCompleted) => {
    if (completed !== isCompleted) {
      setCompleted(isCompleted);
      result.roadmap_completed = isCompleted;
      try {
        await apiFetch(`/api/test-results/${result.id}/complete`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ completed: isCompleted })
        });
      } catch (e) {
        console.error('Failed to update roadmap completion status', e);
      }
    }
  };

  return (
    <div className={`roadmap-card ${isLatest ? 'latest' : ''} ${completed ? 'completed' : ''}`}>
      <div className="roadmap-card-head">
        <div>
          <span className="roadmap-card-level">{LEVEL_LABELS[result.result_level] || result.result_level}</span>
          <span className="roadmap-card-cefr">{result.cefr}</span>
        </div>
        <div className="roadmap-card-badge">
          {completed ? (
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
        <BeautifulRoadmap planText={result.training_plan} studentKey={`result_${result.id}`} onCompleteChange={handleCompletionChange} />
      ) : (
        <p className="roadmap-empty-plan">Bài này chưa có kế hoạch AI.</p>
      )}

      <div className="survey-actions" style={{ marginTop: '20px' }}>
        <button className="survey-btn survey-btn-primary" onClick={onStartSurvey}>
          <span>Bắt đầu khảo sát</span>
          <ArrowRight size={20} />
        </button>
      </div>
    </div>
  );
}

export default function StudentRoadmap({ results, questions, onStartSurvey, onQuickCheck, studentProfile, onTabChange }) {
  return (
    <div className="sd-container" style={{ padding: 0, margin: 0, background: 'transparent', boxShadow: 'none' }}>
      <div className="sd-header">
        <div>
          <h2 className="sd-title">Lộ trình của em</h2>
          <div className="sd-tabs">
            <span onClick={() => onTabChange && onTabChange('student-dashboard')} className="sd-tab">Tổng quan</span>
            <span onClick={() => onTabChange && onTabChange('roadmap')} className="sd-tab active">Lộ trình của em</span>
            <span onClick={() => onTabChange && onTabChange('progress')} className="sd-tab">Tiến bộ</span>
          </div>
        </div>
      </div>

      <main className="max-w-[1200px] mx-auto px-container-margin-mobile md:px-container-margin-desktop py-lg">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
          {/* Left Column: Timeline */}
          <div className="lg:col-span-8">
            {/* Step 1 */}
            <div className="timeline-step relative flex mb-md">
              <div className="timeline-line"></div>
              <div className="timeline-dot completed font-headline-card-sm text-headline-card-sm bg-tertiary text-on-tertiary flex items-center justify-center w-10 h-10 rounded-full z-10 relative">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>check</span>
              </div>
              <div className="timeline-content-card bg-surface-container-lowest rounded-2xl p-lg soft-shadow flex-1 ml-4 border border-outline-variant/30">
                <div className="flex justify-between items-start mb-sm">
                  <div>
                    <span className="bg-tertiary-container/20 text-tertiary-container font-label-md text-label-md px-2 py-1 rounded-full mb-2 inline-block">Đã hoàn thành</span>
                    <h3 className="font-headline-card-sm text-headline-card-sm text-on-background">1. Food and Tableware</h3>
                    <p className="text-on-surface-variant mt-1 text-body-md font-body-md">Từ vựng về đồ ăn và dụng cụ bàn ăn cơ bản.</p>
                  </div>
                  <div className="text-right text-on-surface-variant font-caption text-caption">
                    <div><span className="material-symbols-outlined align-middle text-[16px] mr-1">schedule</span>15 phút</div>
                    <div className="mt-1"><span className="material-symbols-outlined align-middle text-[16px] mr-1">edit_square</span>3 bài tập</div>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="flex justify-between text-caption font-caption mb-1">
                    <span className="text-on-surface-variant">Tiến độ</span>
                    <span className="text-tertiary font-bold">80%</span>
                  </div>
                  <div className="progress-bar-bg h-2 rounded-full w-full">
                    <div className="progress-bar-fill-green h-full rounded-full" style={{width: '80%'}}></div>
                  </div>
                </div>
                <div className="mt-4 flex justify-end">
                  <button className="bg-surface-variant text-primary font-label-md text-label-md px-4 py-2 rounded-full hover:bg-surface-container-high transition-colors">
                    Ôn tập lại
                  </button>
                </div>
              </div>
            </div>

            {/* Step 2 (Active) */}
            <div className="timeline-step active relative flex mb-md">
              <div className="timeline-line"></div>
              <div className="timeline-dot active font-headline-card-sm text-headline-card-sm bg-primary text-on-primary flex items-center justify-center w-12 h-12 rounded-full shadow-[0px_4px_10px_rgba(53,41,157,0.3)] z-10 relative -ml-1">
                2
              </div>
              <div className="timeline-content-card bg-surface-container-lowest rounded-2xl p-lg shadow-lg border border-primary flex-1 ml-3">
                <div className="flex justify-between items-start mb-sm">
                  <div>
                    <span className="bg-primary-container/20 text-primary font-label-md text-label-md px-2 py-1 rounded-full mb-2 inline-block animate-pulse">Đang học</span>
                    <h3 className="font-headline-card-sm text-headline-card-sm text-primary">2. Some và Any</h3>
                    <p className="text-on-surface-variant mt-1 text-body-md font-body-md">Phân biệt cách dùng some và any trong lời mời, câu hỏi và câu phủ định.</p>
                  </div>
                  <div className="text-right text-on-surface-variant font-caption text-caption">
                    <div><span className="material-symbols-outlined align-middle text-[16px] mr-1">schedule</span>20 phút</div>
                    <div className="mt-1"><span className="material-symbols-outlined align-middle text-[16px] mr-1">edit_square</span>5 bài tập</div>
                  </div>
                </div>
                <div className="bg-surface-container-low rounded-lg p-sm mt-4 border border-outline-variant/30 relative overflow-hidden group">
                  <div className="absolute -right-10 -top-10 w-32 h-32 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors"></div>
                  <p className="font-label-md text-label-md text-on-surface-variant mb-1">Ví dụ đang học:</p>
                  <p className="font-headline-card-sm text-headline-card-sm text-on-background italic">"Would you like <span className="text-secondary font-bold">some</span> water?"</p>
                </div>
                <div className="mt-4">
                  <div className="flex justify-between text-caption font-caption mb-1">
                    <span className="text-on-surface-variant">Tiến độ</span>
                    <span className="text-primary font-bold">40%</span>
                  </div>
                  <div className="progress-bar-bg h-2 rounded-full w-full">
                    <div className="progress-bar-fill-purple h-full rounded-full" style={{width: '40%'}}></div>
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <button className="bg-secondary text-on-secondary font-label-md text-label-md px-6 py-3 rounded-full shadow-[0px_4px_10px_rgba(164,60,32,0.2)] hover:-translate-y-1 transition-all duration-200">
                    Tiếp tục bài học
                  </button>
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="timeline-step relative flex mb-md">
              <div className="timeline-line"></div>
              <div className="timeline-dot text-outline font-headline-card-sm text-headline-card-sm bg-surface-container-high border-2 border-outline-variant text-outline flex items-center justify-center w-10 h-10 rounded-full z-10 relative">
                3
              </div>
              <div className="timeline-content-card opacity-80 bg-surface-container-lowest rounded-2xl p-lg soft-shadow flex-1 ml-4 border border-outline-variant/30">
                <div className="flex justify-between items-start mb-sm">
                  <div>
                    <span className="bg-surface-variant text-on-surface-variant font-label-md text-label-md px-2 py-1 rounded-full mb-2 inline-block">Sắp tới</span>
                    <h3 className="font-headline-card-sm text-headline-card-sm text-on-background">3. Past Simple Irregular Verbs</h3>
                    <p className="text-on-surface-variant mt-1 text-body-md font-body-md">Làm quen với các động từ bất quy tắc thường gặp.</p>
                  </div>
                  <div className="text-right text-on-surface-variant font-caption text-caption">
                    <div><span className="material-symbols-outlined align-middle text-[16px] mr-1">schedule</span>25 phút</div>
                    <div className="mt-1"><span className="material-symbols-outlined align-middle text-[16px] mr-1">edit_square</span>4 bài tập</div>
                  </div>
                </div>
                <div className="mt-4 flex justify-end">
                  <button className="text-primary font-label-md text-label-md px-4 py-2 hover:bg-surface-container-high rounded-full transition-colors" disabled>
                    Chờ mở khóa
                  </button>
                </div>
              </div>
            </div>

            {/* Step 4 */}
            <div className="timeline-step relative flex mb-md">
              <div className="timeline-line"></div>
              <div className="timeline-dot text-outline-variant font-headline-card-sm text-headline-card-sm bg-surface-container-high border-2 border-outline-variant border-dashed text-outline-variant flex items-center justify-center w-10 h-10 rounded-full z-10 relative">
                <span className="material-symbols-outlined">lock</span>
              </div>
              <div className="timeline-content-card opacity-60 bg-surface-container-lowest rounded-2xl p-lg soft-shadow flex-1 ml-4 border border-outline-variant/30">
                <div className="flex justify-between items-start mb-sm">
                  <div>
                    <span className="bg-surface-variant/50 text-outline font-label-md text-label-md px-2 py-1 rounded-full mb-2 inline-block">Đã khóa</span>
                    <h3 className="font-headline-card-sm text-headline-card-sm text-on-background">4. Past Simple Question Forms</h3>
                    <p className="text-on-surface-variant mt-1 text-body-md font-body-md">Cách đặt câu hỏi trong thì quá khứ đơn.</p>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Right Column: Support */}
          <div className="lg:col-span-4 mt-8 lg:mt-0">
            <div className="bg-surface-container-lowest rounded-2xl p-lg shadow-[0px_10px_30px_rgba(77,68,181,0.05)] sticky top-[100px]">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-secondary-container/20 flex items-center justify-center text-secondary">
                  <span className="material-symbols-outlined">help_center</span>
                </div>
                <h2 className="font-headline-card text-headline-card text-on-background">Nếu em gặp khó khăn</h2>
              </div>
              <p className="text-body-md font-body-md text-on-surface-variant mb-6">Đừng lo lắng! V-Nexus School luôn ở đây để giúp em vượt qua những bài tập khó.</p>
              
              <div className="space-y-3">
                <button className="w-full flex items-center justify-between p-4 rounded-xl border border-outline-variant hover:border-primary hover:bg-inverse-on-surface transition-all duration-200 group">
                  <div className="flex items-center gap-3 text-on-background">
                    <span className="material-symbols-outlined text-primary">lightbulb</span>
                    <span className="font-label-md text-label-md">Xem ví dụ</span>
                  </div>
                  <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors">chevron_right</span>
                </button>
                <button className="w-full flex items-center justify-between p-4 rounded-xl border border-outline-variant hover:border-primary hover:bg-inverse-on-surface transition-all duration-200 group">
                  <div className="flex items-center gap-3 text-on-background">
                    <span className="material-symbols-outlined text-primary">arrow_downward</span>
                    <span className="font-label-md text-label-md">Giảm độ khó</span>
                  </div>
                  <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors">chevron_right</span>
                </button>
                <button className="w-full flex items-center justify-between p-4 rounded-xl border border-outline-variant hover:border-primary hover:bg-inverse-on-surface transition-all duration-200 group">
                  <div className="flex items-center gap-3 text-on-background">
                    <span className="material-symbols-outlined text-primary">shuffle</span>
                    <span className="font-label-md text-label-md">Làm dạng bài khác</span>
                  </div>
                  <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors">chevron_right</span>
                </button>
                <button className="w-full flex items-center justify-between p-4 rounded-xl bg-primary-container text-on-primary-container hover:bg-primary-fixed-dim transition-all duration-200 shadow-sm mt-4">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined">record_voice_over</span>
                    <span className="font-label-md text-label-md">Nhờ giáo viên hỗ trợ</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
      <style>{`
        .timeline-line {
          position: absolute;
          left: 20px;
          top: 40px;
          bottom: -20px;
          width: 2px;
          background: #dee0ff;
          z-index: 0;
        }
        .timeline-step:last-child .timeline-line {
          display: none;
        }
      `}</style>
    </div>
  );
}
