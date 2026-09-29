import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scan, Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';
import { authApi } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { Token } from '@/types';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const { data } = await authApi.login(form) as { data: Token };
      login(data.access_token, data.refresh_token, data.user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-950 relative overflow-hidden">
      {/* Background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-500/8 rounded-full blur-3xl animate-pulse-slow" style={{animationDelay:'1.5s'}} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md mx-4 relative z-10"
      >
        {/* Glass card */}
        <div className="glass-card p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl shadow-glow mb-4">
              <Scan size={28} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-surface-50">CAPVIA AI</h1>
            <p className="text-surface-400 text-sm mt-1">Paint Defect Detection Platform</p>
          </div>

          <h2 className="text-lg font-semibold text-surface-100 mb-6">Sign in to your account</h2>

          {error && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-4 py-3 mb-5 text-sm">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="label">Email address</label>
              <input
                type="email" required placeholder="you@example.com"
                className="input-field"
                value={form.email}
                onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
              />
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input
                  type={showPwd ? 'text' : 'password'} required placeholder="••••••••"
                  className="input-field pr-10"
                  value={form.password}
                  onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                />
                <button type="button" onClick={() => setShowPwd(p => !p)} className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500 hover:text-surface-300">
                  {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary mt-2 flex items-center justify-center gap-2">
              {loading ? <><Loader2 size={18} className="animate-spin" />Signing in...</> : 'Sign In'}
            </button>

            <button
              type="button"
              onClick={() => setForm({ email: 'demo@capvia.ai', password: 'DemoPass123!' })}
              className="w-full py-2 px-3 rounded-xl border border-primary-600/30 bg-primary-600/10 hover:bg-primary-600/20 text-primary-400 text-xs font-medium transition-all text-center"
            >
              Fill Demo Credentials (demo@capvia.ai)
            </button>
          </form>

          <p className="text-center text-surface-500 text-sm mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>

        <p className="text-center text-surface-600 text-xs mt-4">
          &copy; 2024 CAPVIA AI &mdash; Automated Vehicle Quality Inspection System
        </p>
      </motion.div>
    </div>
  );
}
