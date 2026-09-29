import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, PlusCircle, History, User,
  ChevronLeft, Scan, Zap
} from 'lucide-react';

const navItems = [
  { to: '/dashboard',      icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/new-inspection', icon: PlusCircle,       label: 'New Inspection' },
  { to: '/history',        icon: History,          label: 'History' },
  { to: '/profile',        icon: User,             label: 'Profile' },
];

interface SidebarProps { open: boolean; onToggle: () => void; }

export default function Sidebar({ open, onToggle }: SidebarProps) {
  return (
    <AnimatePresence initial={false}>
      <motion.aside
        animate={{ width: open ? 240 : 72 }}
        transition={{ duration: 0.25, ease: 'easeInOut' }}
        className="relative flex flex-col bg-surface-900 border-r border-surface-800 overflow-hidden flex-shrink-0"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-surface-800">
          <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-glow">
            <Scan size={18} className="text-white" />
          </div>
          <AnimatePresence>
            {open && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }}>
                <div className="font-bold text-surface-50 whitespace-nowrap leading-tight">CAPVIA AI</div>
                <div className="text-xs text-surface-500 whitespace-nowrap">Paint Defect Platform</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 flex flex-col gap-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'nav-item-active' : 'nav-item'}>
              <Icon size={20} className="flex-shrink-0" />
              <AnimatePresence>
                {open && (
                  <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="whitespace-nowrap text-sm">
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          ))}
        </nav>

        {/* Version / AI Badge */}
        <div className="p-3 border-t border-surface-800">
          <div className={`flex items-center gap-2 bg-primary-950/60 border border-primary-800/40 rounded-xl px-3 py-2 ${!open ? 'justify-center' : ''}`}>
            <Zap size={14} className="text-primary-400 flex-shrink-0" />
            {open && <span className="text-xs text-primary-400 font-medium whitespace-nowrap">RT-DETR v2 AI</span>}
          </div>
        </div>

        {/* Toggle button */}
        <button
          onClick={onToggle}
          className="absolute top-5 -right-3 w-6 h-6 bg-surface-700 border border-surface-600 rounded-full flex items-center justify-center hover:bg-surface-600 transition-colors z-10"
        >
          <motion.div animate={{ rotate: open ? 0 : 180 }} transition={{ duration: 0.25 }}>
            <ChevronLeft size={12} className="text-surface-300" />
          </motion.div>
        </button>
      </motion.aside>
    </AnimatePresence>
  );
}
