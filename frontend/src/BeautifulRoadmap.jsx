import { useState, useEffect } from 'react';
import { BookOpen, Check, Lightbulb, HelpCircle, Star, Sparkles, Activity } from 'lucide-react';
import './BeautifulRoadmap.css';

// Simple bold markdown parser: replace **text** with <strong>text</strong>
function renderFormattedText(text) {
  if (!text) return '';
  const parts = text.split(/\*\*([^*]+)\*\*/g);
  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return <strong key={index} style={{ fontWeight: '700', color: '#111827' }}>{part}</strong>;
    }
    return part;
  });
}

export function parseRoadmap(text) {
  if (!text) return null;

  const lines = text.split('\n');
  const sections = [];
  let currentSection = {
    title: '',
    items: [],
    type: 'general' // 'general', 'comments', 'roadmap', 'tips'
  };

  let introText = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Check for section headers
    // Matches: ### (a) Nhận xét, ### Nhận xét, #### Nhận xét, **(a) Nhận xét**, etc.
    const headerMatch = line.match(/^(?:###|####|\*\*|##)\s*(?:\(\w\))?\s*(.*?)(?::|\*\*|\s*)$/i);
    const isSectionHeader = headerMatch && (
      line.startsWith('###') || 
      line.startsWith('####') || 
      line.startsWith('##') ||
      (line.startsWith('**') && line.endsWith('**') && line.length < 100)
    );

    if (isSectionHeader) {
      const title = headerMatch[1].replace(/\*\*|:/g, '').trim();
      let type = 'general';
      
      // Categorize section by keywords
      const titleLower = title.toLowerCase();
      if (titleLower.includes('nhận xét') || titleLower.includes('chung') || titleLower.includes('trình độ')) {
        type = 'comments';
      } else if (titleLower.includes('danh sách') || titleLower.includes('bài tập') || titleLower.includes('lộ trình') || titleLower.includes('giai đoạn') || titleLower.includes('kế hoạch')) {
        type = 'roadmap';
      } else if (titleLower.includes('lời khuyên') || titleLower.includes('khuyên') || titleLower.includes('phương pháp') || titleLower.includes('đề xuất')) {
        type = 'tips';
      }

      if (currentSection.title || currentSection.items.length > 0) {
        sections.push(currentSection);
      }

      currentSection = {
        title: title,
        items: [],
        type: type
      };
    } else {
      if (sections.length === 0 && !currentSection.title) {
        introText.push(line);
      } else {
        const numMatch = line.match(/^(?:\d+\.|-\s+\d+\.)\s*(.*)$/);
        const bulletMatch = line.match(/^(?:-\s+|\*\s+|\+\s+)(.*)$/);
        const stepSubMatch = line.match(/^\*\*(Bước|Giai đoạn)\s*\d+:\s*(.*?)\*\*/i);

        if (stepSubMatch) {
          currentSection.items.push({
            type: 'step_header',
            text: stepSubMatch[0].replace(/\*\*/g, '').trim()
          });
        } else if (numMatch) {
          currentSection.items.push({
            type: 'numbered',
            text: numMatch[1].trim()
          });
        } else if (bulletMatch) {
          currentSection.items.push({
            type: 'bullet',
            text: bulletMatch[1].trim()
          });
        } else {
          currentSection.items.push({
            type: 'paragraph',
            text: line
          });
        }
      }
    }
  }

  if (currentSection.title || currentSection.items.length > 0) {
    sections.push(currentSection);
  }

  return {
    intro: introText.join('\n'),
    sections
  };
}

function tryParseJsonPlan(planText) {
  if (!planText) return null;
  if (typeof planText === 'object') return planText;
  if (typeof planText !== 'string') return null;
  const trimmed = planText.trim();
  if (!trimmed) return null;
  if (!(trimmed.startsWith('{') || trimmed.startsWith('['))) return null;
  try {
    return JSON.parse(trimmed);
  } catch {
    return null;
  }
}

function normalizeJsonPlan(plan) {
  if (!plan || typeof plan !== 'object') return null;
  const steps = Array.isArray(plan.steps) ? plan.steps : [];
  if (steps.length === 0 && !plan.summary && !plan.closing) return null;
  const normalizedSteps = steps
    .map((s, idx) => {
      const stepOrder = Number.isFinite(Number(s.step_order)) ? Number(s.step_order) : (idx + 1);
      const skillName = typeof s.skill_name === 'string' ? s.skill_name : `Bước ${stepOrder}`;
      const skillId = typeof s.skill_id === 'string' ? s.skill_id : null;
      const encouragement = typeof s.encouragement === 'string' ? s.encouragement : null;
      const practiceTip = typeof s.practice_tip === 'string' ? s.practice_tip : null;
      const homeTip = typeof s.home_tip === 'string' ? s.home_tip : null;
      return { step_order: stepOrder, skill_name: skillName, skill_id: skillId, encouragement, practice_tip: practiceTip, home_tip: homeTip };
    })
    .sort((a, b) => a.step_order - b.step_order);

  return {
    summary: typeof plan.summary === 'string' ? plan.summary : '',
    closing: typeof plan.closing === 'string' ? plan.closing : '',
    steps: normalizedSteps,
  };
}

function JsonRoadmap({ plan, completedItems, toggleItem }) {
  const hasContent = !!plan.summary || !!plan.closing || (plan.steps && plan.steps.length > 0);
  if (!hasContent) return null;

  return (
    <div className="roadmap-container">
      {plan.summary && (
        <div className="roadmap-intro-card">
          <div className="roadmap-intro-avatar">
            <Sparkles size={24} />
          </div>
          <p className="roadmap-intro-text">{renderFormattedText(plan.summary)}</p>
        </div>
      )}

      {plan.steps?.length > 0 && (
        <div className="roadmap-section-timeline">
          <h4 className="roadmap-section-title timeline">
            <BookOpen size={20} color="var(--roadmap-primary)" />
            <span>Lộ trình gợi ý</span>
          </h4>

          <div className="roadmap-timeline">
            <div className="roadmap-timeline-line"></div>
            {plan.steps.map((step, idx) => {
              const badgeClass = idx < 3 ? 'phase-green' : 'phase-blue';
              const badgeText = idx < 3 ? 'Ưu tiên cao' : 'Giai đoạn tiếp theo';

              const items = [
                step.encouragement ? `Khích lệ: ${step.encouragement}` : null,
                step.practice_tip ? `Luyện tập: ${step.practice_tip}` : null,
                step.home_tip ? `Tại nhà: ${step.home_tip}` : null,
              ].filter(Boolean);

              return (
                <div key={`${step.step_order}_${step.skill_id || step.skill_name}`} className="roadmap-timeline-node">
                  <div className="roadmap-timeline-dot">{idx + 1}</div>
                  <div className="roadmap-timeline-card">
                    <div className="roadmap-card-header">
                      <h5 className="roadmap-card-title">
                        {renderFormattedText(step.skill_name)}
                      </h5>
                      <span className={`roadmap-card-badge ${badgeClass}`}>{badgeText}</span>
                    </div>

                    {items.length > 0 && (
                      <div className="roadmap-exercises-list">
                        {items.map((text, subIdx) => {
                          const itemKey = `${step.step_order}_${step.skill_name}_${subIdx}_${text}`;
                          const isDone = !!completedItems[itemKey];
                          return (
                            <div
                              key={itemKey}
                              className={`roadmap-exercise-item ${isDone ? 'completed' : ''}`}
                              onClick={() => toggleItem(itemKey)}
                            >
                              <div className="roadmap-checkbox-container">
                                {isDone && <Check size={12} color="white" />}
                              </div>
                              <span className="roadmap-exercise-text">{renderFormattedText(text)}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {plan.closing && (
        <div className="roadmap-section-tips">
          <h4 className="roadmap-section-title tips">
            <Lightbulb size={20} color="var(--roadmap-warning)" />
            <span>Lời nhắn</span>
          </h4>
          <div className="roadmap-tips-grid">
            <div className="roadmap-tip-card">
              <div className="roadmap-tip-icon">
                <Star size={16} />
              </div>
              <p className="roadmap-tip-text">{renderFormattedText(plan.closing)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function BeautifulRoadmap({ planText, studentKey = 'default_student' }) {
  const [completedItems, setCompletedItems] = useState({});

  useEffect(() => {
    if (studentKey) {
      const saved = localStorage.getItem(`roadmap_progress_${studentKey}`);
      setCompletedItems(saved ? JSON.parse(saved) : {});
    }
  }, [studentKey]);

  const toggleItem = (itemText) => {
    const newCompleted = {
      ...completedItems,
      [itemText]: !completedItems[itemText]
    };
    setCompletedItems(newCompleted);
    if (studentKey) {
      localStorage.setItem(`roadmap_progress_${studentKey}`, JSON.stringify(newCompleted));
    }
  };

  const jsonPlanRaw = tryParseJsonPlan(planText);
  const jsonPlan = normalizeJsonPlan(jsonPlanRaw);
  if (jsonPlan) {
    return <JsonRoadmap plan={jsonPlan} completedItems={completedItems} toggleItem={toggleItem} />;
  }

  const parsed = parseRoadmap(planText);

  if (!parsed || (parsed.sections.length === 0 && !parsed.intro)) {
    return (
      <div className="history-training-plan" style={{ whiteSpace: 'pre-wrap' }}>
        {planText}
      </div>
    );
  }

  // Group steps for the roadmap timeline section
  const renderRoadmapSection = (section) => {
    const groupedSteps = [];
    let currentStep = null;
    let currentPhase = "";

    section.items.forEach((item, idx) => {
      if (item.type === 'step_header') {
        currentPhase = item.text;
      } else if (item.type === 'numbered') {
        if (currentStep) {
          groupedSteps.push(currentStep);
        }
        currentStep = {
          id: `step_${idx}`,
          title: item.text,
          phase: currentPhase,
          subItems: []
        };
      } else if (item.type === 'bullet') {
        if (currentStep) {
          currentStep.subItems.push(item.text);
        } else {
          groupedSteps.push({
            id: `step_b_${idx}`,
            title: item.text,
            phase: currentPhase,
            subItems: []
          });
        }
      } else if (item.type === 'paragraph') {
        if (currentStep) {
          currentStep.subItems.push(item.text);
        } else {
          groupedSteps.push({
            id: `step_p_${idx}`,
            title: item.text,
            phase: currentPhase,
            subItems: [],
            isParagraph: true
          });
        }
      }
    });

    if (currentStep) {
      groupedSteps.push(currentStep);
    }

    return (
      <div key={section.title} className="roadmap-section-timeline">
        <h4 className="roadmap-section-title timeline">
          <BookOpen size={20} color="var(--roadmap-primary)" />
          <span>{section.title}</span>
        </h4>
        
        <div className="roadmap-timeline">
          <div className="roadmap-timeline-line"></div>
          {groupedSteps.map((step, sIdx) => {
            const hasBadge = step.phase || sIdx < 3;
            const badgeClass = sIdx < 3 ? "phase-green" : "phase-blue";
            const badgeText = step.phase || (sIdx < 3 ? "Ưu tiên cao" : "Giai đoạn tiếp theo");

            return (
              <div key={step.id} className="roadmap-timeline-node">
                <div className="roadmap-timeline-dot">
                  {sIdx + 1}
                </div>
                <div className="roadmap-timeline-card">
                  <div className="roadmap-card-header">
                    <h5 className="roadmap-card-title">
                      {renderFormattedText(step.title)}
                    </h5>
                    {hasBadge && (
                      <span className={`roadmap-card-badge ${badgeClass}`}>
                        {badgeText}
                      </span>
                    )}
                  </div>
                  
                  {step.subItems.length > 0 && (
                    <div className="roadmap-exercises-list">
                      {step.subItems.map((sub, subIdx) => {
                        const itemKey = `${step.title}_${sub}`;
                        const isDone = !!completedItems[itemKey];
                        return (
                          <div 
                            key={subIdx} 
                            className={`roadmap-exercise-item ${isDone ? 'completed' : ''}`}
                            onClick={() => toggleItem(itemKey)}
                          >
                            <div className="roadmap-checkbox-container">
                              {isDone && <Check size={12} color="white" />}
                            </div>
                            <span className="roadmap-exercise-text">
                              {renderFormattedText(sub)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Render general tips/advice as cards
  const renderTipsSection = (section) => {
    const tipItems = section.items.filter(i => i.type === 'bullet' || i.type === 'numbered');
    const paragraphs = section.items.filter(i => i.type === 'paragraph');

    return (
      <div key={section.title} className="roadmap-section-tips">
        <h4 className="roadmap-section-title tips">
          <Lightbulb size={20} color="var(--roadmap-warning)" />
          <span>{section.title}</span>
        </h4>

        {paragraphs.length > 0 && (
          <div style={{ marginBottom: '14px', fontSize: '14px', color: '#4b5563', lineHeight: '1.6' }}>
            {paragraphs.map((p, idx) => <p key={idx} style={{ margin: '0 0 8px 0' }}>{p.text}</p>)}
          </div>
        )}

        <div className="roadmap-tips-grid">
          {tipItems.map((tip, idx) => {
            return (
              <div key={idx} className="roadmap-tip-card">
                <div className="roadmap-tip-icon">
                  <Star size={16} />
                </div>
                <p className="roadmap-tip-text">
                  {renderFormattedText(tip.text)}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="roadmap-container">
      {/* Intro greeting */}
      {parsed.intro && (
        <div className="roadmap-intro-card">
          <div className="roadmap-intro-avatar">
            <Sparkles size={24} />
          </div>
          <p className="roadmap-intro-text">
            {renderFormattedText(parsed.intro)}
          </p>
        </div>
      )}

      {/* Render sections */}
      {parsed.sections.map((sec) => {
        if (sec.type === 'comments') {
          return (
            <div key={sec.title} className="roadmap-section-comments">
              <h4 className="roadmap-section-title comments">
                <Activity size={20} color="var(--roadmap-secondary)" />
                <span>{sec.title}</span>
              </h4>
              <div className="roadmap-comments-content">
                {sec.items.map((item, idx) => (
                  <p key={idx} style={{ margin: '0 0 10px 0', lastChild: { margin: 0 } }}>
                    {renderFormattedText(item.text)}
                  </p>
                ))}
              </div>
            </div>
          );
        } else if (sec.type === 'roadmap') {
          return renderRoadmapSection(sec);
        } else if (sec.type === 'tips') {
          return renderTipsSection(sec);
        } else {
          // General default fallback for unclassified sections
          return (
            <div key={sec.title} className="roadmap-section-comments">
              <h4 className="roadmap-section-title" style={{ color: '#4b5563' }}>
                <HelpCircle size={20} />
                <span>{sec.title}</span>
              </h4>
              <div className="roadmap-comments-content">
                {sec.items.map((item, idx) => (
                  <p key={idx} style={{ margin: '0 0 10px 0' }}>
                    {renderFormattedText(item.text)}
                  </p>
                ))}
              </div>
            </div>
          );
        }
      })}
    </div>
  );
}
