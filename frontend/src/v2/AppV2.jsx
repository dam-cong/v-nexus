import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { 
  GraduationCap, 
  Users, 
  Trophy, 
  Plus, 
  Trash2, 
  Edit3, 
  Search, 
  X, 
  Award, 
  Sparkles, 
  Mail, 
  BookOpen, 
  Clock, 
  ArrowRight,
  TrendingUp,
  LayoutDashboard,
  Calendar,
  Settings,
  Bell,
  LogOut,
  ClipboardCheck,
  Database,
  FileText,
  AlertTriangle,
  Lightbulb,
  Menu,
  Key,
  BarChart3,
  CheckCircle2,
  Flame,
  Play,
  Target
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiFetch, OfflineError } from '../api';
import Login from '../pages/Login';
import LandingPage from '../pages/LandingPage';
import StudentSurvey from '../StudentSurvey';
import StudentHistory from '../StudentHistory';
import StudentRoadmap from '../StudentRoadmap';
import useOnlineStatus from '../offline/useOnlineStatus';
import { 
  seedFromStaticData, 
  getQuestions as getOfflineQuestions, 
  getPlacementTests as getOfflineTests,
  getStudents as getOfflineStudents,
  getTeachers as getOfflineTeachers,
  getRankings as getOfflineRankings,
  getTestResults as getOfflineTestResults,
  getStudentProfile as getOfflineStudentProfile,
  saveStudents,
  saveTeachers,
  saveRankings,
  saveTestResults,
  saveStudentProfile,
  saveQuestions,
  savePlacementTests
} from '../offline/db.js';
import { flushPendingResults } from '../offline/sync.js';
import { WifiOff, Wifi } from 'lucide-react';
import './index-v2.css';
import './AppV2.css';

// Legacy frontend modules still point to localhost:8000. In the V2 entry,
// transparently route those calls through the current origin so Vite/ngrok
// can proxy /api without changing any legacy source file.
if (typeof window !== 'undefined' && !window.__vnexusV2FetchInstalled) {
  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init) => {
    if (typeof input === 'string' && input.startsWith('http://localhost:8000')) {
      const relativeUrl = input.slice('http://localhost:8000'.length);
      return nativeFetch(`${window.location.origin}${relativeUrl}`, init);
    }
    return nativeFetch(input, init);
  };
  window.__vnexusV2FetchInstalled = true;
}

// Base API URL
const API_BASE = import.meta.env.VITE_API_BASE || "";

function App() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/" element={<LandingPage isAuthenticated={isAuthenticated} user={user} />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/app" replace /> : <Login />} />
      <Route
        path="/app/*"
        element={isAuthenticated ? <DashboardApp user={user} logout={logout} /> : <Navigate to="/login" replace />}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function DashboardApp({ user, logout }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [students, setStudents] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [rankings, setRankings] = useState([]);
  const [testResults, setTestResults] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [placementTests, setPlacementTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [testQuestions, setTestQuestions] = useState([]);
  const [questionSearch, setQuestionSearch] = useState('');
  const [questionSkillFilter, setQuestionSkillFilter] = useState('');
  const [questionDiffFilter, setQuestionDiffFilter] = useState('');
  const [editQuestionModal, setEditQuestionModal] = useState({ open: false, data: null });
  const [editTestModal, setEditTestModal] = useState({ open: false, data: null });
  const [showAddQuestionModal, setShowAddQuestionModal] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);
  const [addQuestionSearch, setAddQuestionSearch] = useState('');
  const [addQuestionSkillFilter, setAddQuestionSkillFilter] = useState('');
  const [addQuestionDiffFilter, setAddQuestionDiffFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Sub-tab states for grouped menu items
  const [userSubTab, setUserSubTab] = useState('students');
  const [assessmentSubTab, setAssessmentSubTab] = useState('test-results');
  // Which grouped menu is expanded in the sidebar (null = none)
  const [openGroup, setOpenGroup] = useState(null);

  // Student survey state
  const [studentActiveTab, setStudentActiveTab] = useState('student-dashboard');
  const [studentTestResults, setStudentTestResults] = useState([]);
  const [studentProfile, setStudentProfile] = useState(null);

  // Offline state
  const isOnline = useOnlineStatus();

  // Search queries
  const [studentSearch, setStudentSearch] = useState('');
  const [studentLevelFilter, setStudentLevelFilter] = useState('');
  const [teacherSearch, setTeacherSearch] = useState('');

  // Modals state
  const [studentModal, setStudentModal] = useState({ open: false, mode: 'create', data: null });
  const [teacherModal, setTeacherModal] = useState({ open: false, mode: 'create', data: null });

  // Form states
  const [surveyForm, setSurveyForm] = useState({
    name: '',
    email: '',
    grade: 'Lớp 6',
    years_studying_english: 1,
    learning_environment: 'school',
    self_assessment_level: 'A1',
    learning_goal: ''
  });

  const [studentForm, setStudentForm] = useState({
    name: '',
    email: '',
    grade: 'Lớp 6',
    password: ''
  });

  const [teacherForm, setTeacherForm] = useState({
    name: '',
    email: '',
    subject: '',
    password: ''
  });

  // Fetch all data
  const fetchStudents = async () => {
    try {
      if (!navigator.onLine) {
        const data = await getOfflineStudents();
        setStudents(data);
        return;
      }
      const res = await apiFetch('/api/students');
      if (res.ok) {
        const data = await res.json();
        setStudents(data);
        saveStudents(data);
      }
    } catch (err) {
      console.error("Error fetching students:", err);
    }
  };

  const fetchTeachers = async () => {
    try {
      if (!navigator.onLine) {
        const data = await getOfflineTeachers();
        setTeachers(data);
        return;
      }
      const res = await apiFetch('/api/teachers');
      if (res.ok) {
        const data = await res.json();
        setTeachers(data);
        saveTeachers(data);
      }
    } catch (err) {
      console.error("Error fetching teachers:", err);
    }
  };

  const fetchRankings = async () => {
    try {
      if (!navigator.onLine) {
        const data = await getOfflineRankings();
        setRankings(data);
        return;
      }
      const res = await apiFetch('/api/rankings');
      if (res.ok) {
        const data = await res.json();
        setRankings(data);
        saveRankings(data);
      }
    } catch (err) {
      console.error("Error fetching rankings:", err);
    }
  };

  const fetchTestResults = async () => {
    try {
      if (!navigator.onLine) {
        const data = await getOfflineTestResults();
        setTestResults(data);
        return;
      }
      const res = await apiFetch('/api/test-results');
      if (res.ok) {
        const data = await res.json();
        setTestResults(data);
        saveTestResults(data);
      }
    } catch (err) {
      console.error("Error fetching test results:", err);
    }
  };

  const fetchStudentTestResults = async () => {
    if (!user || !user.id) return;
    try {
      if (!navigator.onLine) {
        const data = await getOfflineTestResults();
        setStudentTestResults(data.filter(r => r.user_id === user.id));
        return;
      }
      const res = await apiFetch(`/api/test-results/student/${user.id}`);
      if (res.ok) {
        const data = await res.json();
        setStudentTestResults(data);
      }
    } catch (err) {
      console.error("Error fetching student test results:", err);
    }
  };

  const fetchStudentProfile = async () => {
    if (!user || !user.id || user.role !== 'hoc_sinh') return;
    try {
      if (!navigator.onLine) {
        const data = await getOfflineStudentProfile(user.id);
        if (data) setStudentProfile(data);
        return;
      }
      const res = await apiFetch(`/api/students/${user.id}`);
      if (res.ok) {
        const data = await res.json();
        setStudentProfile(data);
        saveStudentProfile(data);
      }
    } catch (err) {
      console.error("Error fetching student profile:", err);
    }
  };

  const fetchQuestions = async () => {
    try {
      if (!navigator.onLine) {
        const data = await getOfflineQuestions();
        setQuestions(data);
        return;
      }
      const res = await apiFetch('/api/questions');
      if (res.ok) {
        const data = await res.json();
        setQuestions(data);
        saveQuestions(data);
      }
    } catch (err) {
      console.error("Error fetching questions:", err);
    }
  };

  const fetchPlacementTests = async () => {
    try {
      if (!navigator.onLine) {
        const data = await getOfflineTests();
        setPlacementTests(data);
        return;
      }
      const res = await apiFetch('/api/placement-tests');
      if (res.ok) {
        const data = await res.json();
        setPlacementTests(data);
        savePlacementTests(data);
      }
    } catch (err) {
      console.error("Error fetching placement tests:", err);
    }
  };

  const fetchTestQuestions = async (testId) => {
    try {
      const res = await apiFetch(`/api/placement-tests/${testId}/questions`);
      if (res.ok) {
        const data = await res.json();
        setTestQuestions(data);
      }
    } catch (err) {
      console.error("Error fetching test questions:", err);
    }
  };

  // Update question
  const handleUpdateQuestion = async (questionId, data) => {
    try {
      const res = await apiFetch(`/api/questions/${questionId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
      if (res.ok) {
        triggerNotification("Cập nhật câu hỏi thành công!");
        setEditQuestionModal({ open: false, data: null });
        fetchQuestions();
      } else {
        const err = await res.json();
        triggerNotification(err.detail || "Lỗi cập nhật", "error");
      }
    } catch (err) {
      triggerNotification("Lỗi kết nối server", "error");
    }
  };

  // Delete question
  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa câu hỏi này?")) return;
    try {
      const res = await apiFetch(`/api/questions/${questionId}`, { method: 'DELETE' });
      if (res.ok) {
        triggerNotification("Đã xóa câu hỏi!");
        fetchQuestions();
      }
    } catch (err) {
      triggerNotification("Lỗi kết nối server", "error");
    }
  };

  // Update placement test
  const handleUpdateTest = async (testId, data) => {
    try {
      const res = await apiFetch(`/api/placement-tests/${testId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
      if (res.ok) {
        triggerNotification("Cập nhật bài test thành công!");
        setEditTestModal({ open: false, data: null });
        fetchPlacementTests();
      } else {
        const err = await res.json();
        triggerNotification(err.detail || "Lỗi cập nhật", "error");
      }
    } catch (err) {
      triggerNotification("Lỗi kết nối server", "error");
    }
  };

  // Delete placement test
  const handleDeleteTest = async (testId) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa bài test này?")) return;
    try {
      const res = await apiFetch(`/api/placement-tests/${testId}`, { method: 'DELETE' });
      if (res.ok) {
        triggerNotification("Đã xóa bài test!");
        setSelectedTest(null);
        setTestQuestions([]);
        fetchPlacementTests();
      }
    } catch (err) {
      triggerNotification("Lỗi kết nối server", "error");
    }
  };

  // Save test questions (replace all)
  const handleSaveTestQuestions = async (testId, questionIds) => {
    try {
      const res = await apiFetch(`/api/placement-tests/${testId}/questions`, {
        method: 'PUT',
        body: JSON.stringify(questionIds)
      });
      if (res.ok) {
        const data = await res.json();
        setTestQuestions(data);
        setShowAddQuestionModal(false);
        triggerNotification(`Đã cập nhật ${data.length} câu hỏi trong bài test!`);
      } else {
        const err = await res.json();
        triggerNotification(err.detail || "Lỗi cập nhật", "error");
      }
    } catch (err) {
      triggerNotification("Lỗi kết nối server", "error");
    }
  };

  // Remove a question from test
  const handleRemoveQuestionFromTest = async (testId, questionId) => {
    if (!window.confirm("Xóa câu hỏi này khỏi bài test?")) return;
    const newIds = testQuestions.filter(q => q.id !== questionId).map(q => q.id);
    await handleSaveTestQuestions(testId, newIds);
  };

  const loadAllData = async () => {
    setLoading(true);
    await Promise.all([fetchStudents(), fetchTeachers(), fetchRankings(), fetchTestResults()]);
    setLoading(false);
  };

  useEffect(() => {
    if (user?.role === 'hoc_sinh') {
      fetchStudentTestResults();
      fetchStudentProfile();
    } else {
      loadAllData();
    }
  }, [user?.id, user?.role]);

  // ── Seed IndexedDB from /data on mount (for offline use) ──────────────
  useEffect(() => {
    (async () => {
      const seeded = await seedFromStaticData();
      if (seeded) {
        console.log('[offline] IndexedDB seeded from /data');
        fetchQuestions();
        fetchPlacementTests();
      }
    })();
  }, []);

  useEffect(() => {
    const onRefresh = () => { fetchStudentTestResults(); };
    window.addEventListener('vnexus:refresh-roadmap', onRefresh);
    return () => window.removeEventListener('vnexus:refresh-roadmap', onRefresh);
  }, []);

  // ── Flush offline write queue when going back online ─────────────────────
  useEffect(() => {
    const handleOnline = async () => {
      if (user?.id) { // Only sync if logged in
        try {
          const syncedCount = await flushPendingResults();
          if (syncedCount > 0) {
            triggerNotification(`Đã đồng bộ ${syncedCount} kết quả khi offline!`);
            if (user?.role === 'hoc_sinh') {
              fetchStudentTestResults();
              fetchStudentProfile();
            } else {
              loadAllData();
            }
          }
        } catch (e) {
          console.error('[Sync] Failed to flush pending results:', e);
        }
      }
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, [user?.id, user?.role]);

  // Show auto-dismiss notifications
  const triggerNotification = (msg, type = 'success') => {
    setSuccessMsg({ message: msg, type });
    setTimeout(() => setSuccessMsg(null), 4000);
  };

  // Survey Form Submission
  const handleSurveySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Create Student (survey data stored as part of student profile)
      const studentRes = await apiFetch('/api/students', {
        method: 'POST',
        body: JSON.stringify({
          name: surveyForm.name,
          email: surveyForm.email,
          grade: surveyForm.grade,
          role_id: 1
        })
      });

      if (!studentRes.ok) {
        const errorDetail = await studentRes.json();
        throw new Error(errorDetail.detail || "Không thể tạo tài khoản học sinh");
      }

      triggerNotification("Học sinh đã được tạo thành công! Hãy cho học sinh làm bài kiểm tra trình độ.");
      
      // Reset survey form
      setSurveyForm({
        name: '',
        email: '',
        grade: 'Lớp 6',
        years_studying_english: 1,
        learning_environment: 'school',
        self_assessment_level: 'A1',
        learning_goal: ''
      });

      // Reload lists and switch tab
      await loadAllData();
      setActiveTab('students');

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Student CRUD
  const handleStudentSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const url = studentModal.mode === 'create' 
        ? '/api/students'
        : `/api/students/${studentModal.data.id}`;
      const method = studentModal.mode === 'create' ? 'POST' : 'PUT';

      const payload = { ...studentForm };
      if (!payload.password) delete payload.password;

      const res = await apiFetch(url, {
        method,
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errorDetail = await res.json();
        throw new Error(errorDetail.detail || "Lỗi thao tác trên học sinh");
      }

      triggerNotification(
        studentModal.mode === 'create' ? "Đã thêm học sinh thành công!" : "Đã cập nhật học sinh thành công!"
      );
      setStudentModal({ open: false, mode: 'create', data: null });
      fetchStudents();
      fetchRankings();
    } catch (err) {
      triggerNotification(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const deleteStudent = async (id) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa học sinh này không? Mọi thông tin xếp hạng và khảo sát liên quan sẽ bị xóa.")) return;
    try {
      const res = await apiFetch(`/api/students/${id}`, { method: 'DELETE' });
      if (res.ok) {
        triggerNotification("Đã xóa học sinh thành công.");
        fetchStudents();
        fetchRankings();
      }
    } catch (err) {
      triggerNotification("Không thể xóa học sinh", "error");
    }
  };

  const resetStudentPassword = async (id, name) => {
    if (!window.confirm(`Reset mật khẩu của "${name}" về mặc định (88888888)?`)) return;
    try {
      const res = await apiFetch(`/api/students/${id}/reset-password`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        triggerNotification(`Đã reset mật khẩu. Mật khẩu mới: ${data.new_password}`);
      }
    } catch (err) {
      triggerNotification("Không thể reset mật khẩu", "error");
    }
  };

  // Teacher CRUD
  const handleTeacherSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const url = teacherModal.mode === 'create' 
        ? '/api/teachers'
        : `/api/teachers/${teacherModal.data.id}`;
      const method = teacherModal.mode === 'create' ? 'POST' : 'PUT';

      const payload = { ...teacherForm };
      if (!payload.password) delete payload.password;

      const res = await apiFetch(url, {
        method,
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errorDetail = await res.json();
        throw new Error(errorDetail.detail || "Lỗi thao tác trên giáo viên");
      }

      triggerNotification(
        teacherModal.mode === 'create' ? "Đã thêm giáo viên thành công!" : "Đã cập nhật giáo viên thành công!"
      );
      setTeacherModal({ open: false, mode: 'create', data: null });
      fetchTeachers();
    } catch (err) {
      triggerNotification(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const deleteTeacher = async (id) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa giáo viên này không?")) return;
    try {
      const res = await apiFetch(`/api/teachers/${id}`, { method: 'DELETE' });
      if (res.ok) {
        triggerNotification("Đã xóa giáo viên thành công.");
        fetchTeachers();
      }
    } catch (err) {
      triggerNotification("Không thể xóa giáo viên", "error");
    }
  };

  const resetTeacherPassword = async (id, name) => {
    if (!window.confirm(`Reset mật khẩu của "${name}" về mặc định (88888888)?`)) return;
    try {
      const res = await apiFetch(`/api/teachers/${id}/reset-password`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        triggerNotification(`Đã reset mật khẩu. Mật khẩu mới: ${data.new_password}`);
      }
    } catch (err) {
      triggerNotification("Không thể reset mật khẩu", "error");
    }
  };

  // Live Score Incrementation for Rankings Leaderboard
  const incrementScore = async (ranking) => {
    try {
      const newScore = ranking.score + 10;
      let newLevel = ranking.level;
      if (newScore >= 80) newLevel = "Expert";
      else if (newScore >= 50) newLevel = "Intermediate";
      else if (newScore >= 20) newLevel = "Elementary";

      const res = await apiFetch(`/api/rankings/${ranking.id}`, {
        method: 'PUT',
        body: JSON.stringify({ score: newScore, level: newLevel })
      });

      if (res.ok) {
        triggerNotification(`Đã cộng 10 điểm cho học sinh!`, 'success');
        fetchRankings();
        fetchStudents();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Helper to resolve student/teacher details
  const getStudentName = (studentId) => {
    const student = students.find(s => s.id === studentId);
    return student ? student.name : `Học sinh #${studentId}`;
  };

  const getStudentEmail = (studentId) => {
    const student = students.find(s => s.id === studentId);
    return student ? student.email : '';
  };

  const getStudentGrade = (studentId) => {
    const student = students.find(s => s.id === studentId);
    return student ? student.grade : '';
  };

  // Avatar background colors based on name string hash
  const getAvatarColor = (name) => {
    if (!name) return '#4d44b5';
    const colors = ['#4d44b5', '#fb7d5b', '#27c26c', '#f59e0b', '#ff5b5b', '#a0a3bd'];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  // Filters
  const filteredStudents = students.filter(s => {
    const matchSearch = s.name.toLowerCase().includes(studentSearch.toLowerCase()) ||
      s.email.toLowerCase().includes(studentSearch.toLowerCase()) ||
      (s.grade && s.grade.toLowerCase().includes(studentSearch.toLowerCase()));
    const matchLevel = !studentLevelFilter || (s.ranking?.level || 'Beginner') === studentLevelFilter;
    return matchSearch && matchLevel;
  });

  const filteredTeachers = teachers.filter(t => 
    t.name.toLowerCase().includes(teacherSearch.toLowerCase()) ||
    t.email.toLowerCase().includes(teacherSearch.toLowerCase()) ||
    (t.subject && t.subject.toLowerCase().includes(teacherSearch.toLowerCase()))
  );

  // Sorting Rankings for top podium
  const sortedRankings = [...rankings].sort((a, b) => b.score - a.score);
  const podiumStudents = sortedRankings.slice(0, 3);

  // Total test results count
  const totalTestResults = testResults.length;
  const avgScore = rankings.length > 0 
    ? Math.round(rankings.reduce((acc, curr) => acc + curr.score, 0) / rankings.length)
    : 0;

  const sortedStudentResults = [...studentTestResults].sort(
    (a, b) => new Date(b.test_date || 0) - new Date(a.test_date || 0)
  );
  const latestStudentResult = sortedStudentResults[0];
  const studentPercent = Math.max(0, Math.min(100, Number(latestStudentResult?.percentage) || 0));
  const completedRoadmaps = studentTestResults.filter(result => result.roadmap_completed).length;

  return (
    <div className={`app-container ${user?.role === 'hoc_sinh' ? 'student-app' : 'staff-app'}`}>
      {/* Mobile Hamburger Toggle */}
      <button 
        className="mobile-menu-toggle" 
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        <Menu size={22} />
      </button>
      
      {/* Mobile Overlay */}
      <div 
        className={`mobile-overlay ${sidebarOpen ? 'visible' : ''}`} 
        onClick={() => setSidebarOpen(false)} 
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <Link className="sidebar-logo" to="/">
          <div className="sidebar-logo-icon"><img src="/logo-mark.png" alt="V-NEXUS SCHOOL" /></div>
          <div className="sidebar-logo-copy"><span>V-NEXUS SCHOOL</span><small>Adaptive learning</small></div>
        </Link>
        
        <div className="sidebar-menu">
          {/* STUDENT SIDEBAR */}
          {user?.role === 'hoc_sinh' ? (
            <>
              <button
                className={`menu-item ${studentActiveTab === 'student-dashboard' ? 'active' : ''}`}
                onClick={() => { setStudentActiveTab('student-dashboard'); setSidebarOpen(false); }}
              >
                <LayoutDashboard size={20} />
                <span>Tổng quan</span>
              </button>
              <button
                className={`menu-item ${studentActiveTab === 'survey' ? 'active' : ''}`}
                onClick={() => { setStudentActiveTab('survey'); setSidebarOpen(false); }}
              >
                <BookOpen size={20} />
                <span>Khảo sát đầu vào</span>
              </button>
              <button
                className={`menu-item ${studentActiveTab === 'roadmap' ? 'active' : ''}`}
                onClick={() => { setStudentActiveTab('roadmap'); fetchStudentTestResults(); if (!questions.length) fetchQuestions(); setSidebarOpen(false); }}
              >
                <Sparkles size={20} />
                <span>Lộ trình của em</span>
              </button>
              <button
                className={`menu-item ${studentActiveTab === 'progress' ? 'active' : ''}`}
                onClick={() => { setStudentActiveTab('progress'); setSidebarOpen(false); }}
              >
                <TrendingUp size={20} />
                <span>Tiến bộ</span>
              </button>
              <button
                className={`menu-item ${studentActiveTab === 'history' ? 'active' : ''}`}
                onClick={() => { setStudentActiveTab('history'); fetchStudentTestResults(); if (!questions.length) fetchQuestions(); setSidebarOpen(false); }}
              >
                <ClipboardCheck size={20} />
                <span>Lịch sử bài đánh giá</span>
              </button>
            </>
          ) : (
            <>
          {/* ADMIN/TEACHER SIDEBAR */}
          <button 
            className={`menu-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => { setActiveTab('dashboard'); setSidebarOpen(false); }}
          >
            <LayoutDashboard size={20} />
            <span>Tổng quan</span>
          </button>

          {/* Users tab: visible to admin and teacher */}
          {(user?.role === 'admin' || user?.role === 'giao_vien') && (
            <button
              className={`menu-item ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => { setActiveTab('users'); setUserSubTab('students'); fetchStudents(); setSidebarOpen(false); }}
            >
              <Users size={20} />
              <span>Người dùng</span>
            </button>
          )}

          <button 
            className={`menu-item ${activeTab === 'leaderboard' ? 'active' : ''}`}
            onClick={() => { setActiveTab('leaderboard'); fetchRankings(); fetchStudents(); setSidebarOpen(false); }}
          >
            <Trophy size={20} />
            <span>Bảng xếp hạng</span>
          </button>

          {/* Assessment tab: visible to admin and teacher */}
          {(user?.role === 'admin' || user?.role === 'giao_vien') && (
            <button
              className={`menu-item ${activeTab === 'assessment' ? 'active' : ''}`}
              onClick={() => { setActiveTab('assessment'); setAssessmentSubTab('test-results'); fetchTestResults(); fetchStudents(); setSidebarOpen(false); }}
            >
              <ClipboardCheck size={20} />
              <span>Đánh giá</span>
            </button>
          )}

          {/* Question Bank tab: visible to admin and teacher */}
          {(user?.role === 'admin' || user?.role === 'giao_vien') && (
            <button 
              className={`menu-item ${activeTab === 'questions' ? 'active' : ''}`}
              onClick={() => { setActiveTab('questions'); fetchQuestions(); setSidebarOpen(false); }}
            >
              <Database size={20} />
              <span>Ngân hàng câu hỏi</span>
            </button>
          )}
            </>
          )}
        </div>

        <div className="sidebar-footer">
          <div className="sidebar-footer-badge"><Sparkles size={15} /></div>
          <div><p>Học đúng trọng tâm</p><span>Tiến bộ mỗi ngày</span></div>
        </div>
      </aside>

      {/* Main Wrapper */}
      <div className="main-wrapper">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-title">
            <span className="header-eyebrow">
              {user?.role === 'hoc_sinh' ? 'Không gian học tập' : 'Trung tâm điều hành'}
            </span>
            <h1>
              {user?.role === 'hoc_sinh' ? (
                <>
                  {studentActiveTab === 'student-dashboard' && 'Tổng quan'}
                  {studentActiveTab === 'survey' && 'Khảo sát đầu vào'}
                  {studentActiveTab === 'roadmap' && 'Lộ trình của em'}
                  {studentActiveTab === 'progress' && 'Tiến bộ'}
                  {studentActiveTab === 'history' && 'Lịch sử bài đánh giá'}
                </>
              ) : (
                <>
                  {activeTab === 'dashboard' && 'Tổng quan'}
                  {activeTab === 'users' && userSubTab === 'students' && 'Danh sách Học sinh'}
                  {activeTab === 'users' && userSubTab === 'teachers' && 'Danh sách Giáo viên'}
                  {activeTab === 'leaderboard' && 'Bảng xếp hạng'}
                  {activeTab === 'assessment' && assessmentSubTab === 'survey' && 'Khảo sát đầu vào'}
                  {activeTab === 'assessment' && assessmentSubTab === 'test-results' && 'Kết quả kiểm tra trình độ'}
                  {activeTab === 'assessment' && assessmentSubTab === 'placement-tests' && 'Danh sách bài test'}
                  {activeTab === 'questions' && 'Ngân hàng câu hỏi'}
                </>
              )}
            </h1>
          </div>
          
          <div className="header-right">
            {/* Conditional Search bar in Header */}
            {activeTab === 'users' && userSubTab === 'students' && (
              <div className="header-search-filter" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div className="search-bar">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Tìm học sinh, email..."
                  value={studentSearch}
                  onChange={e => setStudentSearch(e.target.value)}
                />
              </div>
              <select
                value={studentLevelFilter}
                onChange={e => setStudentLevelFilter(e.target.value)}
                style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px', fontWeight: '600', color: 'var(--text-color)', background: 'white', cursor: 'pointer', minWidth: '130px' }}
              >
                <option value="">Tất cả trình độ</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Expert">Expert</option>
              </select>
              </div>
            )}
            {activeTab === 'users' && userSubTab === 'teachers' && (
              <div className="search-bar">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Tìm giáo viên, môn học..."
                  value={teacherSearch}
                  onChange={e => setTeacherSearch(e.target.value)}
                />
              </div>
            )}
            {activeTab === 'questions' && (
              <div className="search-bar">
                <Search size={18} />
                <input 
                  type="text" 
                  placeholder="Tìm câu hỏi, kỹ năng..." 
                  value={questionSearch}
                  onChange={e => setQuestionSearch(e.target.value)}
                />
              </div>
            )}
            
            <div className="icon-buttons">
              {isOnline ? (
                <span className="online-badge" title="Đang kết nối mạng">
                  <Wifi size={14} /> Online
                </span>
              ) : (
                <span className="offline-badge" title="Đang offline — dữ liệu vẫn sử dụng được">
                  <WifiOff size={14} /> Offline
                </span>
              )}
              <button className="icon-btn"><Bell size={18} /></button>
              <button className="icon-btn"><Settings size={18} /></button>
            </div>
            
            <div className="user-profile">
              <div className="user-info">
                <p className="user-name">{user?.name || 'Người dùng'}</p>
                <p className="user-role">
                  {user?.role === 'admin' ? 'Quản trị viên' : 
                   user?.role === 'giao_vien' ? 'Giáo viên' : 'Học sinh'}
                </p>
              </div>
              <div 
                className="user-avatar" 
                style={{ 
                  background: user?.role === 'admin' ? '#fb7d5b' : user?.role === 'giao_vien' ? '#4d44b5' : '#27c26c',
                  color: 'white', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  fontWeight: '700' 
                }}
              >
                {user?.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
              <button
                onClick={logout}
                className="icon-btn"
                title="Đăng xuất"
                style={{ marginLeft: '8px' }}
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </header>

        {/* Notifications */}
        {successMsg && (
          <div className={`toast toast-${successMsg.type}`}>
            <Sparkles size={18} color={successMsg.type === 'success' ? '#27c26c' : '#ff5b5b'} />
            <span style={{ fontSize: '14px', fontWeight: '700', color: '#303972' }}>{successMsg.message}</span>
          </div>
        )}

        {/* Content Area */}
        <main className="content-area">
          
          {/* ==========================================================
              STUDENT CONTENT
              ========================================================== */}
          {user?.role === 'hoc_sinh' ? (
            <>
              {studentActiveTab === 'survey' && (
                <StudentSurvey user={user} onTabChange={setStudentActiveTab} />
              )}
              {studentActiveTab === 'student-dashboard' && (
                <div className="student-home animate-fade-in">
                  <section className="student-welcome-hero">
                    <div className="student-welcome-copy">
                      <span className="student-welcome-kicker"><Sparkles size={15} /> Hành trình của em</span>
                      <h2>Chào {user?.name?.split(' ').slice(-1)[0] || 'em'}, hôm nay mình cùng tiến thêm một bước nhé!</h2>
                      <p>
                        {latestStudentResult
                          ? 'Lộ trình cá nhân đã sẵn sàng. Chỉ cần một chút đều đặn mỗi ngày để em tiến gần hơn tới mục tiêu.'
                          : 'Bắt đầu bằng một bài khảo sát ngắn để V-NEXUS SCHOOL hiểu điểm mạnh và thiết kế lộ trình phù hợp với em.'}
                      </p>
                      <button
                        className="student-hero-button"
                        onClick={() => {
                          if (latestStudentResult) {
                            setStudentActiveTab('roadmap');
                            fetchStudentTestResults();
                            if (!questions.length) fetchQuestions();
                          } else {
                            setStudentActiveTab('survey');
                          }
                        }}
                      >
                        <Play size={17} fill="currentColor" />
                        {latestStudentResult ? 'Tiếp tục lộ trình' : 'Bắt đầu đánh giá'}
                      </button>
                    </div>
                    <div className="student-hero-progress">
                      <div className="student-progress-ring" style={{ '--student-progress': `${studentPercent * 3.6}deg` }}>
                        <div><strong>{latestStudentResult ? `${studentPercent}%` : 'A1'}</strong><span>{latestStudentResult ? 'Kết quả gần nhất' : 'Sẵn sàng'}</span></div>
                      </div>
                      <div className="student-streak"><Flame size={18} /><span><strong>{studentTestResults.length || 0}</strong> cột mốc đã ghi nhận</span></div>
                    </div>
                    <div className="student-hero-shape shape-one" />
                    <div className="student-hero-shape shape-two" />
                  </section>

                  <div className="student-section-heading">
                    <div><span>ĐIỂM ĐẾN TIẾP THEO</span><h3>Em muốn làm gì hôm nay?</h3></div>
                    <p>Chọn một hoạt động để tiếp tục</p>
                  </div>

                  <section className="student-action-grid">
                    <button className="student-action-card assessment" onClick={() => setStudentActiveTab('survey')}>
                      <span className="student-action-icon"><ClipboardCheck size={22} /></span>
                      <span className="student-action-copy"><b>Đánh giá năng lực</b><small>Khám phá trình độ hiện tại của em</small></span>
                      <ArrowRight size={18} />
                    </button>
                    <button className="student-action-card roadmap" onClick={() => { setStudentActiveTab('roadmap'); fetchStudentTestResults(); if (!questions.length) fetchQuestions(); }}>
                      <span className="student-action-icon"><Target size={22} /></span>
                      <span className="student-action-copy"><b>Lộ trình của em</b><small>Học theo các bước được cá nhân hóa</small></span>
                      <ArrowRight size={18} />
                    </button>
                    <button className="student-action-card history" onClick={() => { setStudentActiveTab('history'); fetchStudentTestResults(); if (!questions.length) fetchQuestions(); }}>
                      <span className="student-action-icon"><BarChart3 size={22} /></span>
                      <span className="student-action-copy"><b>Xem thành tích</b><small>Nhìn lại kết quả và sự tiến bộ</small></span>
                      <ArrowRight size={18} />
                    </button>
                  </section>

                  <section className="student-insight-panel">
                    <div className="student-insight-title">
                      <div className="student-insight-icon"><GraduationCap size={23} /></div>
                      <div><span>HỒ SƠ HỌC TẬP</span><h3>Bức tranh năng lực của em</h3></div>
                    </div>
                    <div className="student-insight-stats">
                      <div><span>Trình độ hiện tại</span><strong>{latestStudentResult?.cefr || 'Chưa xác định'}</strong></div>
                      <div><span>Kết quả gần nhất</span><strong>{latestStudentResult ? `${studentPercent}%` : '—'}</strong></div>
                      <div><span>Lộ trình hoàn thành</span><strong>{completedRoadmaps}</strong></div>
                      <div><span>Kỹ năng cần ưu tiên</span><strong>{latestStudentResult?.gaps?.length || 0}</strong></div>
                    </div>
                    {!latestStudentResult && (
                      <div className="student-empty-tip"><Sparkles size={17} /> Hoàn thành khảo sát đầu tiên để mở khóa hồ sơ năng lực của em.</div>
                    )}
                  </section>
                </div>
              )}
              {studentActiveTab === 'roadmap' && (
                <StudentRoadmap
                  results={studentTestResults}
                  questions={questions}
                  studentProfile={studentProfile}
                  onStartSurvey={() => setStudentActiveTab('survey')}
                />
              )}
              {studentActiveTab === 'progress' && (
                <div className="student-progress-page animate-fade-in">
                  <section className="student-progress-banner">
                    <div><span><TrendingUp size={16} /> Tiến bộ của em</span><h2>Mỗi nỗ lực nhỏ đều tạo nên thay đổi lớn.</h2><p>V-NEXUS SCHOOL ghi nhận kết quả sau từng lần đánh giá để em luôn biết mình đang ở đâu.</p></div>
                    <div className="student-progress-score"><strong>{latestStudentResult ? `${studentPercent}%` : '—'}</strong><span>Điểm gần nhất</span></div>
                  </section>
                  <section className="student-progress-cards">
                    <article><span className="mint"><CheckCircle2 /></span><div><small>Lộ trình hoàn thành</small><strong>{completedRoadmaps}</strong></div></article>
                    <article><span className="violet"><ClipboardCheck /></span><div><small>Lần đánh giá</small><strong>{studentTestResults.length}</strong></div></article>
                    <article><span className="amber"><Trophy /></span><div><small>Trình độ hiện tại</small><strong>{latestStudentResult?.cefr || '—'}</strong></div></article>
                  </section>
                  <section className="student-progress-detail">
                    <div><span className="student-welcome-kicker"><BarChart3 size={15} /> Tổng quan năng lực</span><h3>{latestStudentResult ? 'Em đang đi đúng hướng!' : 'Bắt đầu để nhìn thấy tiến bộ'}</h3><p>{latestStudentResult ? 'Tiếp tục theo lộ trình và hoàn thành đánh giá nhanh để củng cố những kỹ năng còn thiếu.' : 'Sau bài khảo sát đầu tiên, biểu đồ tiến bộ và các cột mốc của em sẽ xuất hiện tại đây.'}</p></div>
                    <button className="btn btn-primary" onClick={() => setStudentActiveTab(latestStudentResult ? 'roadmap' : 'survey')}>{latestStudentResult ? 'Xem lộ trình' : 'Bắt đầu khảo sát'} <ArrowRight size={17} /></button>
                  </section>
                </div>
              )}
              {studentActiveTab === 'history' && (
                <StudentHistory
                  user={user}
                  results={studentTestResults}
                  questions={questions}
                  onStartSurvey={() => setStudentActiveTab('survey')}
                  onRetry={fetchStudentTestResults}
                />
              )}
            </>
          ) : (
            <>
          {/* ==========================================================
              TAB: DASHBOARD OVERVIEW
              ========================================================== */}
          {activeTab === 'dashboard' && (
            <div className="animate-fade-in">
              {/* Stats Cards */}
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: '#e6e4f6', color: '#4d44b5' }}>
                    <GraduationCap />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Học sinh</span>
                    <span className="stat-val">{students.length}</span>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: '#fff2eb', color: '#fb7d5b' }}>
                    <Users />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Giáo viên</span>
                    <span className="stat-val">{teachers.length}</span>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: '#e1f6e8', color: '#27c26c' }}>
                    <ClipboardCheck />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Bài kiểm tra</span>
                    <span className="stat-val">{totalTestResults}</span>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: '#fffbeb', color: '#f59e0b' }}>
                    <Award />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Điểm trung bình</span>
                    <span className="stat-val">{avgScore} pts</span>
                  </div>
                </div>
              </div>

              {/* Charts grid */}
              <div className="charts-grid">
                <div className="panel">
                    <h3 className="card-title">Biểu đồ điểm theo tuần</h3>
                  <div className="chart-placeholder">
                    {/* SVG Line Chart for premium looks */}
                    <svg viewBox="0 0 500 150" style={{ width: '100%', height: '180px' }}>
                      <defs>
                        <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#4d44b5" stopOpacity="0.2"/>
                          <stop offset="100%" stopColor="#4d44b5" stopOpacity="0"/>
                        </linearGradient>
                      </defs>
                      {/* Grid lines */}
                      <line x1="0" y1="30" x2="500" y2="30" stroke="#f2f2f2" strokeWidth="1" />
                      <line x1="0" y1="75" x2="500" y2="75" stroke="#f2f2f2" strokeWidth="1" />
                      <line x1="0" y1="120" x2="500" y2="120" stroke="#f2f2f2" strokeWidth="1" />
                      
                      {/* Area */}
                      <path d="M 0 120 C 50 100, 100 60, 150 90 C 200 120, 250 40, 300 60 C 350 80, 400 30, 500 10 L 500 120 Z" fill="url(#chartGrad)" />
                      {/* Line */}
                      <path d="M 0 120 C 50 100, 100 60, 150 90 C 200 120, 250 40, 300 60 C 350 80, 400 30, 500 10" fill="none" stroke="#4d44b5" strokeWidth="3" />
                      
                      {/* Dots */}
                      <circle cx="150" cy="90" r="5" fill="#4d44b5" stroke="white" strokeWidth="2" />
                      <circle cx="300" cy="60" r="5" fill="#4d44b5" stroke="white" strokeWidth="2" />
                      <circle cx="500" cy="10" r="5" fill="#fb7d5b" stroke="white" strokeWidth="2" />
                    </svg>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)' }}>
                      <span>Tuần 01</span>
                      <span>Tuần 02</span>
                      <span>Tuần 03</span>
                      <span>Tuần 04</span>
                    </div>
                  </div>
                </div>

                <div className="panel">
                    <h3 className="card-title">Thống kê theo lớp</h3>
                  <div className="chart-placeholder">
                    <div className="bar-chart-visual">
                      <div className="bar-column">
                        <div className="bar-fill-container">
                          <div className="bar-fill" style={{ height: '70%', background: '#4d44b5' }}></div>
                        </div>
                        <span className="bar-label">Lớp 6</span>
                      </div>
                      <div className="bar-column">
                        <div className="bar-fill-container">
                          <div className="bar-fill" style={{ height: '85%', background: '#fb7d5b' }}></div>
                        </div>
                        <span className="bar-label">Lớp 7</span>
                      </div>
                      <div className="bar-column">
                        <div className="bar-fill-container">
                          <div className="bar-fill" style={{ height: '40%', background: '#27c26c' }}></div>
                        </div>
                        <span className="bar-label">Lớp 8</span>
                      </div>
                      <div className="bar-column">
                        <div className="bar-fill-container">
                          <div className="bar-fill" style={{ height: '60%', background: '#f59e0b' }}></div>
                        </div>
                        <span className="bar-label">Lớp 9</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom section: Recent Students & Teachers tables */}
              <div className="dashboard-bottom-grid" style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
                {/* Recent Students */}
                <div className="panel table-panel">
                  <div className="table-header-bar">
                    <h3 className="table-title">Học sinh gần đây</h3>
                    <button className="btn btn-primary btn-small" onClick={() => setActiveTab('students')}>Xem tất cả</button>
                  </div>
                  <div className="table-container">
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th>Thông tin học sinh</th>
                          <th>Khối</th>
                          <th>Trình độ</th>
                        </tr>
                      </thead>
                      <tbody>
                        {students.slice(0, 4).map(student => {
                          const level = student.ranking?.level || 'Beginner';
                          const isWeak = level === 'Beginner' || level === 'Starter';
                          return (
                          <tr key={student.id} style={isWeak ? { background: 'rgba(255,77,79,0.02)' } : {}}>
                            <td>
                              <div className="student-meta">
                                <div className="avatar-circle" style={{ background: isWeak ? '#ff4d4f' : getAvatarColor(student.name) }}>
                                  {student.name.charAt(0).toUpperCase()}
                                </div>
                                <div>
                                  <div className="meta-name">{student.name}</div>
                                  <div className="meta-email">{student.email}</div>
                                </div>
                              </div>
                            </td>
                            <td>
                              <span className="badge badge-primary">{student.grade || 'Lớp 6'}</span>
                            </td>
                            <td>
                              <span className={`badge ${level === 'Expert' ? 'badge-success' : level === 'Intermediate' ? 'badge-secondary' : isWeak ? 'badge-danger' : 'badge-primary'}`}>
                                {level}
                                {isWeak && <span style={{ marginLeft: '4px', fontSize: '9px' }}>⚠</span>}
                              </span>
                            </td>
                          </tr>
                          );
                        })}
                        {students.length === 0 && (
                          <tr>
                            <td colSpan="3" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                              Chưa có học sinh nào.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Calendar Card */}
                <div className="panel">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h3 className="card-title" style={{ margin: 0 }}>Lịch học</h3>
                    <span style={{ fontSize: '13px', fontWeight: '700', color: 'var(--primary)' }}>Tháng 7, 2026</span>
                  </div>
                  <div className="calendar-visual">
                    <div className="cal-header">Su</div>
                    <div className="cal-header">Mo</div>
                    <div className="cal-header">Tu</div>
                    <div className="cal-header">We</div>
                    <div className="cal-header">Th</div>
                    <div className="cal-header">Fr</div>
                    <div className="cal-header">Sa</div>
                    
                    <div className="cal-day muted">27</div>
                    <div className="cal-day muted">28</div>
                    <div className="cal-day muted">29</div>
                    <div className="cal-day muted">30</div>
                    <div className="cal-day">1</div>
                    <div className="cal-day">2</div>
                    <div className="cal-day">3</div>
                    
                    <div className="cal-day">4</div>
                    <div className="cal-day">5</div>
                    <div className="cal-day">6</div>
                    <div className="cal-day active">7</div>
                    <div className="cal-day">8</div>
                    <div className="cal-day">9</div>
                    <div className="cal-day">10</div>
                    
                    <div className="cal-day">11</div>
                    <div className="cal-day">12</div>
                    <div className="cal-day">13</div>
                    <div className="cal-day">14</div>
                    <div className="cal-day today">15</div>
                    <div className="cal-day">16</div>
                    <div className="cal-day">17</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ==========================================================
              TAB: STUDENTS DIRECTORY
              ========================================================== */}
          {activeTab === 'users' && (
            <div className="animate-fade-in">
              <div className="subtab-bar">
                <button
                  className={`subtab-btn ${userSubTab === 'students' ? 'active' : ''}`}
                  onClick={() => { setUserSubTab('students'); fetchStudents(); }}
                >
                  <GraduationCap size={16} />
                  Học sinh
                </button>
                {user?.role === 'admin' && (
                  <button
                    className={`subtab-btn ${userSubTab === 'teachers' ? 'active' : ''}`}
                    onClick={() => { setUserSubTab('teachers'); fetchTeachers(); }}
                  >
                    <Users size={16} />
                    Giáo viên
                  </button>
                )}
              </div>
            </div>
          )}

          {activeTab === 'users' && userSubTab === 'students' && (
            <div className="animate-fade-in panel table-panel">
              <div className="table-header-bar">
                <h3 className="table-title">Chi tiết Học sinh</h3>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    setStudentForm({ name: '', email: '', grade: 'Lớp 6', password: '' });
                    setStudentModal({ open: true, mode: 'create', data: null });
                  }}
                >
                  <Plus size={16} />
                  Thêm học sinh
                </button>
              </div>

              {loading && <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Đang tải dữ liệu...</div>}

              {!loading && filteredStudents.length === 0 ? (
                <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <GraduationCap size={48} style={{ opacity: '0.4', marginBottom: '16px' }} />
                  <p>Không tìm thấy học sinh nào matching với query.</p>
                </div>
              ) : (
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Tên</th>
                        <th>Email</th>
                        <th>Khối</th>
                        <th>Trình độ</th>
                        <th>Điểm</th>
                        <th style={{ width: '150px', textAlign: 'center' }}>Thao tác</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredStudents.map(student => (
                        <tr key={student.id}>
                          <td>
                            <div className="student-meta">
                              <div className="avatar-circle" style={{ background: getAvatarColor(student.name) }}>
                                {student.name.charAt(0).toUpperCase()}
                              </div>
                              <span className="meta-name">{student.name}</span>
                            </div>
                          </td>
                          <td style={{ color: 'var(--text-muted)' }}>{student.email}</td>
                          <td>
                            <span className="badge badge-primary">{student.grade || 'Lớp 6'}</span>
                          </td>
                           <td>
                             <span className={`badge ${student.ranking?.level === 'Expert' ? 'badge-success' : student.ranking?.level === 'Intermediate' ? 'badge-secondary' : (student.ranking?.level === 'Beginner' || student.ranking?.level === 'Starter') ? 'badge-danger' : 'badge-primary'}`}>
                               {student.ranking?.level || 'Beginner'}
                             </span>
                           </td>
                          <td style={{ fontWeight: '700', color: '#f59e0b' }}>
                            {student.ranking?.score || 0} pts
                          </td>
                          <td>
                            <div className="action-group">
                              <button 
                                className="action-btn action-btn-edit" 
                                title="Chỉnh sửa"
                                onClick={() => {
                                  setStudentForm({
                                    name: student.name,
                                    email: student.email,
                                    grade: student.grade || 'Lớp 6',
                                    password: ''
                                  });
                                  setStudentModal({ open: true, mode: 'edit', data: student });
                                }}
                              >
                                <Edit3 size={14} />
                              </button>
                              <button 
                                className="action-btn action-btn-edit" 
                                title="Reset mật khẩu"
                                onClick={() => resetStudentPassword(student.id, student.name)}
                              >
                                <Key size={14} />
                              </button>
                              <button 
                                className="action-btn action-btn-delete" 
                                title="Xóa"
                                onClick={() => deleteStudent(student.id)}
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ==========================================================
              TAB: TEACHERS DIRECTORY (under Người dùng)
              ========================================================== */}
          {activeTab === 'users' && userSubTab === 'teachers' && (
            <div className="animate-fade-in panel table-panel">
              <div className="table-header-bar">
                <h3 className="table-title">Chi tiết Giáo viên</h3>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    setTeacherForm({ name: '', email: '', subject: '', password: '' });
                    setTeacherModal({ open: true, mode: 'create', data: null });
                  }}
                >
                  <Plus size={16} />
                  Thêm giáo viên
                </button>
              </div>

              {loading && <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Đang tải dữ liệu...</div>}

              {!loading && filteredTeachers.length === 0 ? (
                <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <Users size={48} style={{ opacity: '0.4', marginBottom: '16px' }} />
                  <p>Không tìm thấy giáo viên nào.</p>
                </div>
              ) : (
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Thông tin giáo viên</th>
                        <th>Môn học</th>
                        <th>Bằng cấp / Email</th>
                        <th>Ngày tham gia</th>
                        <th style={{ width: '150px', textAlign: 'center' }}>Thao tác</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTeachers.map(teacher => (
                        <tr key={teacher.id}>
                          <td>
                            <div className="teacher-meta">
                              <div className="avatar-circle" style={{ background: getAvatarColor(teacher.name) }}>
                                {teacher.name.charAt(0).toUpperCase()}
                              </div>
                              <span className="meta-name">{teacher.name}</span>
                            </div>
                          </td>
                          <td>
                            <span className="badge badge-secondary">{teacher.subject || 'Tiếng Anh'}</span>
                          </td>
                          <td style={{ color: 'var(--text-muted)' }}>{teacher.email}</td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-muted)' }}>
                              <Clock size={12} />
                              <span>{new Date(teacher.created_at).toLocaleDateString('vi-VN')}</span>
                            </div>
                          </td>
                          <td>
                            <div className="action-group">
                              <button 
                                className="action-btn action-btn-edit"
                                title="Chỉnh sửa"
                                onClick={() => {
                                  setTeacherForm({
                                    name: teacher.name,
                                    email: teacher.email,
                                    subject: teacher.subject || '',
                                    password: ''
                                  });
                                  setTeacherModal({ open: true, mode: 'edit', data: teacher });
                                }}
                              >
                                <Edit3 size={14} />
                              </button>
                              <button 
                                className="action-btn action-btn-edit"
                                title="Reset mật khẩu"
                                onClick={() => resetTeacherPassword(teacher.id, teacher.name)}
                              >
                                <Key size={14} />
                              </button>
                              <button 
                                className="action-btn action-btn-delete"
                                title="Xóa"
                                onClick={() => deleteTeacher(teacher.id)}
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ==========================================================
              TAB: LEADERBOARD / RANKINGS
              ========================================================== */}
          {activeTab === 'leaderboard' && (
            <div className="animate-fade-in panel">
              <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <h3 className="card-title">Bảng vinh danh</h3>
                <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Top học sinh xuất sắc nhất hệ thống</p>
              </div>

              {/* Top 3 Podium */}
              {podiumStudents.length > 0 && (
                <div className="podium-container">
                  {/* 2nd place */}
                  {podiumStudents[1] && (
                    <div className="podium-column">
                      <div className="podium-avatar" style={{ background: getAvatarColor(getStudentName(podiumStudents[1].student_id)) }}>
                        {getStudentName(podiumStudents[1].student_id).charAt(0).toUpperCase()}
                        <div className="podium-medal silver-medal">2</div>
                      </div>
                      <div className="podium-name">{getStudentName(podiumStudents[1].student_id)}</div>
                      <div className="podium-score">{podiumStudents[1].score} pts</div>
                      <div className="podium-block podium-block-2">2</div>
                    </div>
                  )}

                  {/* 1st place */}
                  {podiumStudents[0] && (
                    <div className="podium-column">
                      <div className="podium-avatar" style={{ background: getAvatarColor(getStudentName(podiumStudents[0].student_id)) }}>
                        {getStudentName(podiumStudents[0].student_id).charAt(0).toUpperCase()}
                        <div className="podium-medal gold-medal">1</div>
                      </div>
                      <div className="podium-name" style={{ fontSize: '16px', fontWeight: '800' }}>{getStudentName(podiumStudents[0].student_id)}</div>
                      <div className="podium-score" style={{ fontSize: '13px' }}>{podiumStudents[0].score} pts</div>
                      <div className="podium-block podium-block-1">1</div>
                    </div>
                  )}

                  {/* 3rd place */}
                  {podiumStudents[2] && (
                    <div className="podium-column">
                      <div className="podium-avatar" style={{ background: getAvatarColor(getStudentName(podiumStudents[2].student_id)) }}>
                        {getStudentName(podiumStudents[2].student_id).charAt(0).toUpperCase()}
                        <div className="podium-medal bronze-medal">3</div>
                      </div>
                      <div className="podium-name">{getStudentName(podiumStudents[2].student_id)}</div>
                      <div className="podium-score">{podiumStudents[2].score} pts</div>
                      <div className="podium-block podium-block-3">3</div>
                    </div>
                  )}
                </div>
              )}

              {/* Complete Leaderboard List */}
              <div className="table-container" style={{ marginTop: '40px' }}>
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th style={{ width: '80px', textAlign: 'center' }}>Hạng</th>
                      <th>Thông tin học sinh</th>
                      <th>Khối</th>
                      <th>Trình độ</th>
                      <th style={{ width: '120px' }}>Điểm</th>
                      <th style={{ width: '180px', textAlign: 'center' }}>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedRankings.map((rank, index) => (
                      <tr key={rank.id}>
                        <td style={{ textAlign: 'center', fontWeight: '800', fontSize: '15px' }}>
                          {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                        </td>
                        <td>
                          <div className="student-meta">
                            <div className="avatar-circle" style={{ background: getAvatarColor(getStudentName(rank.student_id)) }}>
                              {getStudentName(rank.student_id).charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <div className="meta-name">{getStudentName(rank.student_id)}</div>
                              <div className="meta-email">{getStudentEmail(rank.student_id)}</div>
                            </div>
                          </div>
                        </td>
                        <td>{getStudentGrade(rank.student_id) || 'Lớp 6'}</td>
                        <td>
                          <span className={`badge ${rank.level === 'Expert' ? 'badge-success' : rank.level === 'Intermediate' ? 'badge-secondary' : (rank.level === 'Beginner' || rank.level === 'Starter') ? 'badge-danger' : 'badge-primary'}`}>
                            {rank.level}
                          </span>
                        </td>
                        <td style={{ fontWeight: '800', color: '#fb7d5b', fontSize: '15px' }}>
                          {rank.score} pts
                        </td>
                        <td style={{ textAlign: 'center' }}>
                          <button 
                            className="btn btn-outline btn-small"
                            onClick={() => incrementScore(rank)}
                          >
                            <TrendingUp size={12} />
                            +10 Điểm
                          </button>
                        </td>
                      </tr>
                    ))}
                    {sortedRankings.length === 0 && (
                      <tr>
                        <td colSpan="6" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                          Chưa có dữ liệu xếp hạng.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==========================================================
              TAB: ASSESSMENT (Đánh giá) — groups survey + test-results + placement-tests
              ========================================================== */}
          {activeTab === 'assessment' && (
            <div className="animate-fade-in">
              <div className="subtab-bar">
                <button
                  className={`subtab-btn ${assessmentSubTab === 'survey' ? 'active' : ''}`}
                  onClick={() => setAssessmentSubTab('survey')}
                >
                  <BookOpen size={16} />
                  Khảo sát
                </button>
                <button
                  className={`subtab-btn ${assessmentSubTab === 'test-results' ? 'active' : ''}`}
                  onClick={() => { setAssessmentSubTab('test-results'); fetchTestResults(); fetchStudents(); }}
                >
                  <ClipboardCheck size={16} />
                  Kết quả
                </button>
                <button
                  className={`subtab-btn ${assessmentSubTab === 'placement-tests' ? 'active' : ''}`}
                  onClick={() => { setAssessmentSubTab('placement-tests'); fetchPlacementTests(); setSelectedTest(null); }}
                >
                  <FileText size={16} />
                  Bài test
                </button>
              </div>
            </div>
          )}

          {activeTab === 'assessment' && assessmentSubTab === 'survey' && (
            <div className="animate-fade-in panel survey-card">
              <div className="survey-top">
                <BookOpen size={48} />
                <h2>Khảo sát Năng lực Đầu vào</h2>
                <p>Cung cấp các thông tin cơ bản để AI cá nhân hóa lộ trình học tiếng Anh cho bạn</p>
              </div>

              {error && (
                <div style={{ background: 'var(--danger-bg)', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '14px', borderRadius: '12px', marginBottom: '24px', fontSize: '14px', fontWeight: '600' }}>
                  {error}
                </div>
              )}

              <form onSubmit={handleSurveySubmit} className="form-grid-layout">
                <div className="form-span-full">
                  <label>Họ và Tên Học viên</label>
                  <input 
                    type="text" 
                    placeholder="Ví dụ: Nguyễn Văn A" 
                    value={surveyForm.name}
                    onChange={e => setSurveyForm({...surveyForm, name: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <label>Địa chỉ Email</label>
                  <input 
                    type="email" 
                    placeholder="student@example.com" 
                    value={surveyForm.email}
                    onChange={e => setSurveyForm({...surveyForm, email: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <label>Khối lớp</label>
                  <select 
                    value={surveyForm.grade}
                    onChange={e => setSurveyForm({...surveyForm, grade: e.target.value})}
                  >
                    <option value="Lớp 6">Lớp 6</option>
                    <option value="Lớp 7">Lớp 7</option>
                    <option value="Lớp 8">Lớp 8</option>
                    <option value="Lớp 9">Lớp 9</option>
                    <option value="Lớp 10">Lớp 10</option>
                    <option value="Lớp 11">Lớp 11</option>
                    <option value="Lớp 12">Lớp 12</option>
                  </select>
                </div>

                <div>
                  <label>Số năm học Tiếng Anh</label>
                  <input 
                    type="number" 
                    min="0"
                    value={surveyForm.years_studying_english}
                    onChange={e => setSurveyForm({...surveyForm, years_studying_english: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <label>Môi trường học tập</label>
                  <select 
                    value={surveyForm.learning_environment}
                    onChange={e => setSurveyForm({...surveyForm, learning_environment: e.target.value})}
                  >
                    <option value="school">Chỉ học ở trường</option>
                    <option value="center">Học ở trung tâm</option>
                    <option value="self_study">Tự học qua mạng</option>
                  </select>
                </div>

                <div className="form-span-full">
                  <label>Tự đánh giá trình độ hiện tại</label>
                  <select 
                    value={surveyForm.self_assessment_level}
                    onChange={e => setSurveyForm({...surveyForm, self_assessment_level: e.target.value})}
                  >
                    <option value="A1">A1 (Mới bắt đầu - Beginner)</option>
                    <option value="A2">A2 (Cơ bản - Elementary)</option>
                    <option value="B1">B1 (Trung cấp - Intermediate)</option>
                    <option value="B2">B2 (Trên trung cấp)</option>
                    <option value="C1">C1 (Cao cấp - Advanced)</option>
                  </select>
                </div>

                <div className="form-span-full">
                  <label>Mục tiêu học tập của bạn</label>
                  <textarea 
                    rows="3" 
                    placeholder="Ví dụ: Đạt điểm thi học kỳ tốt, rèn luyện kỹ năng nghe nói..."
                    value={surveyForm.learning_goal}
                    onChange={e => setSurveyForm({...surveyForm, learning_goal: e.target.value})}
                  ></textarea>
                </div>

                <div className="form-span-full" style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
                  <button type="submit" className="btn btn-primary" style={{ padding: '14px 40px' }} disabled={loading}>
                    {loading ? "Đang xử lý..." : "Nộp khảo sát & Bắt đầu"}
                    <ArrowRight size={16} />
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* ==========================================================
              TAB: TEST RESULTS (under Đánh giá)
              ========================================================== */}
          {activeTab === 'assessment' && assessmentSubTab === 'test-results' && (
            <div className="animate-fade-in panel table-panel">
              {!selectedResult ? (
                <>
                  <div className="table-header-bar">
                    <h3 className="table-title">Kết quả kiểm tra trình độ</h3>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                      {testResults.length} kết quả
                    </div>
                  </div>

                  {loading && <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Đang tải dữ liệu...</div>}

                  {!loading && testResults.length === 0 ? (
                    <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      <ClipboardCheck size={48} style={{ opacity: '0.4', marginBottom: '16px' }} />
                      <p>Chưa có kết quả kiểm tra nào.</p>
                    </div>
                  ) : (
                    <div className="table-container">
                      <table className="custom-table">
                        <thead>
                          <tr>
                            <th>Học sinh</th>
                            <th>Ngày thi</th>
                            <th style={{ width: '140px' }}>Điểm số</th>
                            <th>Trình độ</th>
                            <th>CEFR</th>
                            <th>Thời gian</th>
                            <th style={{ width: '120px', textAlign: 'center' }}>Thao tác</th>
                          </tr>
                        </thead>
                        <tbody>
                          {testResults.map(result => {
                            const pct = result.percentage || Math.round((result.score / result.max_score) * 100);
                            return (
                              <tr key={result.id}>
                                <td>
                                  <div className="student-meta">
                                    <div className="avatar-circle" style={{ background: getAvatarColor(getStudentName(result.student_id)) }}>
                                      {getStudentName(result.student_id).charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                      <div className="meta-name">{getStudentName(result.student_id)}</div>
                                      <div className="meta-email">{getStudentEmail(result.student_id)}</div>
                                    </div>
                                  </div>
                                </td>
                                <td>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-muted)' }}>
                                    <Calendar size={12} />
                                    <span>{new Date(result.test_date).toLocaleDateString('vi-VN')}</span>
                                  </div>
                                </td>
                                <td>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <div style={{ flex: 1, height: '8px', background: '#f0eef5', borderRadius: '4px', overflow: 'hidden' }}>
                                      <div style={{ 
                                        height: '100%', 
                                        width: `${pct}%`,
                                        borderRadius: '4px',
                                        background: pct >= 70 ? '#27c26c' : pct >= 40 ? '#fb7d5b' : '#ff4d4f',
                                        transition: 'width 0.5s ease'
                                      }} />
                                    </div>
                                    <span style={{ fontWeight: '800', fontSize: '14px', color: pct >= 70 ? '#27c26c' : pct >= 40 ? '#fb7d5b' : '#ff4d4f', minWidth: '50px', textAlign: 'right' }}>
                                      {result.score}/{result.max_score}
                                    </span>
                                  </div>
                                </td>
                                <td>
                                  <span className={`badge ${result.result_level === 'elementary' ? 'badge-success' : result.result_level === 'starter' ? 'badge-danger' : result.result_level === 'beginner' ? 'badge-secondary' : 'badge-primary'}`}>
                                    {result.result_level === 'starter' ? '⚠ Starter' : result.result_level === 'beginner' ? 'Beginner' : result.result_level === 'elementary' ? 'Elementary' : result.result_level}
                                  </span>
                                </td>
                                <td style={{ fontWeight: '700', fontSize: '14px' }}>{result.cefr}</td>
                                <td>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-muted)' }}>
                                    <Clock size={12} />
                                    <span>{Math.floor(result.time_total_sec / 60)}m {result.time_total_sec % 60}s</span>
                                  </div>
                                </td>
                                <td style={{ textAlign: 'center' }}>
                                  <button 
                                    className="btn btn-primary btn-small"
                                    onClick={() => setSelectedResult(result)}
                                  >
                                    <TrendingUp size={12} />
                                    Chi tiết
                                  </button>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              ) : (
                <>
                  {/* ===== DETAIL VIEW ===== */}
                  <div className="table-header-bar">
                    <div className="placement-detail-header" style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                      <button 
                        className="btn btn-outline btn-small"
                        onClick={() => setSelectedResult(null)}
                      >
                        ← Quay lại
                      </button>
                      <h3 className="table-title" style={{ margin: 0, flex: 1 }}>
                        Kết quả: {getStudentName(selectedResult.student_id)}
                      </h3>
                    </div>
                  </div>

                  {/* Summary Cards — 2 hàng × 2 cột */}
                  <div className="detail-summary-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', padding: '24px 32px', borderBottom: '1px solid var(--border)' }}>
                    {/* Score card */}
                    <div style={{ 
                      padding: '20px', borderRadius: '14px', 
                      background: 'linear-gradient(135deg, rgba(79,69,229,0.06), rgba(79,69,229,0.02))',
                      border: '1px solid rgba(79,69,229,0.1)'
                    }}>
                      <div className="detail-label" style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Điểm số</div>
                      <div className="detail-score-val" style={{ fontSize: '28px', fontWeight: '800', color: 'var(--primary)' }}>
                        {selectedResult.score}<span className="detail-sub-val" style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-muted)' }}>/{selectedResult.max_score}</span>
                      </div>
                      <div style={{ marginTop: '8px', height: '6px', background: '#f0eef5', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ 
                          height: '100%', width: `${selectedResult.percentage || 0}%`, borderRadius: '3px',
                          background: 'linear-gradient(90deg, #4d44b5, #7c6ff0)'
                        }} />
                      </div>
                      <div className="detail-sub-val" style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>{selectedResult.percentage || 0}% đúng</div>
                    </div>

                    {/* Level card */}
                    <div style={{ 
                      padding: '20px', borderRadius: '14px',
                      background: selectedResult.result_level === 'elementary' ? 'rgba(39,194,108,0.06)' : selectedResult.result_level === 'starter' ? 'rgba(255,77,79,0.08)' : selectedResult.result_level === 'beginner' ? 'rgba(251,125,91,0.06)' : 'rgba(79,69,229,0.06)',
                      border: `1px solid ${selectedResult.result_level === 'elementary' ? 'rgba(39,194,108,0.15)' : selectedResult.result_level === 'starter' ? 'rgba(255,77,79,0.2)' : selectedResult.result_level === 'beginner' ? 'rgba(251,125,91,0.15)' : 'rgba(79,69,229,0.1)'}`
                    }}>
                      <div className="detail-label" style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trình độ</div>
                      <div className="detail-level-val" style={{ fontSize: '22px', fontWeight: '800', color: selectedResult.result_level === 'elementary' ? '#27c26c' : selectedResult.result_level === 'starter' ? '#ff4d4f' : selectedResult.result_level === 'beginner' ? '#fb7d5b' : '#4d44b5', textTransform: 'capitalize', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {selectedResult.result_level}
                        {selectedResult.result_level === 'starter' && (
                          <span style={{ fontSize: '10px', fontWeight: '700', padding: '3px 10px', borderRadius: '10px', background: 'rgba(255,77,79,0.12)', color: '#ff4d4f' }}>Cần hỗ trợ khẩn cấp</span>
                        )}
                      </div>
                      <div className="detail-sub-val" style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>CEFR: <strong>{selectedResult.cefr}</strong></div>
                    </div>

                    {/* Time card */}
                    <div style={{ 
                      padding: '20px', borderRadius: '14px',
                      background: 'rgba(251,125,91,0.06)',
                      border: '1px solid rgba(251,125,91,0.1)'
                    }}>
                      <div className="detail-label" style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Thời gian</div>
                      <div className="detail-time-val" style={{ fontSize: '28px', fontWeight: '800', color: '#fb7d5b' }}>
                        {Math.floor(selectedResult.time_total_sec / 60)}<span className="detail-sub-val" style={{ fontSize: '14px', fontWeight: '600' }}> phút </span>{selectedResult.time_total_sec % 60}<span className="detail-sub-val" style={{ fontSize: '14px', fontWeight: '600' }}> giây</span>
                      </div>
                      <div className="detail-sub-val" style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Trung bình {Math.round(selectedResult.time_total_sec / (selectedResult.answers?.length || 1))}s/câu
                      </div>
                    </div>

                    {/* Date card */}
                    <div style={{ 
                      padding: '20px', borderRadius: '14px',
                      background: 'rgba(39,194,108,0.06)',
                      border: '1px solid rgba(39,194,108,0.1)'
                    }}>
                      <div className="detail-label" style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Ngày thi</div>
                      <div className="detail-date-val" style={{ fontSize: '18px', fontWeight: '700', color: '#27c26c' }}>
                        {new Date(selectedResult.test_date).toLocaleDateString('vi-VN')}
                      </div>
                      <div className="detail-sub-val" style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                        {new Date(selectedResult.test_date).toLocaleTimeString('vi-VN')}
                      </div>
                    </div>
                  </div>

                  {/* Mastery — full width */}
                  <div className="detail-mastery-section" style={{ padding: '24px 32px 12px' }}>
                    <h4 className="detail-section-title" style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <TrendingUp size={18} style={{ color: 'var(--primary)' }} />
                      Mức thuần thục kỹ năng (BKT)
                    </h4>
                    <div className="detail-mastery-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
                      {selectedResult.mastery && Object.entries(selectedResult.mastery)
                        .sort((a, b) => (a[1].probability || 0) - (b[1].probability || 0))
                        .map(([skillId, m]) => {
                        const pct = Math.round(m.probability * 100);
                        const color = pct < 20 ? '#ff4d4f' : pct < 40 ? '#fb7d5b' : pct < 60 ? '#f59e0b' : pct < 80 ? '#4d44b5' : '#27c26c';
                        const statusLabel = pct < 20 ? 'Rất yếu' : pct < 40 ? 'Yếu' : pct < 60 ? 'Đang học' : pct < 80 ? 'Khá' : 'Thành thạo';
                        const statusBg = pct < 20 ? 'rgba(255,77,79,0.1)' : pct < 40 ? 'rgba(251,125,91,0.1)' : pct < 60 ? 'rgba(245,158,11,0.1)' : pct < 80 ? 'rgba(79,69,229,0.08)' : 'rgba(39,194,108,0.1)';
                        return (
                          <div key={skillId} style={{ 
                            padding: '12px 16px', borderRadius: '10px',
                            background: pct < 20 ? 'rgba(255,77,79,0.02)' : '#fdfcff',
                            border: `1px solid ${pct < 20 ? 'rgba(255,77,79,0.12)' : 'var(--border)'}`
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                              <div>
                                <span style={{ fontFamily: 'monospace', fontSize: '11px', fontWeight: '700', color: 'var(--primary)', marginRight: '6px' }}>{skillId}</span>
                                <span style={{ fontSize: '12px', color: 'var(--text-color)', fontWeight: '600' }}>{m.skill_name}</span>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ fontSize: '13px', fontWeight: '800', color }}>{pct}%</span>
                                <span style={{ 
                                  fontSize: '10px', fontWeight: '700', padding: '2px 8px', borderRadius: '10px',
                                  background: statusBg, color
                                }}>
                                  {statusLabel}
                                </span>
                              </div>
                            </div>
                            <div style={{ height: '6px', background: '#f0eef5', borderRadius: '3px', overflow: 'hidden' }}>
                              <div style={{ height: '100%', width: `${Math.max(pct, 2)}%`, borderRadius: '3px', background: color, transition: 'width 0.5s ease' }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Gaps + Recommendations — 2 cột cân bằng */}
                  <div className="detail-gaps-recs-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', padding: '12px 32px 24px' }}>
                    {/* Gaps (left) */}
                    <div>
                      <h4 className="detail-section-title" style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <AlertTriangle size={18} style={{ color: '#ff4d4f' }} />
                        Lỗ hổng kiến thức ({selectedResult.gaps?.length || 0})
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {[...(selectedResult.gaps || [])].sort((a, b) => (a.severity === 'high' ? 0 : 1) - (b.severity === 'high' ? 0 : 1)).map((gap, i) => (
                          <div key={i} style={{ 
                            padding: '12px 16px', borderRadius: '10px',
                            background: gap.severity === 'high' ? 'rgba(255,77,79,0.04)' : 'rgba(251,125,91,0.04)',
                            border: `1px solid ${gap.severity === 'high' ? 'rgba(255,77,79,0.15)' : 'rgba(251,125,91,0.15)'}`
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                              <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '20px', height: '20px', borderRadius: '50%', background: gap.severity === 'high' ? 'rgba(255,77,79,0.12)' : 'rgba(251,125,91,0.12)', color: gap.severity === 'high' ? '#ff4d4f' : '#fb7d5b', fontSize: '10px', fontWeight: '800', flexShrink: 0 }}>{i + 1}</span>
                              <span style={{ fontFamily: 'monospace', fontSize: '11px', fontWeight: '700', color: 'var(--primary)' }}>{gap.skill_id}</span>
                              <span style={{ 
                                fontSize: '10px', fontWeight: '700', padding: '2px 8px', borderRadius: '10px',
                                background: gap.severity === 'high' ? 'rgba(255,77,79,0.12)' : 'rgba(251,125,91,0.12)',
                                color: gap.severity === 'high' ? '#ff4d4f' : '#fb7d5b'
                              }}>
                                {gap.severity === 'high' ? '⚠ Nghiêm trọng' : 'Trung bình'}
                              </span>
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4', marginLeft: '28px' }}>{gap.reason}</div>
                          </div>
                        ))}
                        {(!selectedResult.gaps || selectedResult.gaps.length === 0) && (
                          <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>Không có lỗ hổng nào</div>
                        )}
                      </div>
                    </div>

                    {/* Recommendations (right) */}
                    <div>
                      <h4 className="detail-section-title" style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Lightbulb size={18} style={{ color: '#fb7d5b' }} />
                        Đề xuất học tập ({selectedResult.recommendations?.length || 0})
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {selectedResult.recommendations?.map((rec, i) => (
                          <div key={i} style={{ 
                            padding: '12px 16px', borderRadius: '10px',
                            background: rec.priority === 'high' ? 'rgba(251,125,91,0.04)' : 'rgba(79,69,229,0.04)',
                            border: `1px solid ${rec.priority === 'high' ? 'rgba(251,125,91,0.15)' : 'rgba(79,69,229,0.1)'}`
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                              {rec.priority === 'high' ? (
                                <Lightbulb size={14} style={{ color: '#fb7d5b', flexShrink: 0 }} />
                              ) : (
                                <BookOpen size={14} style={{ color: '#4d44b5', flexShrink: 0 }} />
                              )}
                              <span style={{ fontFamily: 'monospace', fontSize: '11px', fontWeight: '700', color: 'var(--primary)' }}>{rec.skill_id}</span>
                              <span style={{ 
                                fontSize: '10px', fontWeight: '700', padding: '2px 8px', borderRadius: '10px',
                                background: rec.priority === 'high' ? 'rgba(251,125,91,0.12)' : 'rgba(79,69,229,0.08)',
                                color: rec.priority === 'high' ? '#fb7d5b' : '#4d44b5'
                              }}>
                                {rec.priority === 'high' ? '🔥 Ưu tiên cao' : '📚 Bình thường'}
                              </span>
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--text-color)', lineHeight: '1.4', marginLeft: '22px' }}>{rec.action}</div>
                          </div>
                        ))}
                        {(!selectedResult.recommendations || selectedResult.recommendations.length === 0) && (
                          <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>Không có đề xuất nào</div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Training plan (AI) */}
                  {selectedResult.training_plan && (
                    <div style={{ padding: '0 32px 24px' }}>
                      <h4 className="detail-section-title" style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Lightbulb size={18} style={{ color: '#a43c20' }} />
                        Kế hoạch đào tạo cá nhân hóa (AI)
                      </h4>
                      <div className="history-training-plan">{selectedResult.training_plan}</div>
                    </div>
                  )}

                  {/* Answers detail */}
                  <div className="detail-answers-section" style={{ padding: '0 32px 24px' }}>
                    <h4 className="detail-section-title" style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FileText size={18} style={{ color: 'var(--primary)' }} />
                      Chi tiết câu trả lời ({selectedResult.answers?.length || 0} câu)
                    </h4>
                    <div className="table-container">
                      <table className="custom-table">
                        <thead>
                          <tr>
                            <th style={{ width: '4%', textAlign: 'center' }}>STT</th>
                            <th style={{ width: '10%' }}>Mã câu</th>
                            <th style={{ width: '13%' }}>Kỹ năng</th>
                            <th style={{ width: '8%', textAlign: 'center' }}>Độ khó</th>
                            <th style={{ width: '7%', textAlign: 'center' }}>Trả lời</th>
                            <th style={{ width: '7%', textAlign: 'center' }}>Kết quả</th>
                            <th style={{ width: '9%', textAlign: 'center' }}>Thời gian</th>
                            <th style={{ width: '30%' }}>Lỗi sai</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedResult.answers?.map((a, idx) => {
                            const isWrong = !a.correct;
                            const isSlow = a.time_spent_sec > 20;
                            const diffMap = { q_001:'easy', q_002:'easy', q_003:'easy', q_004:'easy', q_005:'easy', q_006:'easy', q_007:'medium', q_008:'easy', q_009:'medium', q_010:'easy', q_011:'easy', q_012:'medium', q_013:'easy', q_014:'medium' };
                            const diff = a.difficulty || diffMap[a.question_id] || 'easy';
                            const diffColor = diff === 'hard' ? '#ff4d4f' : diff === 'medium' ? '#fb7d5b' : '#27c26c';
                            const diffBg = diff === 'hard' ? 'rgba(255,77,79,0.1)' : diff === 'medium' ? 'rgba(251,125,91,0.1)' : 'rgba(39,194,108,0.1)';
                            return (
                            <tr key={idx} style={isWrong ? { background: 'rgba(255,77,79,0.02)' } : {}}>
                              <td style={{ textAlign: 'center', fontWeight: '800', color: isWrong ? '#ff4d4f' : 'var(--primary)' }}>{idx + 1}</td>
                              <td>
                                <span style={{ fontFamily: 'monospace', fontSize: '12px', fontWeight: '700', color: 'var(--primary)' }}>{a.question_id}</span>
                              </td>
                              <td>
                                <span className="badge badge-primary" style={{ fontSize: '10px' }}>{a.skill_id}</span>
                              </td>
                              <td style={{ textAlign: 'center' }}>
                                <span style={{ fontSize: '10px', fontWeight: '700', padding: '2px 8px', borderRadius: '10px', background: diffBg, color: diffColor, textTransform: 'capitalize' }}>
                                  {diff === 'easy' ? 'Dễ' : diff === 'medium' ? 'Trung bình' : 'Khó'}
                                </span>
                              </td>
                              <td style={{ textAlign: 'center', fontWeight: '700', fontSize: '15px' }}>
                                {a.selected?.toUpperCase()}
                              </td>
                              <td style={{ textAlign: 'center' }}>
                                <span style={{ 
                                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                                  width: '28px', height: '28px', borderRadius: '50%', fontWeight: '800', fontSize: '13px',
                                  background: a.correct ? 'rgba(39,194,108,0.12)' : 'rgba(255,77,79,0.12)',
                                  color: a.correct ? '#27c26c' : '#ff4d4f'
                                }}>
                                  {a.correct ? '✓' : '✗'}
                                </span>
                              </td>
                              <td style={{ textAlign: 'center', fontSize: '12px', fontWeight: isSlow ? '700' : '400', color: isSlow ? '#fb7d5b' : 'var(--text-muted)' }}>
                                {a.time_spent_sec}s{isSlow && ' ⏱'}
                              </td>
                              <td style={{ fontSize: '12px' }}>
                                {a.error_tag ? (
                                  <span style={{ color: '#ff4d4f', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <AlertTriangle size={11} />
                                    {a.error_tag.replace(/_/g, ' ')}
                                  </span>
                                ) : (
                                  <span style={{ color: 'var(--text-muted)' }}>—</span>
                                )}
                              </td>
                            </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* ==========================================================
              TAB: QUESTION BANK (Ngân hàng câu hỏi)
              ========================================================== */}
          {activeTab === 'questions' && (
            <div className="animate-fade-in panel table-panel">
              <div className="table-header-bar">
                <h3 className="table-title">Ngân hàng câu hỏi ({questions.length} câu)</h3>
                <div className="question-header-filters" style={{ display: 'flex', gap: '8px' }}>
                  <select 
                    value={questionSkillFilter} 
                    onChange={e => setQuestionSkillFilter(e.target.value)}
                    style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px', fontWeight: '600' }}
                  >
                    <option value="">Tất cả kỹ năng</option>
                    {[...new Set(questions.map(q => q.skill_id))].sort().map(sid => (
                      <option key={sid} value={sid}>{sid}</option>
                    ))}
                  </select>
                  <select 
                    value={questionDiffFilter} 
                    onChange={e => setQuestionDiffFilter(e.target.value)}
                    style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px', fontWeight: '600' }}
                  >
                    <option value="">Tất cả độ khó</option>
                    <option value="easy">Dễ</option>
                    <option value="medium">Trung bình</option>
                    <option value="hard">Khó</option>
                  </select>
                </div>
              </div>

              {loading && <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Đang tải dữ liệu...</div>}

              {!loading && (
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th style={{ width: '90px' }}>Mã câu</th>
                        <th>Câu hỏi</th>
                        <th style={{ width: '140px' }}>Kỹ năng</th>
                        <th style={{ width: '100px' }}>Độ khó</th>
                        <th style={{ width: '80px' }}>Đáp án</th>
                        <th style={{ width: '80px' }}>Loại</th>
                        <th style={{ width: '100px', textAlign: 'center' }}>Thao tác</th>
                      </tr>
                    </thead>
                    <tbody>
                      {questions
                        .filter(q => {
                          if (questionSearch) {
                            const s = questionSearch.toLowerCase();
                            if (!q.prompt?.text?.toLowerCase().includes(s) && 
                                !q.skill_name?.toLowerCase().includes(s) &&
                                !q.skill_id?.toLowerCase().includes(s) &&
                                !q.question_id?.toLowerCase().includes(s)) return false;
                          }
                          if (questionSkillFilter && q.skill_id !== questionSkillFilter) return false;
                          if (questionDiffFilter && q.difficulty !== questionDiffFilter) return false;
                          return true;
                        })
                        .map(q => (
                          <tr key={q.id}>
                            <td>
                              <span style={{ fontFamily: 'monospace', fontSize: '12px', fontWeight: '700', color: 'var(--primary)' }}>
                                {q.question_id}
                              </span>
                            </td>
                            <td>
                              <div style={{ maxWidth: '350px' }}>
                                <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '2px' }}>
                                  {q.prompt?.text || '—'}
                                </div>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                  {q.options?.map(o => `${o.option_id}) ${o.label}`).join('  |  ')}
                                </div>
                              </div>
                            </td>
                            <td>
                              <div>
                                <span className="badge badge-primary" style={{ fontSize: '11px' }}>{q.skill_id}</span>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px', lineHeight: '1.2' }}>
                                  {q.skill_name}
                                </div>
                              </div>
                            </td>
                            <td>
                              <span className={`badge ${q.difficulty === 'easy' ? 'badge-success' : q.difficulty === 'hard' ? 'badge-danger' : 'badge-secondary'}`}>
                                {q.difficulty === 'easy' ? 'Dễ' : q.difficulty === 'hard' ? 'Khó' : 'TB'}
                              </span>
                            </td>
                            <td style={{ fontWeight: '800', color: '#27c26c', textAlign: 'center' }}>
                              {q.correct_option_id}
                            </td>
                            <td>
                              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                {q.type === 'read_choice' ? 'Đọc' : 'Nghe'}
                              </span>
                            </td>
                            <td style={{ textAlign: 'center' }}>
                              <div style={{ display: 'flex', gap: '4px', justifyContent: 'center' }}>
                                <button 
                                  className="btn btn-primary btn-small"
                                  style={{ padding: '4px 8px', fontSize: '11px' }}
                                  onClick={() => setEditQuestionModal({ open: true, data: { ...q } })}
                                >
                                  Sửa
                                </button>
                                <button 
                                  className="btn btn-danger btn-small"
                                  style={{ padding: '4px 8px', fontSize: '11px' }}
                                  onClick={() => handleDeleteQuestion(q.id)}
                                >
                                  Xóa
                                </button>
                              </div>
                            </td>
                          </tr>
                      ))}
                      {questions.filter(q => {
                        if (questionSearch) {
                          const s = questionSearch.toLowerCase();
                          if (!q.prompt?.text?.toLowerCase().includes(s) && 
                              !q.skill_name?.toLowerCase().includes(s) &&
                              !q.skill_id?.toLowerCase().includes(s)) return false;
                        }
                        if (questionSkillFilter && q.skill_id !== questionSkillFilter) return false;
                        if (questionDiffFilter && q.difficulty !== questionDiffFilter) return false;
                        return true;
                      }).length === 0 && (
                        <tr>
                          <td colSpan="7" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                            Không tìm thấy câu hỏi nào.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ==========================================================
              TAB: PLACEMENT TESTS (under Đánh giá)
              ========================================================== */}
          {activeTab === 'assessment' && assessmentSubTab === 'placement-tests' && (
            <div className="animate-fade-in panel table-panel">
              {!selectedTest ? (
                <>
                  <div className="table-header-bar">
                    <h3 className="table-title">Danh sách bài kiểm tra trình độ</h3>
                  </div>

                  {loading && <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Đang tải dữ liệu...</div>}

                  {!loading && (
                    <div className="table-container">
                      <table className="custom-table">
                        <thead>
                          <tr>
                            <th style={{ width: '100px' }}>Mã bài</th>
                            <th>Tên bài kiểm tra</th>
                            <th>Số câu hỏi</th>
                            <th>Chiến lược</th>
                            <th style={{ width: '120px', textAlign: 'center' }}>Thao tác</th>
                          </tr>
                        </thead>
                        <tbody>
                          {placementTests.map(test => (
                            <tr key={test.id}>
                              <td>
                                <span style={{ fontFamily: 'monospace', fontSize: '12px', fontWeight: '700', color: 'var(--primary)' }}>
                                  {test.test_id}
                                </span>
                              </td>
                              <td>
                                <div>
                                  <div style={{ fontSize: '14px', fontWeight: '700' }}>{test.title}</div>
                                  {test.mascot && (
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                                      {test.mascot.name} {test.mascot.icon === 'bee' ? '🐝' : '📖'}
                                    </div>
                                  )}
                                </div>
                              </td>
                              <td>
                                <span className="badge badge-primary">
                                  {test.adaptive_config?.questions_per_level 
                                    ? Object.values(test.adaptive_config.questions_per_level).reduce((a, b) => a + b, 0)
                                    : '?'} câu
                                </span>
                              </td>
                              <td>
                                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                  {test.adaptive_config?.strategy === 'level_sequential' ? 'Tuyến tính theo level' : test.adaptive_config?.strategy || '—'}
                                </span>
                              </td>
                              <td style={{ textAlign: 'center' }}>
                                <div style={{ display: 'flex', gap: '4px', justifyContent: 'center' }}>
                                  <button 
                                    className="btn btn-primary btn-small"
                                    onClick={() => {
                                      setSelectedTest(test);
                                      fetchTestQuestions(test.id);
                                    }}
                                  >
                                    <FileText size={12} />
                                    Chi tiết
                                  </button>
                                  <button 
                                    className="btn btn-outline btn-small"
                                    onClick={() => setEditTestModal({ open: true, data: { ...test } })}
                                  >
                                    Sửa
                                  </button>
                                  <button 
                                    className="btn btn-danger btn-small"
                                    onClick={() => handleDeleteTest(test.id)}
                                  >
                                    Xóa
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                          {placementTests.length === 0 && (
                            <tr>
                              <td colSpan="5" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                                Chưa có bài test nào.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {/* Levels info */}
                  {placementTests.length > 0 && placementTests[0].levels && (
                    <div style={{ padding: '20px 24px', borderTop: '1px solid var(--border)' }}>
                      <h4 style={{ fontSize: '14px', fontWeight: '700', marginBottom: '12px', color: 'var(--text-color)' }}>Cấp độ bài kiểm tra</h4>
                      <div className="levels-grid-mobile" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                        {placementTests[0].levels.map(lvl => (
                          <div key={lvl.level_id} style={{ 
                            padding: '14px 16px', 
                            borderRadius: '10px', 
                            background: lvl.level_id === 'starter' ? '#e6e4f6' : lvl.level_id === 'beginner' ? '#fff2eb' : '#e1f6e8',
                            border: '1px solid transparent'
                          }}>
                            <div style={{ fontSize: '13px', fontWeight: '800', color: lvl.level_id === 'starter' ? '#4d44b5' : lvl.level_id === 'beginner' ? '#fb7d5b' : '#27c26c' }}>
                              {lvl.label}
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                              CEFR: {lvl.cefr_equivalent}
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', lineHeight: '1.3' }}>
                              {lvl.description}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <>
                  {/* Test Detail View */}
                  <div className="table-header-bar">
                    <div className="placement-detail-header" style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                      <button 
                        className="btn btn-outline btn-small"
                        onClick={() => { setSelectedTest(null); setTestQuestions([]); }}
                      >
                        ← Quay lại
                      </button>
                      <h3 className="table-title" style={{ margin: 0, flex: 1 }}>
                        {selectedTest.title} <span style={{ fontWeight: '400', fontSize: '13px', color: 'var(--text-muted)' }}>({testQuestions.length} câu hỏi)</span>
                      </h3>
                      <button 
                        className="btn btn-primary btn-small"
                        onClick={() => setShowAddQuestionModal(true)}
                      >
                        + Thêm câu hỏi
                      </button>
                    </div>
                  </div>

                  <div className="table-container">
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th style={{ width: '50px', textAlign: 'center' }}>STT</th>
                          <th style={{ width: '140px' }}>Kỹ năng</th>
                          <th>Câu hỏi</th>
                          <th style={{ width: '80px' }}>Độ khó</th>
                          <th style={{ width: '80px' }}>Đáp án</th>
                          <th>Giải thích</th>
                          <th style={{ width: '70px', textAlign: 'center' }}>Thao tác</th>
                        </tr>
                      </thead>
                      <tbody>
                        {testQuestions.map((q, idx) => (
                          <tr key={q.id}>
                            <td style={{ textAlign: 'center', fontWeight: '800', color: 'var(--primary)' }}>
                              {idx + 1}
                            </td>
                            <td>
                              <span className="badge badge-primary" style={{ fontSize: '11px' }}>{q.skill_id}</span>
                              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                                {q.skill_name}
                              </div>
                            </td>
                            <td>
                              <div style={{ fontSize: '13px', fontWeight: '600' }}>
                                {q.prompt?.text || '—'}
                              </div>
                              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                                {q.options?.map(o => (
                                  <span key={o.option_id} style={{ 
                                    marginRight: '8px',
                                    color: o.option_id === q.correct_option_id ? '#27c26c' : 'var(--text-muted)',
                                    fontWeight: o.option_id === q.correct_option_id ? '700' : '400'
                                  }}>
                                    {o.option_id}) {o.label}
                                  </span>
                                ))}
                              </div>
                            </td>
                            <td>
                              <span className={`badge ${q.difficulty === 'easy' ? 'badge-success' : q.difficulty === 'hard' ? 'badge-danger' : 'badge-secondary'}`}>
                                {q.difficulty === 'easy' ? 'Dễ' : q.difficulty === 'hard' ? 'Khó' : 'TB'}
                              </span>
                            </td>
                            <td style={{ fontWeight: '800', color: '#27c26c', textAlign: 'center', fontSize: '15px' }}>
                              {q.correct_option_id}
                            </td>
                            <td>
                              <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4', maxWidth: '250px' }}>
                                {q.explanation || '—'}
                              </div>
                            </td>
                            <td style={{ textAlign: 'center' }}>
                              <button 
                                className="btn btn-danger btn-small"
                                style={{ padding: '4px 8px', fontSize: '11px' }}
                                onClick={() => handleRemoveQuestionFromTest(selectedTest.id, q.id)}
                              >
                                Xóa
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Scoring info */}
                  {selectedTest.adaptive_config && (
                    <div className="scoring-info-bar" style={{ padding: '16px 24px', borderTop: '1px solid var(--border)', display: 'flex', gap: '24px', alignItems: 'center' }}>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        <strong>Chiến lược:</strong> {selectedTest.adaptive_config.strategy === 'level_sequential' ? 'Tuyến tính theo level' : selectedTest.adaptive_config.strategy}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        <strong>Số câu/level:</strong> {Object.entries(selectedTest.adaptive_config.questions_per_level || {}).map(([k, v]) => `${k}: ${v}`).join(', ')}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

            </>
          )}

        </main>
      </div>

      {/* ==========================================================
          MODALS: STUDENT (CREATE/EDIT)
          ========================================================== */}
      {studentModal.open && (
        <div className="modal-overlay">
          <div className="modal-card animate-fade-in">
            <button 
              className="modal-close-btn" 
              onClick={() => setStudentModal({ open: false, mode: 'create', data: null })}
            >
              <X size={24} />
            </button>
            <h3 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '24px' }}>
              {studentModal.mode === 'create' ? "Thêm mới Học sinh" : "Cập nhật thông tin Học sinh"}
            </h3>

            <form onSubmit={handleStudentSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label>Họ và Tên</label>
                <input 
                  type="text" 
                  value={studentForm.name}
                  onChange={e => setStudentForm({ ...studentForm, name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label>Địa chỉ Email</label>
                <input 
                  type="email" 
                  value={studentForm.email}
                  onChange={e => setStudentForm({ ...studentForm, email: e.target.value })}
                  required
                />
              </div>

              <div>
                <label>Khối lớp</label>
                <select 
                  value={studentForm.grade}
                  onChange={e => setStudentForm({ ...studentForm, grade: e.target.value })}
                >
                  <option value="Lớp 6">Lớp 6</option>
                  <option value="Lớp 7">Lớp 7</option>
                  <option value="Lớp 8">Lớp 8</option>
                  <option value="Lớp 9">Lớp 9</option>
                  <option value="Lớp 10">Lớp 10</option>
                  <option value="Lớp 11">Lớp 11</option>
                  <option value="Lớp 12">Lớp 12</option>
                </select>
              </div>

              <div>
                <label>Mật khẩu</label>
                <input 
                  type="password"
                  placeholder={studentModal.mode === 'create' ? 'Mặc định: 88888888' : 'Để trống nếu không đổi'}
                  value={studentForm.password}
                  onChange={e => setStudentForm({ ...studentForm, password: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
                <button 
                  type="button" 
                  className="btn btn-outline"
                  onClick={() => setStudentModal({ open: false, mode: 'create', data: null })}
                >
                  Hủy
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  Lưu lại
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==========================================================
          MODALS: TEACHER (CREATE/EDIT)
          ========================================================== */}
      {teacherModal.open && (
        <div className="modal-overlay">
          <div className="modal-card animate-fade-in">
            <button 
              className="modal-close-btn" 
              onClick={() => setTeacherModal({ open: false, mode: 'create', data: null })}
            >
              <X size={24} />
            </button>
            <h3 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '24px' }}>
              {teacherModal.mode === 'create' ? "Thêm mới Giáo viên" : "Cập nhật thông tin Giáo viên"}
            </h3>

            <form onSubmit={handleTeacherSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label>Họ và Tên</label>
                <input 
                  type="text" 
                  value={teacherForm.name}
                  onChange={e => setTeacherForm({ ...teacherForm, name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label>Địa chỉ Email</label>
                <input 
                  type="email" 
                  value={teacherForm.email}
                  onChange={e => setTeacherForm({ ...teacherForm, email: e.target.value })}
                  required
                />
              </div>

              <div>
                <label>Môn giảng dạy</label>
                <input 
                  type="text" 
                  placeholder="Ví dụ: Tiếng Anh THCS, Tiếng Anh THPT..." 
                  value={teacherForm.subject}
                  onChange={e => setTeacherForm({ ...teacherForm, subject: e.target.value })}
                  required
                />
              </div>

              <div>
                <label>Mật khẩu</label>
                <input 
                  type="password"
                  placeholder={teacherModal.mode === 'create' ? 'Mặc định: 88888888' : 'Để trống nếu không đổi'}
                  value={teacherForm.password}
                  onChange={e => setTeacherForm({ ...teacherForm, password: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
                <button 
                  type="button" 
                  className="btn btn-outline"
                  onClick={() => setTeacherModal({ open: false, mode: 'create', data: null })}
                >
                  Hủy
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  Lưu lại
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==========================================================
          MODALS: QUESTION (EDIT)
          ========================================================== */}
      {editQuestionModal.open && editQuestionModal.data && (
        <div className="modal-overlay">
          <div className="modal-card animate-fade-in" style={{ maxWidth: '640px' }}>
            <button 
              className="modal-close-btn" 
              onClick={() => setEditQuestionModal({ open: false, data: null })}
            >
              <X size={24} />
            </button>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '20px' }}>
              Sửa câu hỏi: {editQuestionModal.data.question_id}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="modal-form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Mã câu (question_id)</label>
                  <input 
                    type="text" 
                    value={editQuestionModal.data.question_id || ''}
                    onChange={e => setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, question_id: e.target.value } })}
                    style={{ width: '100%' }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Loại</label>
                  <select 
                    value={editQuestionModal.data.type || 'read_choice'}
                    onChange={e => setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, type: e.target.value } })}
                    style={{ width: '100%' }}
                  >
                    <option value="read_choice">Đọc</option>
                    <option value="listen_choice">Nghe</option>
                  </select>
                </div>
              </div>

              <div className="modal-form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Skill ID</label>
                  <input 
                    type="text" 
                    value={editQuestionModal.data.skill_id || ''}
                    onChange={e => setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, skill_id: e.target.value } })}
                    style={{ width: '100%' }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Tên kỹ năng</label>
                  <input 
                    type="text" 
                    value={editQuestionModal.data.skill_name || ''}
                    onChange={e => setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, skill_name: e.target.value } })}
                    style={{ width: '100%' }}
                  />
                </div>
              </div>

              <div className="modal-form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Độ khó</label>
                  <select 
                    value={editQuestionModal.data.difficulty || 'medium'}
                    onChange={e => setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, difficulty: e.target.value } })}
                    style={{ width: '100%' }}
                  >
                    <option value="easy">Dễ</option>
                    <option value="medium">Trung bình</option>
                    <option value="hard">Khó</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Đáp án đúng</label>
                  <select 
                    value={editQuestionModal.data.correct_option_id || 'A'}
                    onChange={e => setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, correct_option_id: e.target.value } })}
                    style={{ width: '100%' }}
                  >
                    {['A','B','C','D'].map(opt => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Nội dung câu hỏi (prompt.text)</label>
                <textarea 
                  rows={2}
                  value={editQuestionModal.data.prompt?.text || ''}
                  onChange={e => setEditQuestionModal({ 
                    ...editQuestionModal, 
                    data: { ...editQuestionModal.data, prompt: { ...editQuestionModal.data.prompt, text: e.target.value } }
                  })}
                  style={{ width: '100%', resize: 'vertical' }}
                />
              </div>

              {/* Options */}
              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '8px', display: 'block' }}>Các lựa chọn (A, B, C, D)</label>
                {(editQuestionModal.data.options || []).map((opt, idx) => (
                  <div key={opt.option_id} style={{ display: 'flex', gap: '8px', marginBottom: '6px', alignItems: 'center' }}>
                    <span style={{ fontWeight: '800', fontSize: '13px', color: 'var(--primary)', width: '20px' }}>{opt.option_id})</span>
                    <input 
                      type="text" 
                      value={opt.label}
                      onChange={e => {
                        const newOpts = [...editQuestionModal.data.options];
                        newOpts[idx] = { ...newOpts[idx], label: e.target.value };
                        setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, options: newOpts } });
                      }}
                      style={{ flex: 1 }}
                    />
                  </div>
                ))}
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Giải thích</label>
                <textarea 
                  rows={2}
                  value={editQuestionModal.data.explanation || ''}
                  onChange={e => setEditQuestionModal({ ...editQuestionModal, data: { ...editQuestionModal.data, explanation: e.target.value } })}
                  style={{ width: '100%', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '8px' }}>
                <button 
                  className="btn btn-outline"
                  onClick={() => setEditQuestionModal({ open: false, data: null })}
                >
                  Hủy
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => handleUpdateQuestion(editQuestionModal.data.id, editQuestionModal.data)}
                >
                  Lưu lại
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==========================================================
          MODALS: PLACEMENT TEST (EDIT)
          ========================================================== */}
      {editTestModal.open && editTestModal.data && (
        <div className="modal-overlay">
          <div className="modal-card animate-fade-in" style={{ maxWidth: '560px' }}>
            <button 
              className="modal-close-btn" 
              onClick={() => setEditTestModal({ open: false, data: null })}
            >
              <X size={24} />
            </button>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '20px' }}>
              Sửa bài test: {editTestModal.data.test_id}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Tên bài kiểm tra</label>
                <input 
                  type="text" 
                  value={editTestModal.data.title || ''}
                  onChange={e => setEditTestModal({ ...editTestModal, data: { ...editTestModal.data, title: e.target.value } })}
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Mascot (icon + tên)</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <input 
                    type="text" 
                    value={editTestModal.data.mascot?.icon || ''}
                    placeholder="bee hoặc book"
                    onChange={e => setEditTestModal({ 
                      ...editTestModal, 
                      data: { ...editTestModal.data, mascot: { ...editTestModal.data.mascot, icon: e.target.value } }
                    })}
                    style={{ width: '100%' }}
                  />
                  <input 
                    type="text" 
                    value={editTestModal.data.mascot?.name || ''}
                    placeholder="Tên mascot"
                    onChange={e => setEditTestModal({ 
                      ...editTestModal, 
                      data: { ...editTestModal.data, mascot: { ...editTestModal.data.mascot, name: e.target.value } }
                    })}
                    style={{ width: '100%' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Chiến lược thi</label>
                <select 
                  value={editTestModal.data.adaptive_config?.strategy || 'level_sequential'}
                  onChange={e => setEditTestModal({ 
                    ...editTestModal, 
                    data: { ...editTestModal.data, adaptive_config: { ...editTestModal.data.adaptive_config, strategy: e.target.value } }
                  })}
                  style={{ width: '100%' }}
                >
                  <option value="level_sequential">Tuyến tính theo level</option>
                  <option value="adaptive">Thích ứng (Adaptive)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Số câu hỏi mỗi level</label>
                {editTestModal.data.levels && editTestModal.data.levels.map(lvl => {
                  const qpl = editTestModal.data.adaptive_config?.questions_per_level || {};
                  return (
                    <div key={lvl.level_id} style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontSize: '13px', fontWeight: '700', minWidth: '100px' }}>{lvl.label}</span>
                      <input 
                        type="number" 
                        min={1}
                        max={20}
                        value={qpl[lvl.level_id] || 5}
                        onChange={e => {
                          const newQpl = { ...qpl, [lvl.level_id]: parseInt(e.target.value) || 5 };
                          setEditTestModal({ 
                            ...editTestModal, 
                            data: { ...editTestModal.data, adaptive_config: { ...editTestModal.data.adaptive_config, questions_per_level: newQpl } }
                          });
                        }}
                        style={{ width: '60px' }}
                      />
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>câu</span>
                    </div>
                  );
                })}
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '8px' }}>
                <button 
                  className="btn btn-outline"
                  onClick={() => setEditTestModal({ open: false, data: null })}
                >
                  Hủy
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => handleUpdateTest(editTestModal.data.id, editTestModal.data)}
                >
                  Lưu lại
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==========================================================
          MODALS: ADD QUESTION TO PLACEMENT TEST
          ========================================================== */}
      {showAddQuestionModal && selectedTest && (
        <div className="modal-overlay">
          <div className="modal-card animate-fade-in" style={{ maxWidth: '820px', maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}>
            <button 
              className="modal-close-btn" 
              onClick={() => setShowAddQuestionModal(false)}
            >
              <X size={24} />
            </button>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-color)', marginBottom: '16px' }}>
              Chọn câu hỏi cho bài test
            </h3>

            {/* Filters */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
              <input 
                type="text"
                placeholder="Tìm kiếm câu hỏi..."
                value={addQuestionSearch}
                onChange={e => setAddQuestionSearch(e.target.value)}
                style={{ flex: 1, minWidth: '200px', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px' }}
              />
              <select 
                value={addQuestionSkillFilter}
                onChange={e => setAddQuestionSkillFilter(e.target.value)}
                style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px', fontWeight: '600' }}
              >
                <option value="">Tất cả kỹ năng</option>
                {[...new Set(questions.map(q => q.skill_id))].sort().map(sid => (
                  <option key={sid} value={sid}>{sid}</option>
                ))}
              </select>
              <select 
                value={addQuestionDiffFilter}
                onChange={e => setAddQuestionDiffFilter(e.target.value)}
                style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px', fontWeight: '600' }}
              >
                <option value="">Tất cả độ khó</option>
                <option value="easy">Dễ</option>
                <option value="medium">Trung bình</option>
                <option value="hard">Khó</option>
              </select>
            </div>

            {/* Current test question IDs */}
            {(() => {
              const currentIds = new Set(testQuestions.map(q => q.id));
              const filtered = questions.filter(q => {
                if (addQuestionSearch) {
                  const s = addQuestionSearch.toLowerCase();
                  if (!q.prompt?.text?.toLowerCase().includes(s) && 
                      !q.skill_name?.toLowerCase().includes(s) &&
                      !q.skill_id?.toLowerCase().includes(s) &&
                      !q.question_id?.toLowerCase().includes(s)) return false;
                }
                if (addQuestionSkillFilter && q.skill_id !== addQuestionSkillFilter) return false;
                if (addQuestionDiffFilter && q.difficulty !== addQuestionDiffFilter) return false;
                return true;
              });
              const selectedIds = new Set(filtered.filter(q => currentIds.has(q.id)).map(q => q.id));

              return (
                <>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    Đang chọn <strong style={{ color: 'var(--primary)' }}>{currentIds.size}</strong> câu hỏi | Hiển thị <strong>{filtered.length}</strong> câu
                  </div>

                  {/* Question list with checkboxes */}
                  <div style={{ flex: 1, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: '8px' }}>
                    <table className="custom-table" style={{ margin: 0 }}>
                      <thead>
                        <tr>
                          <th style={{ width: '40px', textAlign: 'center' }}>
                            <input 
                              type="checkbox"
                              checked={filtered.length > 0 && filtered.every(q => currentIds.has(q.id))}
                              onChange={e => {
                                if (e.target.checked) {
                                  const allIds = [...currentIds, ...filtered.map(q => q.id)];
                                  handleSaveTestQuestions(selectedTest.id, [...new Set(allIds)]);
                                } else {
                                  const keepIds = [...currentIds].filter(id => !filtered.some(q => q.id === id));
                                  handleSaveTestQuestions(selectedTest.id, keepIds);
                                }
                              }}
                            />
                          </th>
                          <th style={{ width: '90px' }}>Mã câu</th>
                          <th>Câu hỏi</th>
                          <th style={{ width: '120px' }}>Kỹ năng</th>
                          <th style={{ width: '80px' }}>Độ khó</th>
                          <th style={{ width: '60px' }}>Đáp án</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filtered.map(q => {
                          const isInTest = currentIds.has(q.id);
                          return (
                            <tr 
                              key={q.id}
                              style={{ 
                                background: isInTest ? 'rgba(79, 69, 229, 0.04)' : 'transparent',
                                cursor: 'pointer'
                              }}
                              onClick={() => {
                                let newIds;
                                if (isInTest) {
                                  newIds = [...currentIds].filter(id => id !== q.id);
                                } else {
                                  newIds = [...currentIds, q.id];
                                }
                                handleSaveTestQuestions(selectedTest.id, newIds);
                              }}
                            >
                              <td style={{ textAlign: 'center' }} onClick={e => e.stopPropagation()}>
                                <input 
                                  type="checkbox"
                                  checked={isInTest}
                                  onChange={() => {
                                    let newIds;
                                    if (isInTest) {
                                      newIds = [...currentIds].filter(id => id !== q.id);
                                    } else {
                                      newIds = [...currentIds, q.id];
                                    }
                                    handleSaveTestQuestions(selectedTest.id, newIds);
                                  }}
                                />
                              </td>
                              <td>
                                <span style={{ fontFamily: 'monospace', fontSize: '11px', fontWeight: '700', color: 'var(--primary)' }}>
                                  {q.question_id}
                                </span>
                              </td>
                              <td>
                                <div style={{ maxWidth: '300px' }}>
                                  <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '2px' }}>
                                    {q.prompt?.text || '—'}
                                  </div>
                                  <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                                    {q.options?.map(o => `${o.option_id}) ${o.label}`).join('  |  ')}
                                  </div>
                                </div>
                              </td>
                              <td>
                                <span className="badge badge-primary" style={{ fontSize: '10px' }}>{q.skill_id}</span>
                              </td>
                              <td>
                                <span className={`badge ${q.difficulty === 'easy' ? 'badge-success' : q.difficulty === 'hard' ? 'badge-danger' : 'badge-secondary'}`}>
                                  {q.difficulty === 'easy' ? 'Dễ' : q.difficulty === 'hard' ? 'Khó' : 'TB'}
                                </span>
                              </td>
                              <td style={{ fontWeight: '800', color: '#27c26c', textAlign: 'center' }}>
                                {q.correct_option_id}
                              </td>
                            </tr>
                          );
                        })}
                        {filtered.length === 0 && (
                          <tr>
                            <td colSpan="6" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                              Không tìm thấy câu hỏi nào.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </>
              );
            })()}

            {/* Footer */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
              <button 
                className="btn btn-outline"
                onClick={() => setShowAddQuestionModal(false)}
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
