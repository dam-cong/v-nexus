import React, { useState } from 'react';
import { 
  Users, BookOpen, ClipboardCheck, GraduationCap, Award, 
  Settings, Bell, AlertTriangle, CheckCircle, Clock,
  Flame, Target, TrendingUp, MessageSquare, Play, ArrowRight
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  LineChart, Line, CartesianGrid,
  Radar, RadarChart, PolarGrid, PolarAngleAxis
} from 'recharts';
import TeacherDashboard from './TeacherDashboard';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('tong-quan');


  const renderStudentDashboard = () => (
    <div className="student-home animate-fade-in" style={{ padding: '20px 0' }}>
      <section className="student-welcome-hero" style={{ background: 'linear-gradient(135deg, #6c63ff 0%, #4d44b5 100%)', color: '#fff', padding: '32px', borderRadius: '16px', position: 'relative', overflow: 'hidden', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div style={{ flex: 1, zIndex: 2 }}>
          <span style={{ background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}><Award size={14} /> Trình học của em</span>
          <h2 style={{ fontSize: '24px', fontWeight: '800', margin: '0 0 8px', color: '#fff' }}>Chào Nguyễn Minh Anh, hôm nay mình cùng tiến thêm một bước nhé!</h2>
          <p style={{ margin: '0 0 20px', opacity: 0.9, fontSize: '14px', color: '#fff' }}>Lộ trình cá nhân của em đã sẵn sàng. Chỉ cần một chút đều đặn mỗi ngày để em tiến gần hơn tới mục tiêu.</p>
          <button style={{ background: '#fff', color: '#4d44b5', border: 'none', padding: '12px 24px', borderRadius: '8px', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}><Play size={16} fill="currentColor" /> Bắt đầu bài học tiếp theo</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', zIndex: 2, minWidth: '150px' }}>
          <div style={{ width: '90px', height: '90px', borderRadius: '50%', border: '6px solid rgba(255,255,255,0.2)', borderTopColor: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
            <strong style={{ fontSize: '20px', fontWeight: '800', color: '#fff' }}>85%</strong>
            <span style={{ fontSize: '10px', opacity: 0.8, color: '#fff' }}>Hoàn thành</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.15)', padding: '6px 12px', borderRadius: '20px', fontSize: '13px', color: '#fff' }}><Flame size={16} color="#ffa940" fill="#ffa940" /> <span><strong>5 ngày</strong> liên tục</span></div>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: '#e0e7ff', color: '#4f46e5', width: '48px', height: '48px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><ClipboardCheck size={24} /></div>
          <div><h4 style={{ margin: '0 0 4px', fontSize: '15px', fontWeight: 'bold' }}>Đánh giá năng lực</h4><p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>Khám phá trình độ hiện tại</p></div>
        </div>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: '#fef3c7', color: '#d97706', width: '48px', height: '48px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Target size={24} /></div>
          <div><h4 style={{ margin: '0 0 4px', fontSize: '15px', fontWeight: 'bold' }}>Lộ trình học tập</h4><p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>Học các bài cá nhân hóa</p></div>
        </div>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: '#dcfce7', color: '#15803d', width: '48px', height: '48px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Award size={24} /></div>
          <div><h4 style={{ margin: '0 0 4px', fontSize: '15px', fontWeight: 'bold' }}>Thành tích & XP</h4><p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>Nhìn lại quá trình tiến bộ</p></div>
        </div>
      </div>

      <div style={{ background: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}><GraduationCap size={20} color="#4d44b5" /> Hồ sơ năng lực</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}><span style={{ fontSize: '12px', color: '#64748b' }}>Trình độ CEFR</span><strong style={{ display: 'block', fontSize: '18px', color: '#4d44b5' }}>A2</strong></div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}><span style={{ fontSize: '12px', color: '#64748b' }}>Điểm trung bình</span><strong style={{ display: 'block', fontSize: '18px', color: '#4d44b5' }}>88%</strong></div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}><span style={{ fontSize: '12px', color: '#64748b' }}>Tổng số XP</span><strong style={{ display: 'block', fontSize: '18px', color: '#4d44b5' }}>2,450 XP</strong></div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}><span style={{ fontSize: '12px', color: '#64748b' }}>Ưu tiên ôn tập</span><strong style={{ display: 'block', fontSize: '18px', color: '#ef4444' }}>Thì quá khứ đơn</strong></div>
          </div>
        </div>
        <div style={{ height: '240px', background: '#f8fafc', borderRadius: '8px', padding: '12px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={[
              { subject: 'Nghe', score: 85 },
              { subject: 'Nói', score: 65 },
              { subject: 'Đọc', score: 90 },
              { subject: 'Viết', score: 75 }
            ]}>
              <PolarGrid stroke="#cbd5e1" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 12, fontWeight: 600 }} />
              <Radar name="Năng lực" dataKey="score" stroke="#4d44b5" fill="#4d44b5" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderParentDashboard = () => (
    <div className="parent-home animate-fade-in" style={{ padding: '20px 0' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <section className="student-welcome-hero" style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)', color: '#fff', padding: '32px', borderRadius: '16px', position: 'relative', overflow: 'hidden', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ zIndex: 2 }}>
              <span style={{ background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}><Users size={14} /> Góc Phụ Huynh</span>
              <h2 style={{ fontSize: '24px', fontWeight: '800', margin: '0 0 8px', color: '#fff' }}>Hành trình học tập của con</h2>
              <p style={{ margin: 0, opacity: 0.9, fontSize: '14px', color: '#fff' }}>Theo dõi tiến độ, xem nhận xét trực tiếp từ giáo viên và hỗ trợ lộ trình học tập của con.</p>
            </div>
            <div style={{ minWidth: '120px', zIndex: 2, background: 'rgba(255,255,255,0.2)', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
              <span style={{ fontSize: '12px', opacity: 0.8, color: '#fff', display: 'block' }}>Học sinh</span>
              <strong style={{ fontSize: '16px', fontWeight: '800', color: '#fff' }}>Nguyễn Minh Anh</strong>
            </div>
          </section>

          <div style={{ background: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 'bold', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}><ClipboardCheck size={20} color="#0ea5e9" /> Nhận xét từ giáo viên (Độc quyền Phụ huynh)</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #0ea5e9' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '12px', color: '#64748b' }}>
                  <strong style={{ color: '#0ea5e9' }}>Cô Hoa (Chủ nhiệm)</strong>
                  <span>19/07/2026 14:30</span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#1e293b', lineHeight: 1.5 }}>Học sinh Minh Anh có sự tập trung tốt trong giờ học nói. Khả năng phát âm cải thiện rõ rệt qua các bài tập tương tác AI.</p>
              </div>
              <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #cbd5e1' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '12px', color: '#64748b' }}>
                  <strong>Thầy Minh (Trợ giảng)</strong>
                  <span>15/07/2026 09:15</span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#1e293b', lineHeight: 1.5 }}>Con cần chú ý làm đầy đủ các bài tập ngữ pháp về Thì quá khứ đơn để đạt kết quả tốt nhất ở bài kiểm tra tuần tới.</p>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 16px', fontSize: '15px', fontWeight: 'bold' }}>Trạng thái học tập của con</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '8px' }}>
                <span style={{ color: '#64748b', fontSize: '13px' }}>Trình độ hiện tại</span>
                <strong style={{ color: '#0ea5e9' }}>A2 (Elementary)</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '8px' }}>
                <span style={{ color: '#64748b', fontSize: '13px' }}>Bài đã hoàn thành</span>
                <strong>42 bài học</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '8px' }}>
                <span style={{ color: '#64748b', fontSize: '13px' }}>Thời gian tự học</span>
                <strong>12.5 giờ</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#64748b', fontSize: '13px' }}>Mục tiêu tuần</span>
                <span style={{ color: '#22c55e', fontWeight: 'bold' }}>Đã đạt (150/100 XP)</span>
              </div>
            </div>
          </div>

          <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 12px', fontSize: '15px', fontWeight: 'bold' }}>Tiên trình học 4 tuần qua</h4>
            <div style={{ height: '150px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={[
                  { week: 'W1', score: 70 },
                  { week: 'W2', score: 75 },
                  { week: 'W3', score: 82 },
                  { week: 'W4', score: 88 }
                ]}>
                  <XAxis dataKey="week" tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Line type="monotone" dataKey="score" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Fake data for charts and stats
  const stats = {
    students: 320,
    classes: 8,
    completion: 94,
    mastery: 66,
    unsynced: 18,
    totalXp: '384K'
  };

  const levelDistribution = [
    { name: 'Pre-A1', value: 30 },
    { name: 'A1', value: 50 },
    { name: 'A2', value: 20 }
  ];

  const progressData = [
    { week: 'Tuần 1', chan_doan: 10, tich_luy: 5 },
    { week: 'Tuần 2', chan_doan: 25, tich_luy: 15 },
    { week: 'Tuần 3', chan_doan: 60, tich_luy: 40 },
    { week: 'Tuần 4', chan_doan: 90, tich_luy: 70 }
  ];

  const renderOverview = () => (
    <div className="animate-fade-in">
      <div className="admin-overview-grid">
        <div className="admin-card admin-stat-card">
          <div className="admin-stat-icon">
            <Users /> Học sinh
          </div>
          <div className="admin-stat-value" style={{color: '#3a2e9b'}}>{stats.students}</div>
        </div>
        <div className="admin-card admin-stat-card">
          <div className="admin-stat-icon">
            <BookOpen /> Lớp học
          </div>
          <div className="admin-stat-value" style={{color: '#3a2e9b'}}>{stats.classes}</div>
        </div>
        <div className="admin-card admin-stat-card">
          <div className="admin-stat-icon">
            <ClipboardCheck /> Hoàn thành chẩn đoán
          </div>
          <div className="admin-stat-value" style={{color: '#22c55e'}}>{stats.completion}%</div>
          <div className="admin-stat-progress">
            <div className="admin-stat-progress-bar" style={{width: `${stats.completion}%`, background: '#22c55e'}}></div>
          </div>
        </div>
        <div className="admin-card admin-stat-card">
          <div className="admin-stat-icon">
            <GraduationCap /> Mức độ thông thạo
          </div>
          <div className="admin-stat-value" style={{color: '#4f46e5'}}>{stats.mastery}%</div>
          <div className="admin-stat-progress">
            <div className="admin-stat-progress-bar" style={{width: `${stats.mastery}%`, background: '#4f46e5'}}></div>
          </div>
        </div>
        <div className="admin-card admin-stat-card" style={{background: '#fff1f2'}}>
          <div className="admin-stat-icon" style={{color: '#ef4444'}}>
            <Clock /> Chưa đồng bộ
          </div>
          <div className="admin-stat-value" style={{color: '#ef4444'}}>{stats.unsynced}</div>
        </div>
      </div>

      <div className="admin-section-grid">
        <div className="admin-card">
          <h3 className="admin-section-title">
            <span>Cảnh báo & Lưu ý</span>
            <AlertTriangle size={20} color="#ef4444" />
          </h3>
          <div className="admin-alert-list">
            <div className="admin-alert-item warning">
              <AlertTriangle className="admin-alert-icon" size={16} />
              <div className="admin-alert-content">
                <h4>Khối 4 - Tỷ lệ chưa đạt cao</h4>
                <p>Chủ đề "Past Simple Question Forms" đang gặp khó khăn.</p>
              </div>
            </div>
            <div className="admin-alert-item warning">
              <Users className="admin-alert-icon" size={16} />
              <div className="admin-alert-content">
                <h4>Lớp 4A & 4C cần hỗ trợ</h4>
                <p>Điểm số trung bình tuần qua thấp hơn mức chuẩn 15%.</p>
              </div>
            </div>
            <div className="admin-alert-item info">
              <Clock className="admin-alert-icon" size={16} />
              <div className="admin-alert-content">
                <h4>Dữ liệu lớp 3B chưa đồng bộ</h4>
                <p>Lần đồng bộ cuối cách đây 48 giờ. Vui lòng kiểm tra thiết bị.</p>
                <div className="admin-alert-action">Đồng bộ ngay</div>
              </div>
            </div>
          </div>
        </div>

        <div className="admin-card">
          <h3 className="admin-section-title">Phân bổ Trình độ</h3>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={levelDistribution} margin={{top: 20, right: 0, left: 0, bottom: 0}}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {levelDistribution.map((entry, index) => (
                    <cell key={`cell-${index}`} fill={index === 0 ? '#e2e8f0' : index === 1 ? '#3a2e9b' : '#b45309'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="admin-section-grid">
        <div className="admin-card" style={{ gridColumn: '1 / -1' }}>
          <h3 className="admin-section-title">Tiến độ chẩn đoán & Tích lũy XP</h3>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={progressData} margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="week" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} hide />
                <Tooltip />
                <Line type="monotone" dataKey="chan_doan" stroke="#22c55e" strokeWidth={3} strokeDasharray="5 5" dot={false} />
                <Line type="monotone" dataKey="tich_luy" stroke="#b45309" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );

  const renderClassAnalysis = () => (
    <div className="animate-fade-in">
      <div className="admin-card" style={{marginBottom: 24, background: '#f8fafc'}}>
        <div style={{display: 'flex', gap: 12, alignItems: 'center'}}>
          <div style={{color: '#3a2e9b'}}><CheckCircle /></div>
          <div>
            <h4 style={{margin: '0 0 4px', fontSize: 14}}>Chế độ bảo mật danh tính</h4>
            <p style={{margin: 0, fontSize: 13, color: '#64748b'}}>Dữ liệu đang được hiển thị dưới dạng tổng hợp khối/lớp. Tên học viên đã được ẩn để đảm bảo quyền riêng tư theo tiêu chuẩn FERPA/GDPR.</p>
          </div>
        </div>
      </div>

      <div className="admin-section-grid">
        <div className="admin-card">
          <h3 className="admin-section-title">Tiến độ chẩn đoán & Nắm vững</h3>
          <p style={{fontSize: 13, color: '#64748b', marginTop: -15, marginBottom: 20}}>So sánh phần trăm hoàn thành và tỷ lệ nắm vững kỹ năng chung.</p>
          
          <div className="admin-progress-row">
            <div className="admin-progress-label">3A</div>
            <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 8}}>
              <div className="admin-progress-track"><div className="admin-progress-fill" style={{width: '85%', background: '#3a2e9b'}}></div></div>
              <div className="admin-progress-track"><div className="admin-progress-fill" style={{width: '60%', background: '#b45309'}}></div></div>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: 8, width: 40, textAlign: 'right', fontSize: 12, fontWeight: 600}}>
              <div style={{color: '#3a2e9b'}}>85%</div>
              <div style={{color: '#b45309'}}>60%</div>
            </div>
          </div>

          <div className="admin-progress-row" style={{marginTop: 24}}>
            <div className="admin-progress-label">3B</div>
            <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 8}}>
              <div className="admin-progress-track"><div className="admin-progress-fill" style={{width: '92%', background: '#3a2e9b'}}></div></div>
              <div className="admin-progress-track"><div className="admin-progress-fill" style={{width: '75%', background: '#b45309'}}></div></div>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: 8, width: 40, textAlign: 'right', fontSize: 12, fontWeight: 600}}>
              <div style={{color: '#3a2e9b'}}>92%</div>
              <div style={{color: '#b45309'}}>75%</div>
            </div>
          </div>
        </div>

        <div className="admin-card">
          <h3 className="admin-section-title">Trạng thái dữ liệu lớp học</h3>
          <p style={{fontSize: 13, color: '#64748b', marginTop: -15, marginBottom: 20}}>Độ tin cậy và tình trạng đồng bộ dữ liệu của từng lớp.</p>
          
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16}}>
            <div style={{padding: 16, background: '#f0fdf4', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 12}}>
              <CheckCircle color="#22c55e" size={20} />
              <div>
                <h4 style={{margin: 0, fontSize: 14}}>Đủ dữ liệu</h4>
                <p style={{margin: 0, fontSize: 12, color: '#64748b'}}>3A, 3B, 4A</p>
              </div>
            </div>
            <div style={{padding: 16, background: '#fef2f2', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 12}}>
              <AlertTriangle color="#ef4444" size={20} />
              <div>
                <h4 style={{margin: 0, fontSize: 14}}>Thiếu dữ liệu</h4>
                <p style={{margin: 0, fontSize: 12, color: '#64748b'}}>3C, 4D</p>
              </div>
            </div>
            <div style={{padding: 16, background: '#f1f5f9', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 12}}>
              <Clock color="#64748b" size={20} />
              <div>
                <h4 style={{margin: 0, fontSize: 14}}>Chưa đồng bộ</h4>
                <p style={{margin: 0, fontSize: 12, color: '#64748b'}}>3D</p>
              </div>
            </div>
            <div style={{padding: 16, background: '#fffbeb', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 12}}>
              <Clock color="#f59e0b" size={20} />
              <div>
                <h4 style={{margin: 0, fontSize: 14}}>Dữ liệu cũ</h4>
                <p style={{margin: 0, fontSize: 12, color: '#64748b'}}>4B, 4C</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="admin-card">
        <h3 className="admin-section-title">Bản đồ nhiệt: Nhóm kỹ năng theo lớp</h3>
        <p style={{fontSize: 13, color: '#64748b', marginTop: -15, marginBottom: 20}}>Tỷ lệ phần trăm nắm vững kiến thức tổng hợp theo từng nhóm kỹ năng cụ thể.</p>
        
        <table className="admin-heatmap-table">
          <thead>
            <tr>
              <th>Lớp</th>
              <th>Vocabulary</th>
              <th>Grammar</th>
              <th>Reading</th>
              <th>Listening</th>
              <th>Past Simple</th>
              <th>Some/Any</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>3A</td>
              <td><span className="heatmap-cell" style={{background: '#f3e8ff', color: '#9333ea'}}>85%</span></td>
              <td><span className="heatmap-cell" style={{background: '#ffedd5', color: '#ea580c'}}>60%</span></td>
              <td><span className="heatmap-cell" style={{background: '#dcfce7', color: '#16a34a'}}>90%</span></td>
              <td><span className="heatmap-cell" style={{background: '#fce7f3', color: '#db2777'}}>75%</span></td>
              <td><span className="heatmap-cell" style={{background: '#ffe4e6', color: '#e11d48'}}>45%</span></td>
              <td><span className="heatmap-cell" style={{background: '#f1f5f9', color: '#64748b'}}>N/A</span></td>
            </tr>
            <tr>
              <td>3B</td>
              <td><span className="heatmap-cell" style={{background: '#dcfce7', color: '#16a34a'}}>92%</span></td>
              <td><span className="heatmap-cell" style={{background: '#e0e7ff', color: '#4f46e5'}}>80%</span></td>
              <td><span className="heatmap-cell" style={{background: '#f3e8ff', color: '#9333ea'}}>78%</span></td>
              <td><span className="heatmap-cell" style={{background: '#ffedd5', color: '#ea580c'}}>65%</span></td>
              <td><span className="heatmap-cell" style={{background: '#f1f5f9', color: '#64748b'}}>N/A</span></td>
              <td><span className="heatmap-cell" style={{background: '#ffe4e6', color: '#e11d48'}}>50%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderLeaderboard = () => (
    <div className="animate-fade-in">
      <div className="admin-card" style={{marginBottom: 24}}>
        <h3 className="admin-section-title" style={{justifyContent: 'center', marginBottom: 40}}>
          Top Học Viên Xuất Sắc Nhất Tuần
        </h3>
        <div className="admin-podium-container">
          <div className="admin-podium second">
            <img src="https://i.pravatar.cc/150?img=11" className="admin-podium-avatar" alt="Avatar" />
            <div className="admin-podium-info">
              <div className="admin-podium-name">Nguyễn Văn A</div>
              <div className="admin-podium-class">Lớp 3A1</div>
              <div className="admin-podium-xp" style={{color: '#64748b'}}>4,200 XP</div>
            </div>
            <div className="admin-podium-base">
              <Award size={32} />
            </div>
          </div>
          <div className="admin-podium first">
            <img src="https://i.pravatar.cc/150?img=5" className="admin-podium-avatar" alt="Avatar" />
            <div className="admin-podium-info">
              <div className="admin-podium-name">Trần Thị B</div>
              <div className="admin-podium-class">Lớp 4B2</div>
              <div className="admin-podium-xp" style={{color: '#3a2e9b', fontSize: 24}}>5,850 XP</div>
            </div>
            <div className="admin-podium-base">
              <Award size={48} />
            </div>
          </div>
          <div className="admin-podium third">
            <img src="https://i.pravatar.cc/150?img=12" className="admin-podium-avatar" alt="Avatar" />
            <div className="admin-podium-info">
              <div className="admin-podium-name">Lê Văn C</div>
              <div className="admin-podium-class">Lớp 3A3</div>
              <div className="admin-podium-xp" style={{color: '#ea580c'}}>3,900 XP</div>
            </div>
            <div className="admin-podium-base">
              <Award size={24} />
            </div>
          </div>
        </div>
      </div>

      <div className="admin-section-grid">
        <div className="admin-card">
          <h3 className="admin-section-title">
            <span style={{display: 'flex', alignItems: 'center', gap: 8}}>
              <Users size={20} color="#ea580c" /> Lớp Sôi Nổi Nhất
            </span>
          </h3>
          <div className="admin-lb-list">
            <div className="admin-lb-item">
              <div className="admin-lb-rank r1">1</div>
              <div className="admin-lb-details">
                <div className="admin-lb-title">Lớp 4B2</div>
                <div className="admin-lb-sub">GV: Cô Hoa</div>
              </div>
              <div className="admin-lb-score-col">
                <div className="admin-lb-score">125,000 XP</div>
                <div className="admin-lb-bar" style={{width: 100, background: '#b45309'}}></div>
              </div>
            </div>
            <div className="admin-lb-item">
              <div className="admin-lb-rank r2">2</div>
              <div className="admin-lb-details">
                <div className="admin-lb-title">Lớp 3A1</div>
                <div className="admin-lb-sub">GV: Thầy Minh</div>
              </div>
              <div className="admin-lb-score-col">
                <div className="admin-lb-score">112,400 XP</div>
                <div className="admin-lb-bar" style={{width: 85, background: '#4f46e5'}}></div>
              </div>
            </div>
            <div className="admin-lb-item">
              <div className="admin-lb-rank r3">3</div>
              <div className="admin-lb-details">
                <div className="admin-lb-title">Lớp 4A1</div>
                <div className="admin-lb-sub">GV: Cô Lan</div>
              </div>
              <div className="admin-lb-score-col">
                <div className="admin-lb-score">98,200 XP</div>
                <div className="admin-lb-bar" style={{width: 70, background: '#4f46e5'}}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="admin-card">
          <h3 className="admin-section-title">
            <span style={{display: 'flex', alignItems: 'center', gap: 8}}>
              <Award size={20} color="#f59e0b" /> Chuỗi Ngày Học Dài Nhất
            </span>
          </h3>
          <div className="admin-streak-grid">
            <div className="admin-streak-card">
              <div className="admin-streak-days">45 <span>ngày</span></div>
              <div className="admin-streak-name">Hoàng Anh</div>
              <div className="admin-streak-class">Lớp 4B2</div>
            </div>
            <div className="admin-streak-card">
              <div className="admin-streak-days">32 <span>ngày</span></div>
              <div className="admin-streak-name">Minh Tú</div>
              <div className="admin-streak-class">Lớp 3A1</div>
            </div>
            <div className="admin-streak-card">
              <div className="admin-streak-days">28 <span>ngày</span></div>
              <div className="admin-streak-name">Bảo Châu</div>
              <div className="admin-streak-class">Lớp 4A1</div>
            </div>
            <div className="admin-streak-card" style={{background: '#f1f5f9', color: '#64748b', cursor: 'pointer'}}>
              <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8}}>
                <div style={{width: 32, height: 32, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                  <BookOpen size={16} />
                </div>
                <div style={{fontSize: 14, fontWeight: 600}}>Xem tất cả</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="admin-card">
        <h3 className="admin-section-title">
          <span style={{display: 'flex', alignItems: 'center', gap: 8}}>
            <Award size={20} color="#22c55e" /> Huy Hiệu Mới Đạt Được
          </span>
        </h3>
        <div className="admin-badges-list">
          <div className="admin-badge-item green">
            <div className="admin-badge-icon"><Award /></div>
            <div className="admin-badge-info">
              <h4>Bộ Não Thiên Tài</h4>
              <p>Đạt điểm tuyệt đối 5 bài kiểm tra.</p>
              <div className="admin-badge-avatars">
                <div className="admin-badge-avatar" style={{background: '#3a2e9b'}}>A</div>
                <div className="admin-badge-avatar" style={{background: '#ea580c'}}>B</div>
                <div className="admin-badge-avatar more">+12</div>
              </div>
            </div>
          </div>
          <div className="admin-badge-item blue">
            <div className="admin-badge-icon"><Users /></div>
            <div className="admin-badge-info">
              <h4>Đồng Đội Gương Mẫu</h4>
              <p>Giúp đỡ bạn cùng lớp hoàn thành bài.</p>
              <div className="admin-badge-avatars">
                <div className="admin-badge-avatar" style={{background: '#16a34a'}}>C</div>
                <div className="admin-badge-avatar" style={{background: '#db2777'}}>D</div>
                <div className="admin-badge-avatar more">+8</div>
              </div>
            </div>
          </div>
          <div className="admin-badge-item orange">
            <div className="admin-badge-icon"><Clock /></div>
            <div className="admin-badge-info">
              <h4>Tốc Độ Ánh Sáng</h4>
              <p>Nộp bài tập sớm nhất lớp 3 lần.</p>
              <div className="admin-badge-avatars">
                <div className="admin-badge-avatar" style={{background: '#9333ea'}}>E</div>
                <div className="admin-badge-avatar more">+5</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="admin-dashboard">
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24}}>
        <h2 style={{fontSize: 28, fontWeight: 800, color: '#3a2e9b', margin: 0}}>
          {activeTab === 'tong-quan' && 'Tổng quan Trường Tiểu học V-Nexus'}
          {activeTab === 'khoi-lop' && 'Phân tích theo khối và lớp'}
          {activeTab === 'vinh-danh' && 'Vinh danh nỗ lực học tập'}
          {activeTab === 'hoc-sinh' && 'Dashboard Học sinh (Demo)'}
          {activeTab === 'phu-huynh' && 'Dashboard Phụ huynh (Demo)'}
          {activeTab === 'giao-vien' && 'Dashboard Giáo viên (Demo)'}
        </h2>
      </div>

      <div className="admin-tab-nav">
        <button className={`admin-tab-btn ${activeTab === 'tong-quan' ? 'active' : ''}`} onClick={() => setActiveTab('tong-quan')}>Tổng quan</button>
        <button className={`admin-tab-btn ${activeTab === 'khoi-lop' ? 'active' : ''}`} onClick={() => setActiveTab('khoi-lop')}>Khối và lớp</button>
        <button className={`admin-tab-btn`} style={{opacity: 0.5, cursor: 'not-allowed'}}>Cảnh báo</button>
        <button className={`admin-tab-btn ${activeTab === 'vinh-danh' ? 'active' : ''}`} onClick={() => setActiveTab('vinh-danh')}>Vinh danh XP</button>
        <button className={`admin-tab-btn`} style={{opacity: 0.5, cursor: 'not-allowed'}}>Nguồn lực</button>
        <button className={`admin-tab-btn ${activeTab === 'hoc-sinh' ? 'active' : ''}`} onClick={() => setActiveTab('hoc-sinh')}>Học sinh</button>
        <button className={`admin-tab-btn ${activeTab === 'phu-huynh' ? 'active' : ''}`} onClick={() => setActiveTab('phu-huynh')}>Phụ huynh</button>
        <button className={`admin-tab-btn ${activeTab === 'giao-vien' ? 'active' : ''}`} onClick={() => setActiveTab('giao-vien')}>Giáo viên</button>

        {activeTab === 'tong-quan' && (
          <div className="admin-tab-filters">
            <select><option>Tất cả các khối</option></select>
            <select><option>Tất cả các lớp</option></select>
            <select><option>Tháng này</option></select>
          </div>
        )}
      </div>

      {activeTab === 'tong-quan' && renderOverview()}
      {activeTab === 'khoi-lop' && renderClassAnalysis()}
      {activeTab === 'vinh-danh' && renderLeaderboard()}
      {activeTab === 'hoc-sinh' && renderStudentDashboard()}
      {activeTab === 'phu-huynh' && renderParentDashboard()}
      {activeTab === 'giao-vien' && <TeacherDashboard />}
    </div>
  );
};

export default AdminDashboard;
