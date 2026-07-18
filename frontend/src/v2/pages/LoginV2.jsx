import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Eye,
  EyeOff,
  GraduationCap,
  Lock,
  Mail,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './LoginV2.css';

const demoAccounts = [
  { label: 'Quản trị viên', email: 'admin@vnexus.vn', icon: ShieldCheck },
  { label: 'Giáo viên', email: 'teacher1@vnexus.vn', icon: BarChart3 },
  { label: 'Học sinh', email: 'hs01@vnexus.vn', icon: GraduationCap },
];

export default function Login() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      await login(email, password);
      navigate('/app', { replace: true });
    } catch (err) {
      setError(err.message);
    }
  };

  const fillDemoAccount = (accountEmail) => {
    setEmail(accountEmail);
    setPassword('123456');
    setError('');
  };

  return (
    <div className="login-page">
      <section className="login-story-panel">
        <Link className="login-back-home" to="/"><ArrowLeft size={16} /> Trở về trang chủ</Link>
        <div className="login-story-content">
          <div className="login-story-brand"><span><Sparkles size={20} /></span> V-Nexus</div>
          <span className="login-story-kicker">ADAPTIVE LEARNING PLATFORM</span>
          <h1>Hiểu đúng năng lực.<br /><em>Học đúng điều cần thiết.</em></h1>
          <p>Một không gian chung để giáo viên dẫn dắt bằng dữ liệu và học sinh tiến bộ theo cách của riêng mình.</p>
          <div className="login-story-points">
            <div><CheckCircle2 /><span><strong>Lộ trình cá nhân hóa</strong><small>Đi từ lỗ hổng thực sự của từng học sinh</small></span></div>
            <div><CheckCircle2 /><span><strong>Tiến bộ nhìn thấy được</strong><small>Rõ ràng với học sinh, hữu ích với giáo viên</small></span></div>
          </div>
        </div>
        <div className="login-story-visual" aria-hidden="true">
          <div className="login-visual-card card-main"><span>Tiến độ học tập</span><strong>+24%</strong><div><i /><i /><i /><i /><i /></div></div>
          <div className="login-visual-card card-float"><Sparkles /><span><b>Lộ trình mới</b><small>Đã sẵn sàng cho em</small></span></div>
        </div>
        <div className="login-story-glow" />
      </section>

      <main className="login-form-panel">
        <div className="login-mobile-brand"><span><Sparkles size={18} /></span> V-Nexus</div>
        <div className="login-form-wrap">
          <div className="login-heading">
            <span>CHÀO MỪNG TRỞ LẠI</span>
            <h2>Đăng nhập vào V-Nexus</h2>
            <p>Tiếp tục hành trình học tập và quản lý của bạn.</p>
          </div>

          {error && <div className="login-error"><AlertCircle size={17} /><span>{error}</span></div>}

          <form onSubmit={handleSubmit} className="login-form">
            <label>
              <span>Địa chỉ email</span>
              <div className="login-input-wrap">
                <Mail size={18} />
                <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="tenban@vnexus.vn" autoComplete="email" required />
              </div>
            </label>
            <label>
              <span>Mật khẩu</span>
              <div className="login-input-wrap">
                <Lock size={18} />
                <input type={showPassword ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Nhập mật khẩu" autoComplete="current-password" required />
                <button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button>
              </div>
            </label>
            <div className="login-form-options"><label><input type="checkbox" /> <span>Ghi nhớ đăng nhập</span></label><button type="button">Quên mật khẩu?</button></div>
            <button className="login-submit" type="submit" disabled={loading}>
              {loading ? <><span className="login-spinner" /> Đang đăng nhập...</> : <>Đăng nhập <ArrowRight size={18} /></>}
            </button>
          </form>

          <div className="login-demo-section">
            <div className="login-divider"><span>Hoặc dùng tài khoản trải nghiệm</span></div>
            <div className="login-demo-grid">
              {demoAccounts.map(({ label, email: accountEmail, icon: Icon }) => (
                <button key={accountEmail} type="button" onClick={() => fillDemoAccount(accountEmail)} className={email === accountEmail ? 'active' : ''}>
                  <Icon size={17} /><span><b>{label}</b><small>{accountEmail}</small></span>
                </button>
              ))}
            </div>
            <p className="login-demo-note">Mật khẩu chung cho tài khoản trải nghiệm: <strong>123456</strong></p>
          </div>
        </div>
        <p className="login-form-footer">Bằng việc đăng nhập, bạn đồng ý với điều khoản sử dụng của V-Nexus.</p>
      </main>
    </div>
  );
}
