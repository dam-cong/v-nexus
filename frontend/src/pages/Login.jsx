import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { LogIn, Mail, Lock, AlertCircle } from 'lucide-react';

export default function Login() {
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #4d44b5 0%, #6c5ce7 50%, #a29bfe 100%)',
      padding: '20px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '420px',
        background: 'white',
        borderRadius: '20px',
        padding: '48px 40px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '14px',
            background: '#fb7d5b',
            color: 'white',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            fontWeight: '900',
            marginBottom: '16px',
            boxShadow: '0 4px 12px rgba(251,125,91,0.3)',
          }}>
            V
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: '800', color: '#303972', margin: 0 }}>
            V-Nexus Tutor
          </h1>
          <p style={{ fontSize: '14px', color: '#a0a3bd', marginTop: '8px' }}>
            Đăng nhập vào hệ thống
          </p>
        </div>

        {/* Error */}
        {error && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: '#ffe8ec',
            color: '#ff5b5b',
            padding: '12px 16px',
            borderRadius: '12px',
            marginBottom: '20px',
            fontSize: '13px',
            fontWeight: '600',
          }}>
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '600', color: '#303972' }}>
              Email
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={18} style={{ position: 'absolute', left: '14px', top: '12px', color: '#a0a3bd' }} />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="email@vnexus.vn"
                required
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 44px',
                  border: '1px solid #c1bbeb',
                  borderRadius: '12px',
                  fontSize: '14px',
                  outline: 'none',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '600', color: '#303972' }}>
              Mật khẩu
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} style={{ position: 'absolute', left: '14px', top: '12px', color: '#a0a3bd' }} />
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 44px',
                  border: '1px solid #c1bbeb',
                  borderRadius: '12px',
                  fontSize: '14px',
                  outline: 'none',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '14px',
              background: '#4d44b5',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '15px',
              fontWeight: '700',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              fontFamily: 'inherit',
              marginTop: '8px',
            }}
          >
            <LogIn size={18} />
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>

        {/* Demo accounts */}
        <div style={{ marginTop: '28px', padding: '16px', background: '#f8f7ff', borderRadius: '12px' }}>
          <p style={{ fontSize: '12px', fontWeight: '700', color: '#a0a3bd', marginBottom: '10px', textTransform: 'uppercase' }}>
            Tài khoản demo (mật khẩu: 123456)
          </p>
          <div style={{ fontSize: '12px', color: '#303972', lineHeight: '1.8' }}>
            <div><b>Admin:</b> admin@vnexus.vn</div>
            <div><b>Giáo viên:</b> teacher1@vnexus.vn</div>
            <div><b>Học sinh:</b> hs01@vnexus.vn</div>
          </div>
        </div>
      </div>
    </div>
  );
}
