import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  BookOpenCheck,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  GraduationCap,
  LineChart,
  Menu,
  ShieldCheck,
  Target,
  Users,
  X,
} from 'lucide-react';
import './LandingPage.css';

const benefits = [
  {
    icon: BrainCircuit,
    title: 'Chẩn đoán đúng khoảng trống',
    text: 'Phân tích từng kỹ năng để tìm ra nguyên nhân thực sự khiến học sinh chưa tiến bộ.',
    tone: 'violet',
  },
  {
    icon: Target,
    title: 'Lộ trình riêng cho từng em',
    text: 'Biến kết quả đánh giá thành các bước học rõ ràng, vừa sức và có thể hoàn thành.',
    tone: 'mint',
  },
  {
    icon: LineChart,
    title: 'Theo dõi bằng dữ liệu',
    text: 'Giáo viên nhìn thấy xu hướng của lớp, còn học sinh hiểu chính xác mình đang tiến bộ ở đâu.',
    tone: 'amber',
  },
];

const steps = [
  ['01', 'Khảo sát đầu vào', 'Một bài đánh giá ngắn giúp xác định nền tảng và thói quen học tập.'],
  ['02', 'Phân tích năng lực', 'V-NEXUS SCHOOL tổng hợp điểm mạnh, lỗ hổng kiến thức và mức độ ưu tiên.'],
  ['03', 'Học theo lộ trình', 'Học sinh nhận kế hoạch cá nhân hóa và kiểm tra nhanh sau từng chặng.'],
];

export default function LandingPage({ isAuthenticated, user }) {
  const [menuOpen, setMenuOpen] = React.useState(false);
  const workspaceLabel = user?.role === 'hoc_sinh' ? 'Vào không gian học' : 'Mở trang quản lý';

  return (
    <div className="landing-page">
      <nav className="landing-nav" aria-label="Điều hướng chính">
        <Link className="landing-brand" to="/" aria-label="V-NEXUS SCHOOL trang chủ">
          <span className="landing-brand-mark"><img src="/logo-mark.png" alt="" /></span>
          <span>V-NEXUS SCHOOL</span>
        </Link>

        <div className={`landing-nav-links ${menuOpen ? 'open' : ''}`}>
          <a href="#why" onClick={() => setMenuOpen(false)}>Giải pháp</a>
          <a href="#how" onClick={() => setMenuOpen(false)}>Cách hoạt động</a>
          <a href="#roles" onClick={() => setMenuOpen(false)}>Dành cho ai</a>
          <Link className="landing-nav-mobile-cta" to={isAuthenticated ? '/app' : '/login'}>
            {isAuthenticated ? workspaceLabel : 'Đăng nhập'}
          </Link>
        </div>

        <div className="landing-nav-actions">
          {isAuthenticated && <span className="landing-welcome">Xin chào, {user?.name?.split(' ').slice(-1)[0]}</span>}
          <Link className="landing-login-link" to={isAuthenticated ? '/app' : '/login'}>
            {isAuthenticated ? workspaceLabel : 'Đăng nhập'} <ArrowRight size={16} />
          </Link>
          <button className="landing-menu-button" onClick={() => setMenuOpen((value) => !value)} aria-label="Mở menu">
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      <main>
        <section className="landing-hero">
          <div className="landing-orb landing-orb-one" />
          <div className="landing-orb landing-orb-two" />
          <div className="landing-hero-copy">
            <div className="landing-kicker"><span /> Nền tảng học tập thích ứng cho thế hệ mới</div>
            <h1>Mỗi học sinh một <em>lộ trình để tỏa sáng.</em></h1>
            <p>
              V-NEXUS SCHOOL giúp nhà trường nhìn thấy khoảng trống năng lực, trao cho giáo viên dữ liệu hữu ích
              và dẫn dắt mỗi học sinh bằng một hành trình học vừa sức, đầy cảm hứng.
            </p>
            <div className="landing-hero-actions">
              <Link className="landing-primary-button" to={isAuthenticated ? '/app' : '/login'}>
                {isAuthenticated ? workspaceLabel : 'Khám phá V-NEXUS SCHOOL'} <ArrowRight size={18} />
              </Link>
              <a className="landing-secondary-button" href="#how">
                Xem cách hoạt động <ChevronRight size={18} />
              </a>
            </div>
            <div className="landing-proof">
              <div className="landing-avatars" aria-hidden="true">
                <span>AN</span><span>MH</span><span>KL</span><span>+8</span>
              </div>
              <div><strong>Học đúng điều mình cần</strong><small>Thay vì học lại mọi thứ từ đầu</small></div>
            </div>
          </div>

          <div className="landing-product-visual" aria-label="Mô phỏng bảng điều khiển V-NEXUS SCHOOL">
            <div className="visual-grid" />
            <div className="visual-dashboard">
              <div className="visual-topbar">
                <div className="visual-mini-brand"><img src="/logo-mark.png" alt="" /> V-NEXUS SCHOOL</div>
                <div className="visual-avatar">LT</div>
              </div>
              <div className="visual-greeting">
                <span>Chào buổi sáng, Linh</span>
                <strong>Sẵn sàng cho một bước tiến mới?</strong>
              </div>
              <div className="visual-content-grid">
                <div className="visual-progress-card">
                  <div className="visual-card-head"><span>Tiến độ tuần này</span><b>72%</b></div>
                  <div className="visual-chart">
                    {[38, 54, 46, 72, 62, 88, 74].map((height, index) => (
                      <i key={index} style={{ '--height': `${height}%` }} className={index === 5 ? 'active' : ''} />
                    ))}
                  </div>
                  <div className="visual-days"><span>T2</span><span>T3</span><span>T4</span><span>T5</span><span>T6</span><span>T7</span><span>CN</span></div>
                </div>
                <div className="visual-level-card">
                  <div className="visual-level-ring"><span>A1</span></div>
                  <strong>Đang tiến bộ</strong>
                  <small>+12% so với tuần trước</small>
                </div>
              </div>
              <div className="visual-next-card">
                <div className="visual-next-icon"><BookOpenCheck size={20} /></div>
                <div><small>Bài học tiếp theo</small><strong>Adverbs of Frequency</strong></div>
                <span>12 phút</span>
                <button aria-label="Bắt đầu"><ArrowRight size={16} /></button>
              </div>
            </div>
            <div className="visual-floating-card visual-floating-top"><CheckCircle2 size={19} /><span><b>Hoàn thành!</b><small>Present Simple</small></span></div>
            <div className="visual-floating-card visual-floating-bottom"><BarChart3 size={19} /><span><b>+18%</b><small>Tiến bộ tháng này</small></span></div>
          </div>
        </section>

        <section className="landing-trust-strip">
          <span>Được thiết kế cho hệ sinh thái giáo dục hiện đại</span>
          <div><b>HỌC SINH</b><b>GIÁO VIÊN</b><b>NHÀ TRƯỜNG</b><b>PHỤ HUYNH</b></div>
        </section>

        <section className="landing-section landing-benefits" id="why">
          <div className="landing-section-heading">
            <span className="landing-section-label">Vì sao chọn V-NEXUS SCHOOL</span>
            <h2>Biến dữ liệu học tập thành<br />những bước tiến có ý nghĩa.</h2>
            <p>Một trải nghiệm thống nhất nhưng được thiết kế riêng cho nhu cầu của từng vai trò.</p>
          </div>
          <div className="landing-benefit-grid">
            {benefits.map(({ icon: Icon, title, text, tone }) => (
              <article className="landing-benefit-card" key={title}>
                <div className={`landing-benefit-icon ${tone}`}><Icon size={24} /></div>
                <h3>{title}</h3>
                <p>{text}</p>
                <a href="#how">Tìm hiểu thêm <ArrowRight size={16} /></a>
              </article>
            ))}
          </div>
        </section>

        <section className="landing-section landing-how" id="how">
          <div className="landing-how-copy">
            <span className="landing-section-label light">Hành trình học thông minh</span>
            <h2>Ba bước đơn giản.<br />Một lộ trình thật sự riêng.</h2>
            <p>Không thêm áp lực cho giáo viên, không làm học sinh choáng ngợp bởi quá nhiều lựa chọn.</p>
            <Link to={isAuthenticated ? '/app' : '/login'}>Bắt đầu hành trình <ArrowRight size={17} /></Link>
          </div>
          <div className="landing-steps">
            {steps.map(([number, title, text], index) => (
              <article className="landing-step" key={number}>
                <span>{number}</span>
                <div><h3>{title}</h3><p>{text}</p></div>
                {index < steps.length - 1 && <i />}
              </article>
            ))}
          </div>
        </section>

        <section className="landing-section landing-roles" id="roles">
          <div className="landing-section-heading centered">
            <span className="landing-section-label">Một nền tảng, nhiều góc nhìn</span>
            <h2>Đúng công cụ cho đúng người.</h2>
          </div>
          <div className="landing-role-grid">
            <article className="landing-role-card student">
              <div className="landing-role-icon"><GraduationCap size={28} /></div>
              <span>Cho học sinh</span>
              <h3>Học có mục tiêu, tiến bộ có thể nhìn thấy.</h3>
              <ul><li><CheckCircle2 /> Lộ trình cá nhân dễ hiểu</li><li><CheckCircle2 /> Bài đánh giá thân thiện</li><li><CheckCircle2 /> Ghi nhận từng cột mốc</li></ul>
            </article>
            <article className="landing-role-card teacher">
              <div className="landing-role-icon"><Users size={28} /></div>
              <span>Cho giáo viên & quản trị</span>
              <h3>Quản lý nhẹ nhàng, can thiệp đúng lúc.</h3>
              <ul><li><ShieldCheck /> Tổng quan toàn lớp</li><li><ClipboardCheck /> Quản lý bài đánh giá</li><li><BarChart3 /> Báo cáo năng lực trực quan</li></ul>
            </article>
          </div>
        </section>

        <section className="landing-cta">
          <div><span>V-NEXUS SCHOOL</span><h2>Sẵn sàng để mỗi học sinh<br />được học theo cách của riêng mình?</h2></div>
          <Link to={isAuthenticated ? '/app' : '/login'}>{isAuthenticated ? workspaceLabel : 'Đăng nhập để bắt đầu'} <ArrowRight size={18} /></Link>
        </section>
      </main>

      <footer className="landing-footer">
        <Link className="landing-brand" to="/"><span className="landing-brand-mark"><img src="/logo-mark.png" alt="" /></span><span>V-NEXUS SCHOOL</span></Link>
        <p>Adaptive learning, meaningful progress.</p>
        <span>© 2026 V-NEXUS SCHOOL</span>
      </footer>
    </div>
  );
}
