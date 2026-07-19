import React, { useState, useEffect } from 'react';
import { X, Save, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { apiFetch } from '../api';

// Gợi ý điền sẵn base URL/model khi đổi chế độ — chỉ là gợi ý, admin có thể sửa lại
// tự do (mọi hãng "fpt"/"gemini"/"openai" đều dùng chung 1 client OpenAI-compatible
// ở backend, không hardcode riêng từng hãng).
const PROVIDER_PRESETS = {
  fpt: { llm_base_url: 'https://mkp-api.fptcloud.com/v1', llm_model: 'DeepSeek-V4-Flash' },
  gemini: {
    llm_base_url: 'https://generativelanguage.googleapis.com/v1beta/openai/',
    llm_model: 'gemini-2.5-flash',
  },
  openai: { llm_base_url: 'https://api.openai.com/v1', llm_model: 'gpt-4o-mini' },
};

export default function SettingsModal({ open, onClose }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);
  const [form, setForm] = useState({
    llm_mode: 'offline',
    llm_api_key: '',
    llm_base_url: '',
    llm_model: '',
  });

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setMsg(null);
    apiFetch('/api/settings/llm')
      .then(r => r.json())
      .then(data => {
        setForm({
          llm_mode: data.llm_mode || 'offline',
          llm_api_key: data.llm_api_key || '',
          llm_base_url: data.llm_base_url || '',
          llm_model: data.llm_model || '',
        });
        setLoading(false);
      })
      .catch(() => {
        setMsg({ type: 'error', text: 'Không thể tải cấu hình' });
        setLoading(false);
      });
  }, [open]);

  const handleChange = (field, value) => {
    if (field === 'llm_mode') {
      // Đổi chế độ luôn tự điền lại Base URL/Model theo gợi ý của chế độ đó — admin
      // sửa tự do sau khi chọn, không có gì bị khóa cứng.
      const preset = PROVIDER_PRESETS[value];
      setForm(prev => ({
        ...prev,
        llm_mode: value,
        llm_base_url: preset ? preset.llm_base_url : prev.llm_base_url,
        llm_model: preset ? preset.llm_model : prev.llm_model,
      }));
    } else {
      setForm(prev => ({ ...prev, [field]: value }));
    }
    setMsg(null);
  };

  const handleSave = async () => {
    setSaving(true);
    setMsg(null);
    try {
      const res = await apiFetch('/api/settings/llm', {
        method: 'PUT',
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Lỗi lưu cấu hình');
      }
      setMsg({ type: 'success', text: 'Đã lưu cấu hình thành công!' });
      setTimeout(() => setMsg(null), 2000);
    } catch (e) {
      setMsg({ type: 'error', text: e.message });
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  return (
    <div className="sm-overlay" onClick={onClose}>
      <div className="sm-modal" onClick={e => e.stopPropagation()}>
        <div className="sm-header">
          <h3>Cấu hình LLM</h3>
          <button className="sm-close" onClick={onClose}><X size={20} /></button>
        </div>

        {loading ? (
          <div className="sm-body"><Loader2 className="sm-spinner" size={32} /></div>
        ) : (
          <div className="sm-body">
            <label className="sm-label">
              Chế độ LLM
              <select
                className="sm-select"
                value={form.llm_mode}
                onChange={e => handleChange('llm_mode', e.target.value)}
              >
                <option value="offline">Offline (không gọi AI)</option>
                <option value="fpt">FPT AI (DeepSeek)</option>
                <option value="gemini">Google Gemini</option>
                <option value="openai">OpenAI (GPT)</option>
                <option value="ollama">Ollama (local)</option>
              </select>
            </label>

            <label className="sm-label">
              API Key
              <input
                className="sm-input"
                type="password"
                placeholder="sk-... hoặc AIza..."
                value={form.llm_api_key}
                onChange={e => handleChange('llm_api_key', e.target.value)}
              />
            </label>

            <label className="sm-label">
              Base URL
              <input
                className="sm-input"
                type="text"
                placeholder="https://generativelanguage.googleapis.com/v1beta/openai/"
                value={form.llm_base_url}
                onChange={e => handleChange('llm_base_url', e.target.value)}
              />
            </label>

            <label className="sm-label">
              Model
              <input
                className="sm-input"
                type="text"
                placeholder="gemini-2.0-flash, DeepSeek-V4-Flash..."
                value={form.llm_model}
                onChange={e => handleChange('llm_model', e.target.value)}
              />
            </label>

            {['fpt', 'gemini', 'openai'].includes(form.llm_mode) && (
              <div className="sm-hint">
                <AlertCircle size={14} />
                <span>
                  Base URL/Model đã điền gợi ý — có thể sửa lại tự do (VD đổi sang model
                  khác, hoặc dùng proxy/endpoint riêng).
                </span>
              </div>
            )}
          </div>
        )}

        <div className="sm-footer">
          {msg && (
            <span className={`sm-msg sm-msg-${msg.type}`}>
              {msg.type === 'success' ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
              {msg.text}
            </span>
          )}
          <div className="sm-actions">
            <button className="sm-btn sm-btn-cancel" onClick={onClose}>Hủy</button>
            <button
              className="sm-btn sm-btn-save"
              onClick={handleSave}
              disabled={saving || loading}
            >
              {saving ? <Loader2 size={14} className="sm-spinner" /> : <Save size={14} />}
              Lưu
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
