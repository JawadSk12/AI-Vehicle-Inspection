import { Menu, Bell } from 'lucide-react';

interface HeaderProps { onMenuClick: () => void; }

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-4 bg-surface-900/80 backdrop-blur-md border-b border-surface-800 flex-shrink-0">
      <div className="flex items-center gap-4">
        <button onClick={onMenuClick} className="btn-ghost p-2 rounded-lg">
          <Menu size={20} />
        </button>
        <div className="hidden md:flex items-center gap-2 text-sm text-surface-400">
          <span>Automated Vehicle Quality Inspection System</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="btn-ghost p-2 rounded-lg relative">
          <Bell size={18} />
        </button>
        <div className="w-9 h-9 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
          A
        </div>
      </div>
    </header>
  );
}
