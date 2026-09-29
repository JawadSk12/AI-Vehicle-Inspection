import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Filter, Trash2, FileText, Eye, Download } from 'lucide-react';
import { inspectionsApi, reportsApi } from '@/lib/api';
import { InspectionList } from '@/types';
import { formatINR, formatDate, severityBadgeClass, downloadBlob } from '@/lib/utils';

const SEVERITIES = ['', 'Minor','Low','Moderate','High','Critical'];

export default function History() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [page, setPage]     = useState(1);
  const [search, setSearch] = useState('');
  const [severity, setSev]  = useState('');
  const [toDelete, setToDelete] = useState<string|null>(null);

  const { data, isLoading } = useQuery<InspectionList>({
    queryKey: ['inspections', page, search, severity],
    queryFn: () => inspectionsApi.list({ page, limit: 15, search: search||undefined, severity: severity||undefined }).then(r => r.data),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => inspectionsApi.delete(id),
    onSuccess: () => { qc.invalidateQueries({queryKey:['inspections']}); setToDelete(null); },
  });

  const downloadCsv = async (id: string, vn: string) => {
    const { data: blob } = await inspectionsApi.exportCsv(id);
    downloadBlob(blob, `capvia_${vn}.csv`);
  };

  const genPdf = useMutation({
    mutationFn: (id: string) => reportsApi.generate(id),
    onSuccess: () => qc.invalidateQueries({queryKey:['inspections']}),
  });

  return (
    <div className="flex flex-col gap-5 animate-slide-up">
      <div>
        <h1 className="section-header">Inspection History</h1>
        <p className="section-sub">Browse, search, and manage all previous inspections</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-60">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-500" />
          <input className="input-field pl-9" placeholder="Search vehicle number, owner..." value={search} onChange={e=>{setSearch(e.target.value);setPage(1);}} />
        </div>
        <select className="input-field w-44" value={severity} onChange={e=>{setSev(e.target.value);setPage(1);}}>
          {SEVERITIES.map(s => <option key={s} value={s}>{s || 'All Severities'}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-800/80">
              <tr>
                {['Vehicle No.','Owner','Model','Severity','Cost','Defects','Date','Actions'].map(h=>(
                  <th key={h} className="text-left py-3 px-4 text-surface-400 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={8} className="text-center py-12 text-surface-500">
                  <div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"/>Loading...
                </td></tr>
              )}
              {!isLoading && data?.items.length === 0 && (
                <tr><td colSpan={8} className="text-center py-12 text-surface-500">No inspections found.</td></tr>
              )}
              {data?.items.map(insp => (
                <motion.tr key={insp.id} initial={{opacity:0}} animate={{opacity:1}} className="border-b border-surface-800 hover:bg-surface-800/40 transition-colors">
                  <td className="py-3 px-4 font-semibold text-surface-100">{insp.vehicle_number}</td>
                  <td className="py-3 px-4 text-surface-400">{insp.owner_name||'—'}</td>
                  <td className="py-3 px-4 text-surface-400">{insp.vehicle_model||'—'}</td>
                  <td className="py-3 px-4"><span className={severityBadgeClass(insp.severity_label)}>{insp.severity_label||'—'}</span></td>
                  <td className="py-3 px-4 text-surface-200">{insp.repair_cost_estimated ? formatINR(insp.repair_cost_estimated) : '—'}</td>
                  <td className="py-3 px-4 text-center text-surface-400">{insp.defect_count??'—'}</td>
                  <td className="py-3 px-4 text-surface-500 whitespace-nowrap">{formatDate(insp.created_at)}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1">
                      <button onClick={()=>navigate(`/inspection/${insp.id}`)} className="btn-ghost p-1.5 rounded-lg" title="View"><Eye size={15}/></button>
                      {!insp.has_report
                        ? <button onClick={()=>genPdf.mutate(insp.id)} className="btn-ghost p-1.5 rounded-lg" title="Generate PDF"><FileText size={15}/></button>
                        : <button onClick={()=>downloadBlob(new Blob(),'placeholder.pdf')} className="btn-ghost p-1.5 rounded-lg" title="Download PDF"><Download size={15}/></button>
                      }
                      <button onClick={()=>downloadCsv(insp.id, insp.vehicle_number)} className="btn-ghost p-1.5 rounded-lg" title="Export CSV"><Download size={15} className="text-accent-400"/></button>
                      <button onClick={()=>setToDelete(insp.id)} className="btn-ghost p-1.5 rounded-lg text-red-400 hover:text-red-300" title="Delete"><Trash2 size={15}/></button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.total > 15 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-surface-800">
            <span className="text-xs text-surface-500">Showing {(page-1)*15+1}–{Math.min(page*15,data.total)} of {data.total}</span>
            <div className="flex gap-2">
              <button disabled={page===1} onClick={()=>setPage(p=>p-1)} className="btn-ghost text-xs py-1 px-3 disabled:opacity-40">Previous</button>
              <button disabled={page*15>=data.total} onClick={()=>setPage(p=>p+1)} className="btn-ghost text-xs py-1 px-3 disabled:opacity-40">Next</button>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirm Modal */}
      {toDelete && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div initial={{scale:0.9,opacity:0}} animate={{scale:1,opacity:1}} className="glass-card p-6 max-w-sm mx-4">
            <h3 className="font-bold text-surface-50 mb-2">Delete Inspection?</h3>
            <p className="text-surface-400 text-sm mb-5">This will permanently delete the inspection and all associated files. This action cannot be undone.</p>
            <div className="flex gap-3">
              <button onClick={()=>setToDelete(null)} className="btn-secondary flex-1">Cancel</button>
              <button onClick={()=>deleteMut.mutate(toDelete!)} disabled={deleteMut.isPending} className="flex-1 bg-red-600 hover:bg-red-500 text-white font-semibold px-4 py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2">
                {deleteMut.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
