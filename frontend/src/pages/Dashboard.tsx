import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { AlertTriangle, BarChart3, Car, TrendingUp, Activity } from 'lucide-react';
import { dashboardApi } from '@/lib/api';
import { formatINR, formatDate, severityBadgeClass, severityColor } from '@/lib/utils';
import { DashboardData } from '@/types';

const PIE_COLORS = ['#22c55e','#84cc16','#f59e0b','#f97316','#ef4444'];

function StatCard({ icon: Icon, label, value, sub, color = 'primary' }: any) {
  return (
    <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} className="stat-card">
      <div className="flex items-center justify-between mb-3">
        <span className="text-surface-400 text-sm font-medium">{label}</span>
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center bg-${color}-600/20`}>
          <Icon size={18} className={`text-${color}-400`} />
        </div>
      </div>
      <div className="text-3xl font-bold text-surface-50">{value}</div>
      {sub && <div className="text-xs text-surface-500 mt-1">{sub}</div>}
    </motion.div>
  );
}

export default function Dashboard() {
  const { data, isLoading, isError } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.get().then(r => r.data),
  });

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (isError || !data) return (
    <div className="flex flex-col gap-6 animate-slide-up">
      <div>
        <h1 className="section-header">Dashboard</h1>
        <p className="section-sub">Vehicle inspection analytics &amp; overview</p>
      </div>
      <div className="glass-card p-12 text-center">
        <BarChart3 size={48} className="mx-auto text-surface-600 mb-4" />
        <p className="text-surface-400 text-lg font-medium">No data available</p>
        <p className="text-surface-500 text-sm mt-1">Make sure the backend server is running, then start a new inspection.</p>
      </div>
    </div>
  );

  const d = data;

  return (
    <div className="flex flex-col gap-6 animate-slide-up">
      {/* Header */}
      <div>
        <h1 className="section-header">Dashboard</h1>
        <p className="section-sub">Vehicle inspection analytics &amp; overview</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard icon={Car}         label="Total Inspections" value={d.total_inspections}           sub="All time"                    color="primary" />
        <StatCard icon={AlertTriangle} label="Critical Defects" value={d.critical_defects}            sub="Requiring immediate attention" color="red" />
        <StatCard icon={Activity}    label="Avg Severity Score" value={`${d.avg_severity.toFixed(1)}/100`} sub="Across all inspections"   color="yellow" />
        <StatCard icon={TrendingUp}  label="Avg Repair Cost"   value={formatINR(d.avg_repair_cost)}  sub="Estimated INR"               color="accent" />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass-card p-6">
          <h2 className="font-semibold text-surface-100 mb-4 flex items-center gap-2">
            <BarChart3 size={18} className="text-primary-400" />Monthly Inspections
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={d.monthly_inspections}>
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} labelStyle={{ color: '#e2e8f0' }} />
              <Area type="monotone" dataKey="count" stroke="#2563eb" fill="url(#colorCount)" strokeWidth={2} dot={{ fill: '#2563eb', r: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card p-6">
          <h2 className="font-semibold text-surface-100 mb-4 flex items-center gap-2">
            <Activity size={18} className="text-accent-400" />Severity Distribution
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={d.severity_distribution} cx="50%" cy="50%" innerRadius={55} outerRadius={90} dataKey="count" nameKey="label" paddingAngle={3}>
                {d.severity_distribution.map((entry, i) => (
                  <Cell key={i} fill={severityColor(entry.label)} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
              <Legend formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{value}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="glass-card p-6">
        <h2 className="font-semibold text-surface-100 mb-4">Average Repair Cost by Month (INR)</h2>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={d.monthly_inspections}>
            <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} formatter={(v: any) => [formatINR(Number(v)), 'Avg Cost']} />
            <Bar dataKey="avg_cost" fill="#2563eb" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Inspections */}
      <div className="glass-card p-6">
        <h2 className="font-semibold text-surface-100 mb-4">Recent Inspections</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-700">
                {['Vehicle No.','Owner','Model','Severity','Cost (INR)','Date'].map(h => (
                  <th key={h} className="text-left py-3 px-3 text-surface-400 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {d.recent_inspections.length === 0 && (
                <tr><td colSpan={6} className="text-center py-8 text-surface-500">No inspections yet. Start with a new inspection.</td></tr>
              )}
              {d.recent_inspections.map((insp: any) => (
                <tr key={insp.id} className="border-b border-surface-800 hover:bg-surface-800/50 transition-colors">
                  <td className="py-3 px-3 font-medium text-surface-100">{insp.vehicle_number}</td>
                  <td className="py-3 px-3 text-surface-400">{insp.owner_name || '—'}</td>
                  <td className="py-3 px-3 text-surface-400">{insp.vehicle_model || '—'}</td>
                  <td className="py-3 px-3"><span className={severityBadgeClass(insp.severity_label)}>{insp.severity_label || '—'}</span></td>
                  <td className="py-3 px-3 text-surface-100">{insp.repair_cost_estimated ? formatINR(insp.repair_cost_estimated) : '—'}</td>
                  <td className="py-3 px-3 text-surface-500">{formatDate(insp.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
