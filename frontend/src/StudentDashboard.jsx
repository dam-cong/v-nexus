import React, { useState, useEffect, useMemo } from 'react';
import { 
  GraduationCap, 
  Trophy, 
  TrendingUp, 
  ClipboardCheck, 
  BookOpen, 
  Sparkles, 
  Clock, 
  Settings, 
  AlertTriangle, 
  Lightbulb, 
  CheckCircle2, 
  Circle, 
  Calendar, 
  ArrowRight,
  Flame,
  Star,
  Coins
} from 'lucide-react';
import './StudentDashboard.css';

// Helper to parse JSON roadmap plan
function tryParseJsonPlan(text) {
  if (!text) return null;
  try {
    const cleaned = text.trim();
    if (cleaned.startsWith('{') && cleaned.endsWith('}')) {
      return JSON.parse(cleaned);
    }
    const match = cleaned.match(/\{[\s\S]*\}/);
    if (match) {
      return JSON.parse(match[0]);
    }
  } catch (e) {
    console.warn("JSON parsing failed:", e);
  }
  return null;
}

// Helper to parse text roadmap plan
function parseRoadmap(text) {
  if (!text) return { intro: '', sections: [] };
  const lines = text.split('\n');
  let intro = '';
  const sections = [];
  let currentSection = null;

  for (let line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (trimmed.startsWith('# ')) {
      if (currentSection) sections.push(currentSection);
      currentSection = { title: trimmed.replace('# ', ''), type: 'roadmap', items: [] };
    } else if (trimmed.startsWith('## ')) {
      if (currentSection) sections.push(currentSection);
      currentSection = { title: trimmed.replace('## ', ''), type: 'roadmap', items: [] };
    } else if (trimmed.match(/^\d+\.\s+/)) {
      if (currentSection) {
        currentSection.items.push({ type: 'numbered', text: trimmed.replace(/^\d+\.\s+/, '') });
      }
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      if (currentSection) {
        currentSection.items.push({ type: 'bullet', text: trimmed.replace(/^[-*]\s+/, '') });
      }
    } else {
      if (!currentSection) {
        intro += trimmed + '\n';
      } else {
        currentSection.items.push({ type: 'paragraph', text: trimmed });
      }
    }
  }
  if (currentSection) sections.push(currentSection);
  return { intro, sections };
}

export default function StudentDashboard({ user, studentProfile, results, onTabChange, view = 'overview' }) {
  const latestResult = useMemo(() => {
    return results && results.length > 0 ? results[0] : null;
  }, [results]);

  const planText = useMemo(() => {
    return latestResult?.training_plan || studentProfile?.training_plan || '';
  }, [latestResult, studentProfile]);

  const studentKey = useMemo(() => {
    if (latestResult?.id) return `result_${latestResult.id}`;
    if (studentProfile?.id) return `survey_${studentProfile.id}`;
    return 'default';
  }, [latestResult, studentProfile]);

  const [completedItems, setCompletedItems] = useState({});

  useEffect(() => {
    if (studentKey) {
      const saved = localStorage.getItem(`roadmap_progress_${studentKey}`);
      setCompletedItems(saved ? JSON.parse(saved) : {});
    }
  }, [studentKey]);

  // Compute total keys in roadmap plan to determine progress
  const totalItemKeys = useMemo(() => {
    if (!planText) return [];
    const keys = [];
    const jsonPlan = tryParseJsonPlan(planText);
    if (jsonPlan) {
      jsonPlan.steps?.forEach((step) => {
        const items = [
          step.encouragement ? `Khích lệ: ${step.encouragement}` : null,
          step.practice_tip ? `Luyện tập: ${step.practice_tip}` : null,
          step.home_tip ? `Tại nhà: ${step.home_tip}` : null,
        ].filter(Boolean);
        items.forEach((text, subIdx) => {
          keys.push(`${step.step_order}_${step.skill_name}_${subIdx}_${text}`);
        });
      });
    } else {
      const parsed = parseRoadmap(planText);
      parsed.sections.forEach(section => {
        if (section.type === 'roadmap') {
          let currentStep = null;
          section.items.forEach((item, idx) => {
            if (item.type === 'numbered') {
              if (currentStep) {
                currentStep.subItems.forEach(sub => keys.push(`${currentStep.title}_${sub}`));
              }
              currentStep = { title: item.text, subItems: [] };
            } else if (item.type === 'bullet' || item.type === 'paragraph') {
              if (currentStep) currentStep.subItems.push(item.text);
            }
          });
          if (currentStep) {
            currentStep.subItems.forEach(sub => keys.push(`${currentStep.title}_${sub}`));
          }
        }
      });
    }
    return keys;
  }, [planText]);

  const checkedCount = useMemo(() => {
    return totalItemKeys.filter(k => completedItems[k]).length;
  }, [totalItemKeys, completedItems]);

  const progressPercentage = useMemo(() => {
    if (totalItemKeys.length === 0) return 0;
    return Math.round((checkedCount / totalItemKeys.length) * 100);
  }, [checkedCount, totalItemKeys]);

  // Streak, XP, Coins
  const streak = useMemo(() => {
    return latestResult ? (checkedCount % 5) + 3 : 0;
  }, [latestResult, checkedCount]);

  const xp = useMemo(() => {
    const baseRankScore = studentProfile?.ranking?.score || 0;
    return baseRankScore + (checkedCount * 100);
  }, [studentProfile, checkedCount]);

  const coins = useMemo(() => {
    return latestResult ? 150 + (checkedCount * 15) : 0;
  }, [latestResult, checkedCount]);

  // Compute Next Lesson / Task
  const nextLesson = useMemo(() => {
    if (!planText) return null;
    const jsonPlan = tryParseJsonPlan(planText);
    if (jsonPlan) {
      for (const step of jsonPlan.steps || []) {
        const items = [
          step.encouragement ? `Khích lệ: ${step.encouragement}` : null,
          step.practice_tip ? `Luyện tập: ${step.practice_tip}` : null,
          step.home_tip ? `Tại nhà: ${step.home_tip}` : null,
        ].filter(Boolean);
        for (let subIdx = 0; subIdx < items.length; subIdx++) {
          const key = `${step.step_order}_${step.skill_name}_${subIdx}_${items[subIdx]}`;
          if (!completedItems[key]) {
            return {
              title: `Topic: ${step.skill_name}`,
              description: items[subIdx],
              duration: '8 phút',
              questions: '6 câu hỏi',
            };
          }
        }
      }
    } else {
      const parsed = parseRoadmap(planText);
      for (const section of parsed.sections) {
        if (section.type === 'roadmap') {
          let currentStep = null;
          for (const item of section.items) {
            if (item.type === 'numbered') {
              currentStep = item.text;
            } else if (item.type === 'bullet' || item.type === 'paragraph') {
              const key = `${currentStep}_${item.text}`;
              if (!completedItems[key]) {
                return {
                  title: currentStep || "Chủ đề học tập",
                  description: item.text,
                  duration: '10 phút',
                  questions: '5 câu hỏi',
                };
              }
            }
          }
        }
      }
    }
    return null;
  }, [planText, completedItems]);

  // Progress filter
  const [skillFilter, setSkillFilter] = useState('all');

  const masteryList = useMemo(() => {
    if (!latestResult?.mastery) return [];
    return Object.entries(latestResult.mastery).map(([id, val]) => ({
      id,
      ...val
    })).sort((a, b) => b.probability - a.probability);
  }, [latestResult]);

  const filteredMastery = useMemo(() => {
    if (skillFilter === 'good') {
      return masteryList.filter(m => m.status === 'mastered');
    } else if (skillFilter === 'developing') {
      return masteryList.filter(m => m.status === 'developing');
    } else if (skillFilter === 'needs_work') {
      return masteryList.filter(m => m.status === 'weak');
    }
    return masteryList;
  }, [masteryList, skillFilter]);

  if (view === 'progress') {
    return (
      <div className="sd-container" style={{ padding: 0, margin: 0, background: 'transparent', boxShadow: 'none' }}>
        <div className="sd-header">
          <div>
            <h2 className="sd-title">Kỹ năng của em</h2>
            <div className="sd-tabs">
              <span onClick={() => onTabChange('student-dashboard')} className={`sd-tab ${view === 'overview' ? 'active' : ''}`}>Tổng quan</span>
              <span onClick={() => onTabChange('roadmap')} className={`sd-tab ${view === 'roadmap' ? 'active' : ''}`}>Lộ trình của em</span>
              <span onClick={() => onTabChange('progress')} className={`sd-tab ${view === 'progress' ? 'active' : ''}`}>Tiến bộ</span>
            </div>
          </div>
        </div>

        <div className="p-container-margin-mobile md:p-container-margin-desktop flex-1 mb-20 md:mb-0 max-w-7xl mx-auto w-full">
          <div className="mb-lg flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <p className="font-body-lg text-body-lg text-on-surface-variant">Theo dõi sự tiến bộ và tập trung vào những điểm cần cải thiện.</p>
            </div>
            {/* Filters */}
            <div className="flex flex-wrap gap-2">
              <button className="bg-primary text-on-primary rounded-full px-4 py-2 font-label-md text-label-md shadow-sm transition-transform hover:scale-105">Tất cả</button>
              <button className="bg-surface-container text-on-surface rounded-full px-4 py-2 font-label-md text-label-md shadow-sm transition-transform hover:scale-105 border border-outline-variant">Đang làm tốt</button>
              <button className="bg-surface-container text-on-surface rounded-full px-4 py-2 font-label-md text-label-md shadow-sm transition-transform hover:scale-105 border border-outline-variant">Đang tiến bộ</button>
              <button className="bg-surface-container text-on-surface rounded-full px-4 py-2 font-label-md text-label-md shadow-sm transition-transform hover:scale-105 border border-outline-variant">Nên luyện thêm</button>
            </div>
          </div>

          {/* Bento Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-lg mt-8">
            {/* Main Skills List */}
            <div className="md:col-span-8 grid gap-4 grid-cols-1 sm:grid-cols-2">
              {/* Skill Card 1 */}
              <div className="bg-surface-container-lowest rounded-2xl p-lg soft-shadow hover-lift flex flex-col justify-between border border-outline-variant/30">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-headline-card-sm text-headline-card-sm text-on-surface">Adverbs of Frequency</h3>
                    <span className="material-symbols-outlined text-tertiary">check_circle</span>
                  </div>
                  <div className="flex items-center gap-2 mb-sm">
                    <span className="bg-tertiary/10 text-tertiary font-caption text-caption px-2 py-1 rounded-md">Đang làm tốt</span>
                    <span className="font-caption text-caption text-outline">78% Mastery</span>
                  </div>
                  <div className="w-full h-2 rounded-full progress-bar-bg mb-4 overflow-hidden">
                    <div className="h-full progress-bar-fill-good rounded-full" style={{width: '78%'}}></div>
                  </div>
                  <div className="text-sm text-on-surface-variant mb-4 font-body-md">
                    <p>Đã hoàn thành: 45/50 câu</p>
                    <p>Lần tập cuối: Hôm qua</p>
                  </div>
                </div>
                <button className="w-full bg-surface-container-high text-primary hover:bg-primary hover:text-on-primary rounded-full py-2 font-label-md text-label-md transition-colors mt-auto border border-primary/20">Xem chi tiết</button>
              </div>

              {/* Skill Card 2 */}
              <div className="bg-surface-container-lowest rounded-2xl p-lg soft-shadow hover-lift flex flex-col justify-between border border-outline-variant/30">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-headline-card-sm text-headline-card-sm text-on-surface">Comparative Adjectives</h3>
                    <span className="material-symbols-outlined text-tertiary">check_circle</span>
                  </div>
                  <div className="flex items-center gap-2 mb-sm">
                    <span className="bg-tertiary/10 text-tertiary font-caption text-caption px-2 py-1 rounded-md">Đang làm tốt</span>
                    <span className="font-caption text-caption text-outline">74% Mastery</span>
                  </div>
                  <div className="w-full h-2 rounded-full progress-bar-bg mb-4 overflow-hidden">
                    <div className="h-full progress-bar-fill-good rounded-full" style={{width: '74%'}}></div>
                  </div>
                  <div className="text-sm text-on-surface-variant mb-4 font-body-md">
                    <p>Đã hoàn thành: 38/50 câu</p>
                    <p>Lần tập cuối: 2 ngày trước</p>
                  </div>
                </div>
                <button className="w-full bg-surface-container-high text-primary hover:bg-primary hover:text-on-primary rounded-full py-2 font-label-md text-label-md transition-colors mt-auto border border-primary/20">Xem chi tiết</button>
              </div>

              {/* Skill Card 3 */}
              <div className="bg-surface-container-lowest rounded-2xl p-lg soft-shadow hover-lift flex flex-col justify-between border border-outline-variant/30">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-headline-card-sm text-headline-card-sm text-on-surface">Must / Mustn't</h3>
                    <span className="material-symbols-outlined text-secondary-container">trending_up</span>
                  </div>
                  <div className="flex items-center gap-2 mb-sm">
                    <span className="bg-secondary-container/10 text-secondary-container font-caption text-caption px-2 py-1 rounded-md">Đã nắm khá tốt</span>
                    <span className="font-caption text-caption text-outline">71% Mastery</span>
                  </div>
                  <div className="w-full h-2 rounded-full progress-bar-bg mb-4 overflow-hidden">
                    <div className="h-full bg-secondary-container rounded-full" style={{width: '71%'}}></div>
                  </div>
                  <div className="text-sm text-on-surface-variant mb-4 font-body-md">
                    <p>Đã hoàn thành: 30/45 câu</p>
                    <p>Lần tập cuối: 3 ngày trước</p>
                  </div>
                </div>
                <button className="w-full bg-surface-container-high text-primary hover:bg-primary hover:text-on-primary rounded-full py-2 font-label-md text-label-md transition-colors mt-auto border border-primary/20">Xem chi tiết</button>
              </div>

              {/* Skill Card 4 */}
              <div className="bg-error-container/20 rounded-2xl p-lg soft-shadow hover-lift flex flex-col justify-between border border-error/20">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-headline-card-sm text-headline-card-sm text-on-surface">Food and Tableware</h3>
                    <span className="material-symbols-outlined text-error">warning</span>
                  </div>
                  <div className="flex items-center gap-2 mb-sm">
                    <span className="bg-error/10 text-error font-caption text-caption px-2 py-1 rounded-md">Nên luyện thêm</span>
                    <span className="font-caption text-caption text-outline">48% Mastery</span>
                  </div>
                  <div className="w-full h-2 rounded-full progress-bar-bg mb-4 overflow-hidden">
                    <div className="h-full bg-error rounded-full" style={{width: '48%'}}></div>
                  </div>
                  <div className="text-sm text-on-surface-variant mb-4 font-body-md">
                    <p>Đã hoàn thành: 15/40 câu</p>
                    <p>Lần tập cuối: Tuần trước</p>
                  </div>
                </div>
                <button className="w-full bg-secondary text-on-secondary hover:bg-secondary/90 rounded-full py-2 font-label-md text-label-md transition-colors mt-auto shadow-sm">Luyện tập ngay</button>
              </div>
            </div>

            {/* Right Side Panel */}
            <div className="md:col-span-4 flex flex-col gap-lg">
              {/* Insight Card */}
              <div className="bg-gradient-to-br from-primary/10 to-surface-variant rounded-2xl p-lg soft-shadow border border-primary/20 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl -mr-10 -mt-10"></div>
                <div className="flex items-center gap-2 mb-4 relative z-10">
                  <span className="material-symbols-outlined text-primary text-3xl">lightbulb</span>
                  <h3 className="font-headline-card-sm text-headline-card-sm text-primary">Vì sao em nên học kỹ năng này?</h3>
                </div>
                <p className="font-body-md text-body-md text-on-surface-variant mb-4 relative z-10">
                  Việc nắm vững <strong>Past Simple Irregular Verbs</strong> (Động từ bất quy tắc) giúp em kể những câu chuyện thú vị đã xảy ra trong quá khứ một cách tự nhiên hơn, giống như người bản xứ vậy!
                </p>
                <div className="bg-surface-container-lowest/80 backdrop-blur-sm rounded-xl p-4 border border-outline-variant/30 relative z-10">
                  <p className="font-label-md text-label-md text-on-surface mb-2">Ví dụ:</p>
                  <div className="flex gap-2 items-center text-sm font-body-md">
                    <span className="text-error line-through">I goed to the park.</span>
                    <span className="material-symbols-outlined text-outline text-sm">arrow_forward</span>
                    <span className="text-tertiary-container font-bold">I went to the park.</span>
                  </div>
                </div>
              </div>

              {/* Action Card */}
              <div className="bg-surface-container-lowest rounded-2xl p-lg soft-shadow border border-outline-variant/30 flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-primary-container flex items-center justify-center text-on-primary shrink-0">
                  <span className="material-symbols-outlined text-3xl">psychology</span>
                </div>
                <div>
                  <h4 className="font-label-md text-label-md text-on-surface mb-1">Gợi ý ôn tập</h4>
                  <p className="font-caption text-caption text-on-surface-variant mb-2">Hệ thống thấy em hay nhầm "Some/Any". Làm 1 bài test nhỏ nhé?</p>
                  <button className="text-primary font-label-md text-label-md hover:underline flex items-center gap-1">
                    Làm test 5 phút <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // OVERVIEW TAB (Bento Grid)
  return (
    <div className="sd-container">
      <div className="sd-header">
        <div>
          <h2 className="sd-title">Chào {user?.name || 'học sinh'}, hôm nay em muốn học gì?</h2>
          <div className="sd-tabs">
            <span onClick={() => onTabChange('student-dashboard')} className={`sd-tab ${view === 'overview' ? 'active' : ''}`}>Tổng quan</span>
            <span onClick={() => onTabChange('roadmap')} className={`sd-tab ${view === 'roadmap' ? 'active' : ''}`}>Lộ trình của em</span>
            <span onClick={() => onTabChange('progress')} className={`sd-tab ${view === 'progress' ? 'active' : ''}`}>Tiến bộ</span>
          </div>
        </div>
      </div>

      <div className="sd-top-grid">
        {/* Hero Card */}
        <div className="sd-hero-card">
          <div className="sd-hero-bg"></div>
          <div className="sd-hero-img">
            <img 
              alt="Medi Bee Mascot" 
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBms-463sLWso2Ge_0HWfvhBffOd_RqPUHgteHq-R83321nXcXBf1tWKVHB7PUqz62VvsKKGt8po4oTPrLCwuRqZlufivDBPV4rSihUWBdsF6uyQtPP5woM1JDtdk013k_MqSwTaSVnjH1GebGyTucTDnPHXqGvmZc6pn2lxNxsD4Wt-2Ym7QjxTTHciRgm43_MYRWpbChYGHLrewsNT8lsWmpqmzZ7ROIYLAcG-yhpXoOddP2itEgm"
            />
          </div>
          <div className="sd-hero-content">
            <div className="sd-hero-badge">
              Trình độ hiện tại
            </div>
            <h3 className="sd-hero-level">{latestResult ? `${latestResult.cefr} — ${latestResult.result_level}` : 'Chưa đánh giá'}</h3>
            <p className="sd-hero-desc">
              {latestResult ? 'Em đang làm rất tốt. Hãy hoàn thành các bài học tiếp theo trên lộ trình của em.' : 'Hãy hoàn thành bài khảo sát đầu vào để Medi Bee xây dựng lộ trình học tập cá nhân hóa dành riêng cho em.'}
            </p>
            <div className="sd-hero-actions">
              {latestResult ? (
                <>
                  <button onClick={() => onTabChange('roadmap')} className="sd-btn-primary">
                    Tiếp tục học
                  </button>
                  <button onClick={() => onTabChange('roadmap')} className="sd-btn-secondary">
                    Xem lộ trình
                  </button>
                </>
              ) : (
                <button onClick={() => onTabChange('survey')} className="sd-btn-danger">
                  Bắt đầu khảo sát
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Next Task Card */}
        <div className="sd-next-card">
          <div>
            <div className="sd-next-header">
              <div className="sd-next-icon">
                <BookOpen size={24} />
              </div>
              <span className="sd-status-badge">
                <CheckCircle2 size={12} /> Sẵn sàng
              </span>
            </div>
            <p className="sd-next-label">Bài học tiếp theo</p>
            {nextLesson ? (
              <>
                <h3 className="sd-next-title">{nextLesson.title}</h3>
                <p className="sd-next-desc">{nextLesson.description}</p>
                <div className="sd-next-meta">
                  <span><Clock size={12} /> {nextLesson.duration}</span>
                  <span><GraduationCap size={12} /> {nextLesson.questions}</span>
                </div>
              </>
            ) : (
              <>
                <h3 className="sd-next-title">Khảo sát năng lực</h3>
                <p className="sd-next-desc">Xác định điểm mạnh, điểm yếu với bài khảo sát 15 phút.</p>
              </>
            )}
          </div>
          <button 
            onClick={() => onTabChange(latestResult ? 'roadmap' : 'survey')} 
            className="sd-next-btn"
          >
            {latestResult ? 'Bắt đầu ngay' : 'Khảo sát ngay'}
          </button>
        </div>
      </div>

      {/* KPI Row */}
      <div className="sd-kpi-grid">
        {/* Progress Circular KPI */}
        <div className="sd-kpi-card">
          <div className="sd-circular-progress">
            <svg viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="15.915" fill="none" stroke="#e3dfff" strokeWidth="4"></circle>
              <circle cx="18" cy="18" r="15.915" fill="none" stroke="#35299d" strokeWidth="4"
                      strokeDasharray={`${progressPercentage}, 100`}></circle>
            </svg>
            <div className="sd-circular-text">{progressPercentage}%</div>
          </div>
          <div>
            <p className="sd-kpi-label">Tiến độ lộ trình</p>
            <p className="sd-kpi-val">{progressPercentage}%</p>
          </div>
        </div>

        {/* Streak */}
        <div className="sd-kpi-card">
          <div className="sd-kpi-icon flame">
            <Flame size={24} />
          </div>
          <div>
            <p className="sd-kpi-label">Chuỗi học tập</p>
            <p className="sd-kpi-val">{streak} <span>ngày</span></p>
          </div>
        </div>

        {/* XP */}
        <div className="sd-kpi-card">
          <div className="sd-kpi-icon star">
            <Star size={24} />
          </div>
          <div>
            <p className="sd-kpi-label">Kinh nghiệm</p>
            <p className="sd-kpi-val">{xp.toLocaleString()} <span>XP</span></p>
          </div>
        </div>

        {/* Coins */}
        <div className="sd-kpi-card">
          <div className="sd-kpi-icon coins">
            <Coins size={24} />
          </div>
          <div>
            <p className="sd-kpi-label">Xu tích lũy</p>
            <p className="sd-kpi-val">{coins}</p>
          </div>
        </div>
      </div>

      <div className="sd-bottom-grid">
        {/* Assigned tasks */}
        <div className="sd-section-card">
          <div className="sd-section-header">
            <h3 className="sd-section-title">Nhiệm vụ lộ trình</h3>
            <button onClick={() => onTabChange('roadmap')} className="sd-link">Xem tất cả</button>
          </div>
          {nextLesson ? (
            <div className="sd-task-item">
              <div className="sd-task-left">
                <div className="sd-task-icon">
                  <ClipboardCheck size={20} />
                </div>
                <div>
                  <h4 className="sd-task-title">{nextLesson.title}</h4>
                  <p className="sd-task-desc">{nextLesson.description}</p>
                </div>
              </div>
              <span className="sd-task-badge">Chưa bắt đầu</span>
            </div>
          ) : (
            <div className="sd-empty-state">
              {latestResult ? 'Chúc mừng! Em đã hoàn thành tất cả nhiệm vụ.' : 'Vui lòng hoàn thành khảo sát để nhận nhiệm vụ.'}
            </div>
          )}
        </div>

        {/* Weekly Chart */}
        <div className="sd-section-card">
          <div className="sd-section-header">
            <h3 className="sd-section-title">Tiến độ tuần này</h3>
            <span style={{fontSize: '12px', color: '#787584'}}>Thống kê 7 ngày qua</span>
          </div>
          <div className="sd-chart-container">
            <div className="sd-chart-bar" style={{height: '20%'}}></div>
            <div className="sd-chart-bar" style={{height: '40%'}}></div>
            <div className="sd-chart-bar active" style={{height: '80%'}}></div>
            <div className="sd-chart-bar" style={{height: '30%'}}></div>
            <div className="sd-chart-bar" style={{height: '10%'}}></div>
            <div className="sd-chart-bar" style={{height: '0%'}}></div>
            <div className="sd-chart-bar" style={{height: '0%'}}></div>
          </div>
          <div className="sd-chart-labels">
            <span>T2</span><span>T3</span><span>T4</span><span>T5</span><span>T6</span><span>T7</span><span>CN</span>
          </div>
        </div>
      </div>
    </div>
  );
}
