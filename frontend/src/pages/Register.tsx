import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scan, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { authApi } from '@/lib/api';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await authApi.register(form);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-950 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-accent-500/8 rounded-full blur-3xl animate-pulse-slow" />
      </div>
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} className="w-full max-w-md mx-4 relative z-10">
        <div className="glass-card p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl shadow-glow mb-4">
              <Scan size={28} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-surface-50">Create Account</h1>
            <p className="text-surface-400 text-sm mt-1">Join CAPVIA AI Platform</p>
          </div>
          {error && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-4 py-3 mb-5 text-sm">
              <AlertCircle size={16} />{error}
            </div>
          )}
          {success && (
            <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 text-green-400 rounded-xl px-4 py-3 mb-5 text-sm">
              <CheckCircle size={16} />Account created! Redirecting to login...
            </div>
          )}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="label">Full Name</label>
              <input type="text" required placeholder="John Doe" className="input-field" value={form.name} onChange={e => setForm(p=>({...p,name:e.target.value}))} />
            </div>
            <div>
              <label className="label">Email address</label>
              <input type="email" required placeholder="you@example.com" className="input-field" value={form.email} onChange={e => setForm(p=>({...p,email:e.target.value}))} />
            </div>
            <div>
              <label className="label">Password</label>
              <input type="password" required minLength={8} placeholder="Min 8 characters" className="input-field" value={form.password} onChange={e => setForm(p=>({...p,password:e.target.value}))} />
            </div>
            <button type="submit" disabled={loading||success} className="btn-primary mt-2 flex items-center justify-center gap-2">
              {loading ? <><Loader2 size={18} className="animate-spin"/>Creating...</> : 'Create Account'}
            </button>
          </form>
          <p className="text-center text-surface-500 text-sm mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">Sign in</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
