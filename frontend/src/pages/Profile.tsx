import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, Mail, Shield, Calendar, LogOut, Scan } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { formatDate } from '@/lib/utils';

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="max-w-2xl mx-auto animate-slide-up">
      <div className="mb-6">
        <h1 className="section-header">Profile</h1>
        <p className="section-sub">Your account details and settings</p>
      </div>

      <div className="glass-card p-8">
        {/* Avatar */}
        <div className="flex items-center gap-5 mb-8 pb-8 border-b border-surface-700">
          <div className="w-20 h-20 bg-primary-600 rounded-2xl flex items-center justify-center text-3xl font-bold text-white shadow-glow">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-surface-50">{user?.name}</h2>
            <p className="text-surface-400">{user?.email}</p>
            <span className="inline-block mt-2 bg-primary-600/20 text-primary-400 border border-primary-600/30 text-xs font-semibold px-3 py-1 rounded-full">
              {user?.role?.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Details */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {[
            { icon: User,    label: 'Full Name',  value: user?.name },
            { icon: Mail,    label: 'Email',       value: user?.email },
            { icon: Shield,  label: 'Role',        value: user?.role },
            { icon: Calendar,label: 'Member Since',value: user?.created_at ? formatDate(user.created_at) : '—' },
          ].map(({icon:Icon,label,value}) => (
            <motion.div key={label} initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} className="bg-surface-800/60 rounded-xl p-4 flex items-center gap-3">
              <div className="w-10 h-10 bg-surface-700 rounded-xl flex items-center justify-center flex-shrink-0">
                <Icon size={18} className="text-primary-400" />
              </div>
              <div>
                <div className="text-xs text-surface-500 mb-0.5">{label}</div>
                <div className="text-surface-100 font-medium text-sm">{value || '—'}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Platform info */}
        <div className="bg-surface-800/40 rounded-xl p-4 mb-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <Scan size={18} className="text-primary-400" />
          </div>
          <div>
            <div className="text-sm font-semibold text-surface-200">CAPVIA AI Platform</div>
            <div className="text-xs text-surface-500">RT-DETR v2 Large &bull; Automated Vehicle Quality Inspection System &bull; v1.0.0</div>
          </div>
        </div>

        <button onClick={handleLogout} className="w-full flex items-center justify-center gap-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-600/30 font-semibold px-6 py-3 rounded-xl transition-colors">
          <LogOut size={18} />Sign Out
        </button>
      </div>
    </div>
  );
}
