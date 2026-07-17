import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
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
  LogOut
} from 'lucide-react';
import { useAuth } from './context/AuthContext';
import { apiFetch } from './api';
import Login from './pages/Login';
import './App.css';

// Base API URL
const API_BASE = "http://localhost:8000";

function App() {
  const { user, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Login />;
  }

  return <DashboardApp user={user} logout={logout} />;
}

function DashboardApp({ user, logout }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [students, setStudents] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Search queries
  const [studentSearch, setStudentSearch] = useState('');
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
    grade: 'Lớp 6'
  });

  const [teacherForm, setTeacherForm] = useState({
    name: '',
    email: '',
    subject: ''
  });

  // Fetch all data
  const fetchStudents = async () => {
    try {
      const res = await apiFetch('/api/students');
      if (res.ok) {
        const data = await res.json();
        setStudents(data);
      }
    } catch (err) {
      console.error("Error fetching students:", err);
    }
  };

  const fetchTeachers = async () => {
    try {
      const res = await apiFetch('/api/teachers');
      if (res.ok) {
        const data = await res.json();
        setTeachers(data);
      }
    } catch (err) {
      console.error("Error fetching teachers:", err);
    }
  };

  const fetchRankings = async () => {
    try {
      const res = await apiFetch('/api/rankings');
      if (res.ok) {
        const data = await res.json();
        setRankings(data);
      }
    } catch (err) {
      console.error("Error fetching rankings:", err);
    }
  };

  const loadAllData = async () => {
    setLoading(true);
    await Promise.all([fetchStudents(), fetchTeachers(), fetchRankings()]);
    setLoading(false);
  };

  useEffect(() => {
    loadAllData();
  }, []);

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
      // 1. Create Student
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

      const newStudent = await studentRes.json();

      // 2. Create Survey record linked to student ID
      const surveyRes = await apiFetch('/api/surveys', {
        method: 'POST',
        body: JSON.stringify({
          student_id: newStudent.id,
          years_studying_english: parseInt(surveyForm.years_studying_english) || 0,
          learning_environment: surveyForm.learning_environment,
          self_assessment_level: surveyForm.self_assessment_level,
          learning_goal: surveyForm.learning_goal
        })
      });

      if (!surveyRes.ok) {
        throw new Error("Không thể lưu kết quả khảo sát đầu vào");
      }

      triggerNotification("Khảo sát đầu vào đã được nộp thành công! Tài khoản học sinh đã được tạo.");
      
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

      const res = await apiFetch(url, {
        method,
        body: JSON.stringify(studentForm)
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

  // Teacher CRUD
  const handleTeacherSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const url = teacherModal.mode === 'create' 
        ? '/api/teachers'
        : `/api/teachers/${teacherModal.data.id}`;
      const method = teacherModal.mode === 'create' ? 'POST' : 'PUT';

      const res = await apiFetch(url, {
        method,
        body: JSON.stringify(teacherForm)
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
  const filteredStudents = students.filter(s => 
    s.name.toLowerCase().includes(studentSearch.toLowerCase()) ||
    s.email.toLowerCase().includes(studentSearch.toLowerCase()) ||
    (s.grade && s.grade.toLowerCase().includes(studentSearch.toLowerCase()))
  );

  const filteredTeachers = teachers.filter(t => 
    t.name.toLowerCase().includes(teacherSearch.toLowerCase()) ||
    t.email.toLowerCase().includes(teacherSearch.toLowerCase()) ||
    (t.subject && t.subject.toLowerCase().includes(teacherSearch.toLowerCase()))
  );

  // Sorting Rankings for top podium
  const sortedRankings = [...rankings].sort((a, b) => b.score - a.score);
  const podiumStudents = sortedRankings.slice(0, 3);

  // Total surveys count
  const totalSurveys = students.reduce((acc, curr) => acc + (curr.surveys?.length || 0), 0);
  const avgScore = rankings.length > 0 
    ? Math.round(rankings.reduce((acc, curr) => acc + curr.score, 0) / rankings.length)
    : 0;

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">V</div>
          <span>V-Nexus Tutor</span>
        </div>
        
        <div className="sidebar-menu">
          <button 
            className={`menu-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </button>

          {/* Students tab: visible to admin and teacher */}
          {(user?.role === 'admin' || user?.role === 'giao_vien') && (
            <button 
              className={`menu-item ${activeTab === 'students' ? 'active' : ''}`}
              onClick={() => { setActiveTab('students'); fetchStudents(); }}
            >
              <GraduationCap size={20} />
              <span>Học sinh</span>
            </button>
          )}

          {/* Teachers tab: admin only */}
          {user?.role === 'admin' && (
            <button 
              className={`menu-item ${activeTab === 'teachers' ? 'active' : ''}`}
              onClick={() => { setActiveTab('teachers'); fetchTeachers(); }}
            >
              <Users size={20} />
              <span>Giáo viên</span>
            </button>
          )}

          <button 
            className={`menu-item ${activeTab === 'leaderboard' ? 'active' : ''}`}
            onClick={() => { setActiveTab('leaderboard'); fetchRankings(); fetchStudents(); }}
          >
            <Trophy size={20} />
            <span>Bảng xếp hạng</span>
          </button>

          {/* Survey tab: visible to admin and teacher */}
          {(user?.role === 'admin' || user?.role === 'giao_vien') && (
            <button 
              className={`menu-item ${activeTab === 'survey' ? 'active' : ''}`}
              onClick={() => setActiveTab('survey')}
            >
              <BookOpen size={20} />
              <span>Khảo sát đầu vào</span>
            </button>
          )}
        </div>

        <div className="sidebar-footer">
          <p>V-Nexus Tutor</p>
          <p>Adaptive Platform v1.0</p>
        </div>
      </aside>

      {/* Main Wrapper */}
      <div className="main-wrapper">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-title">
            <h1>
              {activeTab === 'dashboard' && 'Tổng quan'}
              {activeTab === 'students' && 'Danh sách Học sinh'}
              {activeTab === 'teachers' && 'Danh sách Giáo viên'}
              {activeTab === 'leaderboard' && 'Bảng xếp hạng'}
              {activeTab === 'survey' && 'Khảo sát đầu vào'}
            </h1>
          </div>
          
          <div className="header-right">
            {/* Conditional Search bar in Header */}
            {activeTab === 'students' && (
              <div className="search-bar">
                <Search size={18} />
                <input 
                  type="text" 
                  placeholder="Tìm học sinh, email..." 
                  value={studentSearch}
                  onChange={e => setStudentSearch(e.target.value)}
                />
              </div>
            )}
            {activeTab === 'teachers' && (
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
            
            <div className="icon-buttons">
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
                    <BookOpen />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Khảo sát</span>
                    <span className="stat-val">{totalSurveys}</span>
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
              <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
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
                        {students.slice(0, 4).map(student => (
                          <tr key={student.id}>
                            <td>
                              <div className="student-meta">
                                <div className="avatar-circle" style={{ background: getAvatarColor(student.name) }}>
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
                              <span className={`badge ${student.ranking?.level === 'Expert' ? 'badge-success' : student.ranking?.level === 'Intermediate' ? 'badge-secondary' : 'badge-primary'}`}>
                                {student.ranking?.level || 'Beginner'}
                              </span>
                            </td>
                          </tr>
                        ))}
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
          {activeTab === 'students' && (
            <div className="animate-fade-in panel table-panel">
              <div className="table-header-bar">
                <h3 className="table-title">Chi tiết Học sinh</h3>
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    setStudentForm({ name: '', email: '', grade: 'Lớp 6' });
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
                            <span className={`badge ${student.ranking?.level === 'Expert' ? 'badge-success' : student.ranking?.level === 'Intermediate' ? 'badge-secondary' : 'badge-primary'}`}>
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
                                    grade: student.grade || 'Lớp 6'
                                  });
                                  setStudentModal({ open: true, mode: 'edit', data: student });
                                }}
                              >
                                <Edit3 size={14} />
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
              TAB: TEACHERS DIRECTORY
              ========================================================== */}
          {activeTab === 'teachers' && (
            <div className="animate-fade-in panel table-panel">
              <div className="table-header-bar">
                <h3 className="table-title">Chi tiết Giáo viên</h3>
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    setTeacherForm({ name: '', email: '', subject: '' });
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
                                    subject: teacher.subject || ''
                                  });
                                  setTeacherModal({ open: true, mode: 'edit', data: teacher });
                                }}
                              >
                                <Edit3 size={14} />
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
                          <span className={`badge ${rank.level === 'Expert' ? 'badge-success' : rank.level === 'Intermediate' ? 'badge-secondary' : 'badge-primary'}`}>
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
              TAB: SURVEY ONBOARDING FORM
              ========================================================== */}
          {activeTab === 'survey' && (
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

    </div>
  );
}

export default App;
