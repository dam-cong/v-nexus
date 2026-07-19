import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Award,
  BarChart3,
  BookOpenCheck,
  BrainCircuit,
  Check,
  CheckCircle2,
  ClipboardCheck,
  GraduationCap,
  Heart,
  Lightbulb,
  Menu,
  Play,
  Rocket,
  School,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  UserRound,
  Users,
  WifiOff,
  X,
} from 'lucide-react';
import studentAudienceImage from '../images/HS.png';
import parentAudienceImage from '../images/PH.png';
import teacherAudienceImage from '../images/GV.png';
import schoolAudienceImage from '../images/school 2.png';
import vBeeImage from '../images/V-Bee.png';
import './LandingPage.css';

const problemItems = [
  { icon: Target, text: 'Khó tập trung khi nhìn màn hình' },
  { icon: Users, text: 'Thiếu tương tác của con người' },
  { icon: BookOpenCheck, text: 'Một chương trình cho tất cả' },
];

const learningSteps = [
  { number: '1', icon: ClipboardCheck, title: 'Chẩn đoán\nnăng lực', tone: 'violet' },
  { number: '2', icon: BrainCircuit, title: 'Tạo lộ trình\ncá nhân hóa', tone: 'cyan' },
  { number: '3', icon: UserRound, title: 'Luyện tập\n& đánh giá', tone: 'orange' },
  { number: '4', icon: TrendingUp, title: 'Tiến bộ\nmỗi ngày', tone: 'mint' },
];

const audiences = [
  {
    icon: GraduationCap,
    title: 'Học sinh',
    text: 'Biết mình học gì, giỏi gì',
    tone: 'student',
    visual: <><img className="audience-avatar" src={studentAudienceImage} alt="Học sinh" /><BarChart3 /></>,
  },
  {
    icon: Heart,
    title: 'Phụ huynh',
    text: 'Theo dõi & đồng hành',
    tone: 'parent',
    visual: <><img className="audience-avatar" src={parentAudienceImage} alt="Phụ huynh đồng hành cùng học sinh" /><CheckCircle2 /></>,
  },
  {
    icon: UserRound,
    title: 'Giáo viên',
    text: 'Nắm lớp dễ dàng hơn',
    tone: 'teacher',
    visual: <><img className="audience-avatar" src={teacherAudienceImage} alt="Giáo viên" /><ClipboardCheck /></>,
  },
  {
    icon: School,
    title: 'Nhà trường',
    text: 'Quản lý tổng quan',
    tone: 'school',
    visual: <><img className="audience-avatar" src={schoolAudienceImage} alt="Nhà trường" /><TrendingUp /></>,
  },
];

const differences = [
  { icon: BrainCircuit, title: 'Cá nhân hóa', text: 'lộ trình học' },
  { icon: Award, title: 'Tạo động lực', text: 'học lâu dài' },
  { icon: Users, title: 'Giáo viên duyệt', text: 'mọi đề xuất AI' },
  { icon: ShieldCheck, title: 'Ưu tiên vùng', text: 'nông thôn, vùng xa' },
];

export default function LandingPage({ isAuthenticated, user }) {
  const [menuOpen, setMenuOpen] = React.useState(false);
  const destination = isAuthenticated ? '/app' : '/login';
  const workspaceLabel = user?.role === 'hoc_sinh' ? 'Vào lớp học' : 'Mở trang quản lý';
  const ctaLabel = isAuthenticated ? workspaceLabel : 'Đăng nhập';

  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="school-landing">
      <header className="school-header">
        <nav className="school-nav" aria-label="Điều hướng chính">
          <Link className="school-brand" to="/" aria-label="V-Nexus School - Trang chủ">
            <img src="/logo-mark.png" alt="" />
            <span>V-NEXUS SCHOOL</span>
          </Link>

          <div className={`school-nav-links ${menuOpen ? 'is-open' : ''}`}>
            <a className="active" href="#home" onClick={closeMenu}>Trang chủ</a>
            <a href="#solution" onClick={closeMenu}>Giải pháp</a>
            <a href="#audience" onClick={closeMenu}>Dành cho ai</a>
            <a href="#difference" onClick={closeMenu}>Điểm khác biệt</a>
            <Link className="school-mobile-login" to={destination} onClick={closeMenu}>{ctaLabel}</Link>
          </div>

          <div className="school-nav-actions">
            {isAuthenticated && <span className="school-welcome">Xin chào, {user?.name?.split(' ').at(-1)}</span>}
            <Link className="school-login" to={destination}>{ctaLabel}</Link>
            <button
              className="school-menu-toggle"
              type="button"
              aria-label={menuOpen ? 'Đóng menu' : 'Mở menu'}
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((value) => !value)}
            >
              {menuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </nav>
      </header>

      <main>
        <section className="school-hero" id="home">
          <div className="school-hero-glow" />
          <div className="school-shell school-hero-inner">
            <div className="school-hero-copy">
              <p className="school-eyebrow">AI-powered adaptive learning platform</p>
              <h1>Mỗi học sinh <em>một lộ trình</em> học tập riêng</h1>
              <p className="school-hero-lead">
                Nền tảng học tập thích ứng dùng AI cho các trường <strong>K12 Việt Nam</strong>
              </p>

              <div className="school-feature-pills" aria-label="Điểm nổi bật">
                <span><Sparkles /> Cá nhân hóa lộ trình</span>
                <span><Users /> Đồng hành cùng giáo viên</span>
                <span><WifiOff /> Không lo mất mạng</span>
              </div>

              <div className="school-hero-actions">
                <Link className="school-primary-cta" to={destination}>
                  {isAuthenticated ? workspaceLabel : 'Khám phá ngay'} <ArrowRight />
                </Link>
                <a className="school-video-link" href="#solution">
                  <i><Play /></i> Xem video
                </a>
              </div>
            </div>

            <div className="school-hero-art" aria-label="Học sinh học cùng nền tảng V-Nexus">
              <img src="/landing-hero-v2.png" alt="Học sinh vui vẻ học trên laptop cùng bảng tiến độ AI" />
              <div className="hero-progress-float">
                <small>Tiến bộ tuần này</small>
                <strong>+32%</strong>
                <TrendingUp />
              </div>
              <div className="hero-badge-float">
                <small>Huy hiệu mới</small>
                <div><Award /><Sparkles /><ShieldCheck /></div>
              </div>
              <div className="hero-path-float">
                <strong>Lộ trình của Minh</strong>
                <span><Check /> Chẩn đoán</span>
                <span><Check /> Luyện tập</span>
                <span><Target /> Phát triển kỹ năng</span>
              </div>
            </div>
          </div>
        </section>

        <section className="school-problem" id="about">
          <div className="school-shell school-problem-grid">
            <div className="school-problem-copy">
              <p className="school-section-kicker">Vấn đề</p>
              <h2>Vì sao nhiều học sinh<br />bỏ học giữa chừng?</h2>
              <div className="problem-list">
                {problemItems.map(({ icon: Icon, text }) => (
                  <div className="problem-chip" key={text}><Icon /><span>{text}</span></div>
                ))}
              </div>
              <div className="problem-note">
                <Lightbulb />
                <p>AI mở ra cơ hội để mọi trẻ em – dù ở đâu – đều có lộ trình học phù hợp cho chính mình.</p>
              </div>
            </div>

            <div className="school-ai-scene" aria-hidden="true">
              <div className="ai-orbit orbit-one"><span><BookOpenCheck /></span></div>
              <div className="ai-orbit orbit-two"><span><Award /></span></div>
              <div className="ai-orbit orbit-three"><span><Play /></span></div>
              <div className="ai-core"><BrainCircuit /><strong>AI</strong></div>
              <div className="ai-student">👧🏻</div>
              <div className="ai-spark spark-one">✦</div>
              <div className="ai-spark spark-two">✧</div>
            </div>
          </div>
        </section>

        <section className="school-solution" id="solution">
          <div className="school-shell">
            <div className="school-section-heading">
              <p className="school-section-kicker">Giải pháp</p>
              <h2>Học tập hiệu quả hơn với vòng lặp AI thông minh</h2>
            </div>

            <div className="solution-steps">
              {learningSteps.map(({ number, icon: Icon, title, tone }, index) => (
                <React.Fragment key={number}>
                  <article className={`solution-card ${tone}`}>
                    <span className="solution-number">{number}</span>
                    <div className="solution-illustration"><Icon /></div>
                    <h3>{title.split('\n').map((line) => <React.Fragment key={line}>{line}<br /></React.Fragment>)}</h3>
                  </article>
                  {index < learningSteps.length - 1 && <ArrowRight className="solution-arrow" />}
                </React.Fragment>
              ))}
            </div>

            <div className="solution-benefits">
              <span>🚀 Học nhanh/chậm theo năng lực</span>
              <span>🏆 Coin • XP • Huy hiệu tạo động lực</span>
              <span><WifiOff /> Chạy được khi mất mạng</span>
            </div>
          </div>
        </section>

        <section className="school-audience" id="audience">
          <div className="school-shell">
            <div className="school-section-heading">
              <p className="school-section-kicker">Dành cho ai</p>
              <h2>Giải pháp cho 4 nhóm trong hệ sinh thái giáo dục</h2>
            </div>

            <div className="audience-grid">
              {audiences.map(({ icon: Icon, title, text, tone, visual }) => (
                <article className={`audience-card ${tone}`} key={title}>
                  <div className="audience-card-head">
                    <i><Icon /></i>
                    <div><h3>{title}</h3><p>{text}</p></div>
                  </div>
                  <div className="audience-visual">{visual}</div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="school-difference" id="difference">
          <div className="school-shell difference-inner">
            <div className="difference-heading">
              <p>Điểm khác biệt của V-Nexus</p>
              <h2>AI hỗ trợ – Con người quyết định</h2>
            </div>
            <div className="difference-grid">
              {differences.map(({ icon: Icon, title, text }) => (
                <div className="difference-item" key={title}>
                  <i><Icon /></i>
                  <p><strong>{title}</strong><span>{text}</span></p>
                </div>
              ))}
            </div>
            <div className="difference-mascot" aria-hidden="true"><img src={vBeeImage} alt="" /></div>
          </div>
        </section>

        <section className="school-final-cta">
          <div className="school-shell final-cta-inner">
            <div className="final-cta-copy"><Rocket /><h2>Sẵn sàng để mỗi học sinh<br />tỏa sáng theo cách của riêng mình?</h2></div>
            <Link to={destination}>{isAuthenticated ? workspaceLabel : 'Đăng ký tư vấn'} <ArrowRight /></Link>
          </div>
        </section>
      </main>

      <footer className="school-footer">
        <div className="school-shell school-footer-inner">
          <Link className="school-brand" to="/">
            <img src="/logo-mark.png" alt="" /><span>V-NEXUS SCHOOL</span>
          </Link>
          <p>AI-powered Adaptive Learning Platform</p>
          <span>© 2026 V-NEXUS SCHOOL</span>
        </div>
      </footer>
    </div>
  );
}
