/**
 * Bayesian Knowledge Tracing (BKT) Engine — Port 1:1 từ domain/bkt.py + knowledge_graph.py
 * Pure math, không I/O, chạy hoàn toàn offline trên trình duyệt.
 */

// ── Knowledge Graph ──────────────────────────────────────────────────────────

const SKILLS = {
  "G3U04-VOC": { name: "Bộ phận cơ thể (eyes, nose, hands...)", grade: 3 },
  "G3U04-PAT": { name: "Touch your... / These are my...", grade: 3 },
  "G3U09-VOC": { name: "Màu sắc (red, blue, green...)", grade: 3 },
  "G3U09-PAT": { name: "What colour is it? - It's...", grade: 3 },
  "G3U11-VOC": { name: "Gia đình (father, mother, brother...)", grade: 3 },
  "G3U11-PAT": { name: "Who's that? - He's my father", grade: 3 },
  "G3U14-VOC": { name: "Đồ vật phòng ngủ (bed, lamp, picture...)", grade: 3 },
  "G3U14-PAT": { name: "Vị trí: in / on / under / behind", grade: 3 },
  "G4U01-VOC": { name: "Bạn bè & quốc tịch", grade: 4 },
  "G4U01-PAT": { name: "Where are you from? - I'm from...", grade: 4 },
  "G4U02-VOC": { name: "Thời gian & giờ", grade: 4 },
  "G4U02-PAT": { name: "What time is it? - It's...o'clock", grade: 4 },
  "G4U03-VOC": { name: "Ngày trong tuần & thói quen", grade: 4 },
  "G4U03-PAT": { name: "What do you do on Mondays? - I...", grade: 4 },
  "G4U05-VOC": { name: "Khả năng - Things we can do", grade: 4 },
  "G4U05-PAT": { name: "Can you...? - Yes, I can / No, I can't", grade: 4 },
}

const PREREQUISITES = {
  "G3U04-PAT": ["G3U04-VOC"],
  "G3U09-VOC": ["G3U04-PAT"],
  "G3U09-PAT": ["G3U09-VOC"],
  "G3U11-VOC": ["G3U09-PAT"],
  "G3U11-PAT": ["G3U11-VOC"],
  "G3U14-VOC": ["G3U11-PAT"],
  "G3U14-PAT": ["G3U14-VOC"],
  "G4U01-VOC": ["G3U14-PAT"],
  "G4U01-PAT": ["G4U01-VOC"],
  "G4U02-VOC": ["G4U01-PAT"],
  "G4U02-PAT": ["G4U02-VOC"],
  "G4U03-VOC": ["G4U02-PAT"],
  "G4U03-PAT": ["G4U03-VOC"],
  "G4U05-VOC": ["G4U03-PAT"],
  "G4U05-PAT": ["G4U05-VOC"],
}

function get_skill_name(skill_id) {
  return (SKILLS[skill_id] || {}).name || skill_id
}

function get_prerequisites(skill_id) {
  return [...(PREREQUISITES[skill_id] || [])]
}

function has_skill(skill_id) {
  return skill_id in SKILLS
}

function trace_root_causes(skill_id, mastery_map, threshold = 0.5) {
  if (!has_skill(skill_id)) return []
  const prob = (mastery_map[skill_id] || {}).probability ?? 1.0
  if (prob >= threshold) return []

  const prereqs = get_prerequisites(skill_id)
  if (!prereqs.length) return [skill_id]

  const roots = []
  for (const p of prereqs) {
    const sub = trace_root_causes(p, mastery_map, threshold)
    if (sub.length) {
      roots.push(...sub)
    } else if (((mastery_map[p] || {}).probability ?? 1.0) < threshold) {
      roots.push(p)
    }
  }
  // dedupe preserving order
  return [...new Set(roots)]
}

// ── BKT Parameters ──────────────────────────────────────────────────────────

const PRIOR = 0.3
const TRANSIT = 0.3
const GUESS = 0.2
const SLIP = 0.1

const THRESHOLD_MASTERED = 0.7
const THRESHOLD_DEVELOPING = 0.45
const ROOT_THRESHOLD = 0.5

function _status(probability) {
  if (probability >= THRESHOLD_MASTERED) return "mastered"
  if (probability >= THRESHOLD_DEVELOPING) return "developing"
  return "weak"
}

// ── Core BKT ────────────────────────────────────────────────────────────────

function update_probability(prior_p, correct) {
  let posterior
  if (correct) {
    const num = prior_p * (1 - SLIP)
    const den = prior_p * (1 - SLIP) + (1 - prior_p) * GUESS
    posterior = den > 0 ? num / den : prior_p
  } else {
    const num = prior_p * SLIP
    const den = prior_p * SLIP + (1 - prior_p) * (1 - GUESS)
    posterior = den > 0 ? num / den : 0.0
  }
  const updated = posterior + (1 - posterior) * TRANSIT
  return Math.max(0.0, Math.min(1.0, updated))
}

function compute_mastery(answers) {
  const mastery = {}
  for (const a of answers || []) {
    const sid = a.skill_id
    if (sid && !(sid in mastery)) {
      mastery[sid] = {
        probability: PRIOR,
        correct: 0,
        total: 0,
        skill_name: get_skill_name(sid),
        status: _status(PRIOR),
        is_default: true,
      }
    }
  }
  for (const a of answers || []) {
    const sid = a.skill_id
    if (!sid || !(sid in mastery)) continue
    const m = mastery[sid]
    m.is_default = false
    m.total += 1
    const is_correct = !!a.correct
    if (is_correct) m.correct += 1
    m.probability = update_probability(m.probability, is_correct)
    m.status = _status(m.probability)
  }
  return mastery
}

function diagnose_gaps(mastery_map, skill_ids) {
  const gaps = []
  const skills_to_check = new Set(skill_ids || Object.keys(mastery_map))

  function _expand(sid) {
    for (const p of get_prerequisites(sid)) {
      if (!skills_to_check.has(p)) {
        skills_to_check.add(p)
        _expand(p)
      }
    }
  }

  for (const sid of [...skills_to_check]) _expand(sid)

  for (const sid of skills_to_check) {
    if (!has_skill(sid)) {
      gaps.push({
        skill_id: sid,
        skill_name: get_skill_name(sid),
        probability: (mastery_map[sid] || {}).probability || null,
        status: "unknown",
        severity: "unknown",
        root_causes: [],
        reason: `Kỹ năng '${sid}' không tồn tại trong đồ thị kiến thức — cần bổ sung dữ liệu.`,
      })
      continue
    }

    const prob = (mastery_map[sid] || {}).probability ?? PRIOR
    if (prob >= THRESHOLD_DEVELOPING) continue

    const roots = trace_root_causes(sid, mastery_map, ROOT_THRESHOLD)
    const severity = prob < 0.15 ? "high" : "medium"
    let reason = `Chưa nắm vững ${get_skill_name(sid)}`
    if (roots.length) {
      const root_names = roots.map(r => get_skill_name(r)).join(", ")
      reason += `. Gốc rễ: ${root_names}.`
    }

    gaps.push({
      skill_id: sid,
      skill_name: get_skill_name(sid),
      probability: Math.round(prob * 1000) / 1000,
      status: _status(prob),
      severity,
      root_causes: roots,
      reason,
    })
  }

  gaps.sort((a, b) => {
    if (a.severity !== "high" && b.severity === "high") return 1
    if (a.severity === "high" && b.severity !== "high") return -1
    return (a.probability || 0) - (b.probability || 0)
  })
  return gaps
}

function run_assessment(answers) {
  const mastery = compute_mastery(answers)
  const gaps = diagnose_gaps(mastery)
  return { mastery, gaps }
}

// ── Learning Steps (roadmap structure) ──────────────────────────────────────

const DIFFICULTY_MAP = { high: "easy", medium: "medium" }
const DURATION_MAP = { high: "20 phút", medium: "15 phút" }

function generate_learning_steps(mastery, gaps) {
  if (!gaps || !gaps.length) return []
  const steps = []
  let step_num = 0

  for (const g of gaps) {
    if (g.severity !== "high") continue
    step_num++
    const sid = g.skill_id || ""
    const prob = g.probability || 0
    steps.push({
      step_order: step_num,
      skill_id: sid,
      skill_name: g.skill_name || sid,
      current_mastery: Math.round(prob * 1000) / 1000,
      status: g.status || _status(prob),
      severity: "high",
      reason: g.reason || "Gốc rễ lỗ hổng — cần ưu tiên ôn trước",
      suggested_difficulty: "easy",
      estimated_duration: DURATION_MAP.high,
    })
  }

  for (const g of gaps) {
    if (g.severity !== "medium") continue
    step_num++
    const sid = g.skill_id || ""
    const prob = g.probability || 0
    let root_info = ""
    if (g.root_causes && g.root_causes.length) {
      const root_names = g.root_causes.map(r => get_skill_name(r))
      root_info = `. Tiên quyết: ${root_names.join(", ")}`
    }
    steps.push({
      step_order: step_num,
      skill_id: sid,
      skill_name: g.skill_name || sid,
      current_mastery: Math.round(prob * 1000) / 1000,
      status: g.status || _status(prob),
      severity: "medium",
      reason: (g.reason || "Cần củng cố thêm") + root_info,
      suggested_difficulty: DIFFICULTY_MAP.medium,
      estimated_duration: DURATION_MAP.medium,
    })
  }

  return steps
}

// ── Offline Training Plan Fallback (from plan_tool.py:193) ─────────────────

function generate_offline_plan(mastery, gaps, student_name) {
  const steps = generate_learning_steps(mastery, gaps)
  if (!steps.length) {
    return {
      summary: `${student_name || "Em"} đã nắm vững tất cả kỹ năng!`,
      steps: [],
      closing: "Làm tốt lắm! Hãy tiếp tục luyện tập đều đặn.",
    }
  }

  const plan_steps = steps.map(s => ({
    step_order: s.step_order,
    skill_name: s.skill_name,
    encouragement: `Em hãy luyện kỹ năng '${s.skill_name}' nhé!`,
    practice_tip: `Làm 5-10 bài tập về '${s.skill_name}' với độ khó '${s.suggested_difficulty}'.`,
    home_tip: `Dành ${s.estimated_duration} mỗi ngày để ôn '${s.skill_name}'.`,
  }))

  return {
    summary: `${student_name || "Em"} cần ôn ${steps.length} kỹ năng theo lộ trình BKT.`,
    steps: plan_steps,
    closing: "Em làm tốt lắm! Hãy kiên trì mỗi ngày một chút!",
  }
}

export {
  SKILLS,
  PREREQUISITES,
  get_skill_name,
  get_prerequisites,
  has_skill,
  trace_root_causes,
  update_probability,
  compute_mastery,
  diagnose_gaps,
  run_assessment,
  generate_learning_steps,
  generate_offline_plan,
}
