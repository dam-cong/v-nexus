import React, { useState } from 'react';
import './TeacherDashboard.css';
import {
  AlertTriangle, Info, RefreshCw, CheckCircle, Download, Shield,
  TrendingUp, Activity, BarChart2, Star, Zap, Users,
  ChevronRight, Award, Flame, Eye
} from 'lucide-react';

// Fake Data Constants
const FAKE_STUDENTS_AI = [
  { id: 1, name: 'Nguyễn Minh Anh', class: 'Lớp 4A', acc: 88, spd: 'Vừa', eff: 'Cao', comment: 'Học sinh có tiến bộ vượt bậc, đủ điều kiện nâng cấp trình độ.', action: 'Xác nhận' },
  { id: 2, name: 'Trần Thị Bảo', class: 'Lớp 4A', acc: 88, spd: 'Vừa', eff: 'Cao', comment: 'Nắm vững cấu trúc ngữ pháp cơ bản.', action: 'Xác nhận' },
  { id: 3, name: 'Lê Văn Cường', class: 'Lớp 4A', acc: 88, spd: 'Vừa', eff: 'Cao', comment: 'Cần thêm thử thách để duy trì động lực.', action: 'Xác nhận' },
  { id: 4, name: 'Phạm Hoàng Nam', class: 'Lớp 4A', acc: 92, spd: 'Nhanh', eff: 'Cao', comment: 'Kỹ năng nghe hiểu rất tốt, cần phát huy thêm phần nói.', action: 'Xác nhận' },
  { id: 5, name: 'Đỗ Thu Hà', class: 'Lớp 4A', acc: 85, spd: 'Vừa', eff: 'Ổn định', comment: 'Hoàn thành tốt các bài tập về nhà, tích cực phát biểu.', action: 'Xác nhận' },
  { id: 6, name: 'Lý Thanh Tùng', class: 'Lớp 4A', acc: 78, spd: 'Chậm', eff: 'Cần cố gắng', comment: 'Cần tập trung hơn vào từ vựng chuyên ngành.', action: 'Xác nhận' },
  { id: 7, name: 'Trần Tuấn Kiệt', class: 'Lớp 4A', acc: 90, spd: 'Nhanh', eff: 'Cao', comment: 'Khả năng tư duy logic tốt, cần rèn luyện thêm tốc độ viết.', action: 'Xác nhận' },
  { id: 8, name: 'Hoàng Diệu Mai', class: 'Lớp 4A', acc: 82, spd: 'Vừa', eff: 'Ổn định', comment: 'Cần chú ý hơn đến các lỗi chính tả cơ bản.', action: 'Xác nhận' },
];

const FAKE_XP_LEADERBOARD = [
  { id: 1, name: 'Lớp 4B2', teacher: 'GV: Cô Hoa', xp: 125000, pct: 100 },
  { id: 2, name: 'Lớp 3A1', teacher: 'Thầy Minh', xp: 112400, pct: 90 },
  { id: 3, name: 'Lớp 4A1', teacher: 'Cô Lan', xp: 98200, pct: 78 }
];

export default function TeacherDashboard() {
  const [currentView, setCurrentView] = useState('attention');
  const [subView, setSubView] = useState('ai-recommendations'); // For views with sub-menus

  const renderAttentionView = () => (
    <div className="attention-grid">
      <div className="attention-cards">
        <div className="attention-card urgent">
          <div className="attention-card-header">
            <div className="attention-title-group">
              <div className="attention-icon"><AlertTriangle size={20} /></div>
              <div>
                <h3 className="attention-title">Lớp 4A - Ngữ pháp</h3>
                <p className="attention-subtitle">Past Simple Question Forms</p>
              </div>
            </div>
            <span className="attention-badge">Khẩn cấp</span>
          </div>
          <div className="attention-stats">
            <div className="stat-item">
              <span className="stat-label">Tỷ lệ chưa đạt</span>
              <span className="stat-value red">57%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Học sinh hợp lệ</span>
              <span className="stat-value">32/35</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Xu hướng</span>
              <span className="stat-value" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <TrendingUp size={20} style={{ color: '#ff4d4f', transform: 'rotate(180deg)' }} /> Giảm
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Trạng thái</span>
              <span className="stat-value" style={{ fontSize: '15px', color: 'var(--text-muted)' }}>Chưa xử lý</span>
            </div>
          </div>
          <div className="attention-footer">
            <div className="attention-hint">
              <Star size={16} /> Gợi ý: Hỗ trợ từ giáo viên & Dạy lại.
            </div>
            <div className="attention-actions">
              <button className="btn-soft">Chi tiết</button>
              <button className="btn-solid" style={{ background: '#4d44b5' }}>Giao hỗ trợ</button>
            </div>
          </div>
        </div>

        <div className="attention-card warning">
          <div className="attention-card-header">
            <div className="attention-title-group">
              <div className="attention-icon"><Info size={20} /></div>
              <div>
                <h3 className="attention-title">Lớp 4C - Từ vựng</h3>
                <p className="attention-subtitle">Some / Any</p>
              </div>
            </div>
            <span className="attention-badge">Cần chú ý</span>
          </div>
          <div className="attention-stats">
            <div className="stat-item">
              <span className="stat-label">Cần thực hành</span>
              <span className="stat-value orange">49%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Học sinh hợp lệ</span>
              <span className="stat-value">28/30</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Xu hướng</span>
              <span className="stat-value" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Activity size={20} style={{ color: '#fb7d5b' }} /> Đi ngang
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Trạng thái</span>
              <span className="stat-value" style={{ fontSize: '15px', color: 'var(--text-muted)' }}>Chưa xử lý</span>
            </div>
          </div>
          <div className="attention-footer">
            <div className="attention-hint">
              <Star size={16} /> Gợi ý: Cung cấp tài liệu nhóm.
            </div>
            <div className="attention-actions">
              <button className="btn-soft">Chi tiết</button>
              <button className="btn-solid" style={{ background: '#4d44b5' }}>Cung cấp tài liệu</button>
            </div>
          </div>
        </div>

        <div className="attention-card tech">
          <div className="attention-card-header">
            <div className="attention-title-group">
              <div className="attention-icon"><RefreshCw size={20} /></div>
              <div>
                <h3 className="attention-title">Lớp 3B - Hệ thống</h3>
                <p className="attention-subtitle">Đồng bộ dữ liệu</p>
              </div>
            </div>
            <span className="attention-badge">Kỹ thuật</span>
          </div>
          <div className="attention-stats">
            <div className="stat-item">
              <span className="stat-label">Dữ liệu chưa đồng bộ</span>
              <span className="stat-value" style={{ color: '#1e293b' }}>22%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Độ phủ dữ liệu</span>
              <span className="stat-value" style={{ color: '#1e293b' }}>Thấp</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Trạng thái</span>
              <span className="stat-value" style={{ fontSize: '15px', color: 'var(--text-muted)' }}>Đang chờ kiểm tra</span>
            </div>
          </div>
          <div className="attention-footer">
            <div className="attention-hint" style={{ color: '#fb7d5b' }}>
              <AlertTriangle size={16} /> Gợi ý: Kiểm tra thiết bị / kết nối.
            </div>
            <div className="attention-actions">
              <button className="btn-soft" style={{ background: '#e2e8f0' }}>Đã xử lý</button>
              <button className="btn-solid" style={{ background: '#4d44b5' }}>Gửi IT hỗ trợ</button>
            </div>
          </div>
        </div>
      </div>

      <div className="sidebar-panels">
        <div className="side-panel">
          <h3>Hành động nhanh</h3>
          <div className="action-list">
            <div className="action-list-item">
              <CheckCircle size={20} className="icon" />
              Đánh dấu đã đọc tất cả
            </div>
            <div className="action-list-item">
              <Download size={20} className="icon" />
              Xuất báo cáo
            </div>
          </div>
        </div>
        
        <div className="side-panel">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={20} className="icon" style={{ color: '#27c26c' }} />
            Nguyên tắc bảo mật
          </h3>
          <div className="rules-list">
            <div className="rule-item">
              <CheckCircle size={16} className="rule-icon" /> Chỉ hiển thị dữ liệu tổng hợp.
            </div>
            <div className="rule-item">
              <CheckCircle size={16} className="rule-icon" /> Không hiển thị hồ sơ cá nhân.
            </div>
            <div className="rule-item">
              <CheckCircle size={16} className="rule-icon" /> Không bêu rếu lỗ hổng cá nhân.
            </div>
            <div className="rule-item">
              <CheckCircle size={16} className="rule-icon" /> XP chỉ dành cho sự công nhận nỗ lực.
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAIRecommendations = () => (
    <div className="ai-table-card">
      <table className="ai-table">
        <thead>
          <tr>
            <th>Học sinh</th>
            <th>Thông số</th>
            <th>Nhận xét AI</th>
            <th>Phê duyệt</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          {FAKE_STUDENTS_AI.map(s => (
            <tr key={s.id}>
              <td>
                <div className="ai-student-info">
                  <div className="ai-student-avatar" style={{ background: `hsl(${s.id * 50}, 70%, 60%)` }}>
                    {s.name.charAt(0)}
                  </div>
                  <div>
                    <div className="ai-student-name">{s.name}</div>
                    <div className="ai-student-class">{s.class}</div>
                  </div>
                </div>
              </td>
              <td>
                <div className="ai-stats-grid">
                  <div className="ai-stat-lbl">Acc</div>
                  <div className="ai-stat-lbl">Spd</div>
                  <div className="ai-stat-lbl">Eff</div>
                  <div className="ai-stat-val">{s.acc}%</div>
                  <div className="ai-stat-val">{s.spd}</div>
                  <div className="ai-stat-val">{s.eff}</div>
                </div>
              </td>
              <td style={{ width: '35%' }}>
                <div className="ai-comment-box">{s.comment}</div>
              </td>
              <td>
                <span className="btn-pass">Pass <ChevronRight size={14} style={{ transform: 'rotate(90deg)' }} /></span>
              </td>
              <td>
                <button className="btn-solid" style={{ background: '#4d44b5' }}>{s.action}</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderClassOverview = () => (
    <div className="overview-grid">
      <div className="overview-main">
        <div className="overview-stats">
          <div className="overview-stat-card">
            <div className="overview-stat-label">Học sinh</div>
            <div className="overview-stat-value">40</div>
          </div>
          <div className="overview-stat-card">
            <div className="overview-stat-label">Hoàn thành</div>
            <div className="overview-stat-value green">36</div>
          </div>
          <div className="overview-stat-card">
            <div className="overview-stat-label">Độ thành thạo</div>
            <div className="overview-stat-value orange">63%</div>
          </div>
          <div className="overview-stat-card">
            <div className="overview-stat-label">Cần ôn tập</div>
            <div className="overview-stat-value orange">8</div>
          </div>
          <div className="overview-stat-card">
            <div className="overview-stat-label">Nhóm đề xuất</div>
            <div className="overview-stat-value">4</div>
          </div>
        </div>

        <div className="heatmap-panel">
          <div className="heatmap-header">
            <h3 className="heatmap-title">Bản đồ kỹ năng (Skill Heatmap)</h3>
            <div className="heatmap-legend">
              <div className="legend-item"><div className="legend-dot green"></div> Thành thạo</div>
              <div className="legend-item"><div className="legend-dot purple"></div> Đang tiến bộ</div>
              <div className="legend-item"><div className="legend-dot orange"></div> Cần củng cố</div>
              <div className="legend-item"><div className="legend-dot blue"></div> Thiếu dữ liệu</div>
              <div className="legend-item"><div className="legend-dot dashed"></div> Chưa ĐB</div>
            </div>
          </div>
          <table className="heatmap-table">
            <thead>
              <tr>
                <th style={{ textAlign: 'left', transform: 'none' }}>Học sinh/Nhóm</th>
                <th>Present Simple</th>
                <th>Adverbs of Freq</th>
                <th>Some/Any</th>
                <th>Past Simple</th>
                <th>Comparatives</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="label group">Nhóm Tăng tốc (8)</td>
                <td><div className="hm-cell green"></div></td>
                <td><div className="hm-cell green"></div></td>
                <td><div className="hm-cell purple"></div></td>
                <td><div className="hm-cell orange"></div></td>
                <td><div className="hm-cell green"></div></td>
              </tr>
              <tr>
                <td className="label">Nguyễn Văn A</td>
                <td><div className="hm-cell green"></div></td>
                <td><div className="hm-cell green"></div></td>
                <td><div className="hm-cell green"></div></td>
                <td><div className="hm-cell dashed"></div></td>
                <td><div className="hm-cell green"></div></td>
              </tr>
              <tr>
                <td className="label">Trần Thị B</td>
                <td><div className="hm-cell green"></div></td>
                <td><div className="hm-cell green"></div></td>
                <td><div className="hm-cell purple"></div></td>
                <td><div className="hm-cell purple"></div></td>
                <td><div className="hm-cell purple"></div></td>
              </tr>
              <tr>
                <td className="label group">Nhóm Củng cố (5)</td>
                <td><div className="hm-cell purple"></div></td>
                <td><div className="hm-cell orange"></div></td>
                <td><div className="hm-cell orange"></div></td>
                <td><div className="hm-cell orange"></div></td>
                <td><div className="hm-cell purple"></div></td>
              </tr>
              <tr>
                <td className="label">Lê Văn C</td>
                <td><div className="hm-cell purple"></div></td>
                <td><div className="hm-cell orange"></div></td>
                <td><div className="hm-cell orange"></div></td>
                <td><div className="hm-cell dashed"></div></td>
                <td><div className="hm-cell blue"></div></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="overview-sidebar">
        <div className="action-req-panel">
          <h3>Kỹ năng chung cần chú ý</h3>
          
          <div className="req-card">
            <div className="req-header">
              <span className="req-name">Past Simple Question Forms</span>
              <span className="req-status">57% chưa đạt</span>
            </div>
            <div className="req-bar-bg"><div className="req-bar-fill" style={{ width: '57%' }}></div></div>
          </div>

          <div className="req-card">
            <div className="req-header">
              <span className="req-name">Some / Any</span>
              <span className="req-status orange">46% cần luyện tập</span>
            </div>
            <div className="req-bar-bg"><div className="req-bar-fill orange" style={{ width: '46%' }}></div></div>
          </div>

          <div className="req-card" style={{ background: 'rgba(203,213,225,0.1)' }}>
            <div className="req-header">
              <span className="req-name">Food and Tableware</span>
              <span className="req-status" style={{ background: '#e2e8f0', color: '#64748b' }}>38% thiếu dữ liệu</span>
            </div>
            <div className="req-bar-bg"><div className="req-bar-fill purple" style={{ width: '38%' }}></div></div>
          </div>
        </div>

        <div className="action-req-panel" style={{ background: '#4d44b5', color: 'white' }}>
          <h3 style={{ color: 'white', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={20} />
            Hành động đề xuất
          </h3>
          <div className="action-btn-group">
            <button className="btn-large-action">
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Users size={20} /> Hỗ trợ cá nhân (4 hs)
              </div>
              <ChevronRight size={18} />
            </button>
            <button className="btn-large-action">
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Users size={20} /> Kèm theo nhóm (2 nhóm)
              </div>
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderXPLeaderboard = () => (
    <div className="xp-container">
      <div className="xp-podium-section">
        <h3 className="xp-podium-title">Top Học Viên Xuất Sắc Nhất Tuần</h3>
        <div className="podium-container">
          <div className="podium-slot">
            <div className="podium-avatar">
              N
            </div>
            <div className="podium-name">Nguyễn Văn A</div>
            <div className="podium-class">Lớp 3A1</div>
            <div className="podium-xp">4,200 XP</div>
            <div className="podium-box second">
              <Award size={32} style={{ color: '#94a3b8' }} />
            </div>
          </div>

          <div className="podium-slot">
            <div className="podium-avatar" style={{ width: '80px', height: '80px', fontSize: '28px', border: '4px solid #fbbf24' }}>
              <div className="crown-icon"><Award size={32} fill="#fbbf24" /></div>
              T
            </div>
            <div className="podium-name" style={{ fontSize: '16px' }}>Trần Thị B</div>
            <div className="podium-class">Lớp 4B2</div>
            <div className="podium-xp" style={{ fontSize: '24px' }}>5,850 XP</div>
            <div className="podium-box first">
              <Award size={40} style={{ color: '#fbbf24' }} />
            </div>
          </div>

          <div className="podium-slot">
            <div className="podium-avatar">
              L
            </div>
            <div className="podium-name">Lê Văn C</div>
            <div className="podium-class">Lớp 3A3</div>
            <div className="podium-xp">3,900 XP</div>
            <div className="podium-box third">
              <Award size={32} style={{ color: '#fdba74' }} />
            </div>
          </div>
        </div>
      </div>

      <div className="xp-grid-bottom">
        <div className="xp-list-panel">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Users size={20} style={{ color: '#fb7d5b' }} />
            Lớp Sôi Nổi Nhất
          </h3>
          {FAKE_XP_LEADERBOARD.map((item, index) => (
            <div key={item.id} className="xp-list-item">
              <div className={`xp-rank ${index === 0 ? 'top' : ''}`}>{index + 1}</div>
              <div className="xp-class-info">
                <div className="xp-class-name">{item.name}</div>
                <div className="xp-teacher-name">{item.teacher}</div>
              </div>
              <div className="xp-score-group">
                <div className="xp-score-val">{item.xp.toLocaleString()} XP</div>
                <div className="xp-score-bar">
                  <div className="xp-score-fill" style={{ width: `${item.pct}%` }}></div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="xp-right-panel">
          <div className="xp-list-panel" style={{ marginBottom: '24px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Flame size={20} style={{ color: '#fb923c' }} />
              Chuỗi Ngày Học Dài Nhất
            </h3>
            <div className="streak-grid">
              <div className="streak-card">
                <div className="streak-days">45 <span style={{ fontSize: '14px', fontWeight: '600' }}>ngày</span></div>
                <div className="streak-name">Hoàng Anh</div>
                <div className="streak-class">Lớp 4B2</div>
              </div>
              <div className="streak-card">
                <div className="streak-days">32 <span style={{ fontSize: '14px', fontWeight: '600' }}>ngày</span></div>
                <div className="streak-name">Minh Tú</div>
                <div className="streak-class">Lớp 3A1</div>
              </div>
              <div className="streak-card">
                <div className="streak-days">28 <span style={{ fontSize: '14px', fontWeight: '600' }}>ngày</span></div>
                <div className="streak-name">Bảo Châu</div>
                <div className="streak-class">Lớp 4A1</div>
              </div>
              <div className="streak-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'transparent', border: '1px dashed var(--border)', cursor: 'pointer' }}>
                <Eye size={24} style={{ color: '#a855f7', marginBottom: '8px' }} />
                <span style={{ fontSize: '14px', color: '#a855f7', fontWeight: '600' }}>Xem tất cả</span>
              </div>
            </div>
          </div>

          <div className="badges-panel">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Star size={20} style={{ color: '#27c26c' }} />
              Huy Hiệu Mới Đạt Được
            </h3>
            <div className="badges-grid">
              <div className="badge-card green">
                <div className="badge-icon-lg green">★</div>
                <div className="badge-info">
                  <h4>Bộ Não Thiên Tài</h4>
                  <p>Đạt điểm tuyệt đối 5 bài kiểm tra.</p>
                  <div className="badge-avatars">
                    <div className="badge-avatar">A</div>
                    <div className="badge-avatar" style={{ background: '#fb7d5b' }}>B</div>
                    <div className="badge-avatar more">+12</div>
                  </div>
                </div>
              </div>
              <div className="badge-card blue">
                <div className="badge-icon-lg blue"><Users size={24} /></div>
                <div className="badge-info">
                  <h4>Đồng Đội Gương Mẫu</h4>
                  <p>Giúp đỡ bạn cùng lớp hoàn thành bài.</p>
                  <div className="badge-avatars">
                    <div className="badge-avatar" style={{ background: '#27c26c' }}>C</div>
                    <div className="badge-avatar" style={{ background: '#fb7d5b' }}>D</div>
                    <div className="badge-avatar more">+8</div>
                  </div>
                </div>
              </div>
              <div className="badge-card orange">
                <div className="badge-icon-lg orange"><Zap size={24} /></div>
                <div className="badge-info">
                  <h4>Tốc Độ Ánh Sáng</h4>
                  <p>Nộp bài tập sớm nhất lớp 3 lần.</p>
                  <div className="badge-avatars">
                    <div className="badge-avatar" style={{ background: '#a855f7' }}>E</div>
                    <div className="badge-avatar more">+5</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="teacher-dashboard animate-fade-in">
      <div className="td-header">
        <h1>
          {currentView === 'attention' && 'Lớp cần chú ý'}
          {currentView === 'ai-recommendations' && 'Phân tích & Đề xuất AI Cá nhân'}
          {currentView === 'class-overview' && 'Tổng quan lớp 4A'}
          {currentView === 'xp-leaderboard' && 'Vinh danh nỗ lực học tập'}
        </h1>
        {/* Render subtabs depending on current view to mimic screenshots */}
        {(currentView === 'ai-recommendations' || currentView === 'class-overview') && (
          <div className="td-subnav">
            <button className={`td-subnav-btn ${currentView === 'class-overview' ? 'active' : ''}`} onClick={() => setCurrentView('class-overview')}>Tổng quan lớp</button>
            <button className="td-subnav-btn">Học sinh</button>
            <button className={`td-subnav-btn ${currentView === 'ai-recommendations' ? 'active' : ''}`} onClick={() => setCurrentView('ai-recommendations')}>Đề xuất AI</button>
            <button className="td-subnav-btn">Bài tập</button>
            <button className="td-subnav-btn">Can thiệp</button>
            <button className="td-subnav-btn">Báo cáo</button>
          </div>
        )}
        {currentView === 'xp-leaderboard' && (
          <div className="td-subnav">
            <button className="td-subnav-btn">Tổng quan</button>
            <button className="td-subnav-btn">Khối và lớp</button>
            <button className="td-subnav-btn">Cảnh báo</button>
            <button className="td-subnav-btn active">Vinh danh XP</button>
            <button className="td-subnav-btn">Nguồn lực</button>
          </div>
        )}
      </div>

      <div style={{ marginBottom: '24px' }}>
        {/* Global Navigation to switch between screenshots easily */}
        <div style={{ display: 'flex', gap: '8px', padding: '12px', background: 'rgba(77, 68, 181, 0.05)', borderRadius: '12px', border: '1px dashed rgba(77, 68, 181, 0.3)' }}>
          <span style={{ fontSize: '13px', fontWeight: '700', color: 'var(--primary)', marginRight: '8px', alignSelf: 'center' }}>Demo Menu:</span>
          <button className={`td-subnav-btn ${currentView === 'attention' ? 'active' : ''}`} onClick={() => setCurrentView('attention')}>1. Lớp cần chú ý</button>
          <button className={`td-subnav-btn ${currentView === 'ai-recommendations' ? 'active' : ''}`} onClick={() => setCurrentView('ai-recommendations')}>2. Đề xuất AI</button>
          <button className={`td-subnav-btn ${currentView === 'class-overview' ? 'active' : ''}`} onClick={() => setCurrentView('class-overview')}>3. Tổng quan lớp 4A</button>
          <button className={`td-subnav-btn ${currentView === 'xp-leaderboard' ? 'active' : ''}`} onClick={() => setCurrentView('xp-leaderboard')}>4. Vinh danh XP</button>
        </div>
      </div>

      <div className="td-content">
        {currentView === 'attention' && renderAttentionView()}
        {currentView === 'ai-recommendations' && renderAIRecommendations()}
        {currentView === 'class-overview' && renderClassOverview()}
        {currentView === 'xp-leaderboard' && renderXPLeaderboard()}
      </div>
    </div>
  );
}
