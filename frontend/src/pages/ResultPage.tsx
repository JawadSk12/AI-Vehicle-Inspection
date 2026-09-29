import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Download, FileText, Eye, EyeOff, AlertTriangle, CheckCircle, ArrowLeft, Loader2, Layers } from 'lucide-react';
import { inspectionsApi, reportsApi } from '@/lib/api';
import { Inspection } from '@/types';
import { formatINR, formatDate, severityBadgeClass, severityColor, getStorageUrl, downloadBlob } from '@/lib/utils';

function SeverityGauge({ score }: { score: number }) {
  const color = score < 20 ? '#22c55e' : score < 40 ? '#84cc16' : score < 60 ? '#f59e0b' : score < 80 ? '#f97316' : '#ef4444';
  const pct = Math.min(score, 100);
  return (
    <div className="relative flex flex-col items-center">
      <svg width={160} height={100} viewBox="0 0 160 100">
        <path d="M 20 90 A 70 70 0 0 1 140 90" fill="none" stroke="#334155" strokeWidth={14} strokeLinecap="round" />
        <motion.path
          d="M 20 90 A 70 70 0 0 1 140 90"
          fill="none" stroke={color} strokeWidth={14} strokeLinecap="round"
          strokeDasharray="220" strokeDashoffset={220 - (220 * pct / 100)}
          initial={{ strokeDashoffset: 220 }} animate={{ strokeDashoffset: 220 - (220 * pct / 100) }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
        <text x="80" y="88" textAnchor="middle" fill={color} fontSize={28} fontWeight="bold" fontFamily="Inter">{score.toFixed(0)}</text>
        <text x="80" y="98" textAnchor="middle" fill="#64748b" fontSize={9} fontFamily="Inter">/100</text>
      </svg>
    </div>
  );
}

export default function ResultPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [showAnnotated, setShowAnnotated] = useState(true);

  const { data: insp, isLoading } = useQuery<Inspection>({
    queryKey: ['inspection', id],
    queryFn: () => inspectionsApi.get(id!).then(r => r.data),
  });

  const generatePdf = useMutation({
    mutationFn: () => reportsApi.generate(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['inspection', id] }),
  });

  const downloadPdf = useMutation({
    mutationFn: async () => {
      const { data } = await reportsApi.download(id!);
      downloadBlob(data, `CAPVIA_Inspection_${id}.pdf`);
    },
  });

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!insp) return <div className="text-center text-surface-400 mt-20">Inspection not found.</div>;

  const imageSrc = showAnnotated && insp.result_path
    ? getStorageUrl(insp.result_path)
    : getStorageUrl(insp.image_path);

  return (
    <div className="max-w-7xl mx-auto animate-slide-up">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate(-1)} className="btn-ghost flex items-center gap-2">
          <ArrowLeft size={16} />Back
        </button>
        <div className="flex-1">
          <h1 className="section-header">Inspection Result</h1>
          <p className="section-sub">{insp.vehicle_number} &bull; {formatDate(insp.created_at)}</p>
        </div>
        <div className="flex gap-2">
          {!insp.has_report ? (
            <button onClick={() => generatePdf.mutate()} disabled={generatePdf.isPending} className="btn-secondary flex items-center gap-2 text-sm">
              {generatePdf.isPending ? <Loader2 size={16} className="animate-spin"/> : <FileText size={16}/>}Generate PDF
            </button>
          ) : (
            <button onClick={() => downloadPdf.mutate()} disabled={downloadPdf.isPending} className="btn-primary flex items-center gap-2 text-sm">
              {downloadPdf.isPending ? <Loader2 size={16} className="animate-spin"/> : <Download size={16}/>}Download PDF
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT: Image panel */}
        <div className="glass-card p-4 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-surface-300">
              {showAnnotated ? 'AI Annotated Image' : 'Original Image'}
            </span>
            {insp.result_path && (
              <button onClick={() => setShowAnnotated(p=>!p)} className="btn-ghost flex items-center gap-1 text-xs">
                {showAnnotated ? <><EyeOff size={14}/>Show Original</> : <><Eye size={14}/>Show Annotated</>}
              </button>
            )}
          </div>
          <div className="relative rounded-xl overflow-hidden bg-surface-900">
            <img src={imageSrc} alt="inspection" className="w-full object-contain max-h-96 rounded-xl" onError={e => { (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjI0MCIgdmlld0JveD0iMCAwIDMyMCAyNDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjMyMCIgaGVpZ2h0PSIyNDAiIGZpbGw9IiMxZTI5M2IiLz48dGV4dCB4PSIxNjAiIHk9IjEyOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzY0NzQ4YiIgZm9udC1zaXplPSIxNCIgZm9udC1mYW1pbHk9InN5c3RlbS11aSI+SW1hZ2Ugbm90IGF2YWlsYWJsZTwvdGV4dD48L3N2Zz4='; }} />
            {!showAnnotated && <div className="absolute top-3 left-3 bg-surface-900/80 text-xs text-surface-300 px-2 py-1 rounded">Original</div>}
          </div>

          {/* Defect count badge */}
          <div className="flex gap-2 flex-wrap mt-2">
            <div className="bg-surface-800 rounded-xl px-4 py-2 text-center flex-1">
              <div className="text-2xl font-bold text-surface-50">{insp.defect_count ?? 0}</div>
              <div className="text-xs text-surface-400 mt-0.5">Defects Found</div>
            </div>
            <div className="bg-surface-800 rounded-xl px-4 py-2 text-center flex-1">
              <div className="text-2xl font-bold text-surface-50">{insp.confidence ? (insp.confidence * 100).toFixed(0) : 0}%</div>
              <div className="text-xs text-surface-400 mt-0.5">Confidence</div>
            </div>
            <div className="bg-surface-800 rounded-xl px-4 py-2 text-center flex-1">
              <div className="text-2xl font-bold text-surface-50">{insp.total_area_mm2?.toFixed(1) ?? 0}</div>
              <div className="text-xs text-surface-400 mt-0.5">Total Area mm²</div>
            </div>
          </div>
        </div>

        {/* RIGHT: Results panel */}
        <div className="flex flex-col gap-4">
          {/* Severity */}
          <div className="glass-card p-5">
            <div className="flex items-center gap-4">
              <SeverityGauge score={insp.severity_score ?? 0} />
              <div>
                <div className="text-sm text-surface-400 mb-1">Severity Level</div>
                <span className={`${severityBadgeClass(insp.severity_label)} text-base px-3 py-1.5`}>
                  {insp.severity_label ?? 'N/A'}
                </span>
                <div className="text-xs text-surface-500 mt-2">Score: {insp.severity_score?.toFixed(1) ?? 0}/100</div>
              </div>
            </div>
          </div>

          {/* Cost */}
          <div className="glass-card p-5 border border-primary-800/40">
            <div className="text-sm text-surface-400 mb-1">Estimated Repair Cost</div>
            <div className="text-4xl font-bold text-primary-400">{insp.repair_cost_estimated ? formatINR(insp.repair_cost_estimated) : '—'}</div>
            <div className="text-xs text-surface-500 mt-1">
              Range: {insp.repair_cost_min ? formatINR(insp.repair_cost_min) : '—'} – {insp.repair_cost_max ? formatINR(insp.repair_cost_max) : '—'}
            </div>
            <div className="flex gap-4 mt-3">
              <div><div className="text-xs text-surface-500">Time Required</div><div className="text-sm text-surface-200 font-medium">{insp.time_required ?? '—'}</div></div>
              <div><div className="text-xs text-surface-500">Priority</div><div className="text-sm text-surface-200 font-medium">{insp.priority ?? '—'}</div></div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="glass-card p-5">
            <div className="flex items-center gap-2 mb-2">
              {(insp.severity_score ?? 0) >= 60 ? <AlertTriangle size={16} className="text-red-400"/> : <CheckCircle size={16} className="text-green-400"/>}
              <span className="text-sm font-semibold text-surface-200">Recommendation</span>
            </div>
            <p className="text-surface-400 text-sm leading-relaxed">{insp.recommendation ?? 'No recommendation available.'}</p>
          </div>

          {/* Defect table */}
          {insp.defects && insp.defects.length > 0 && (
            <div className="glass-card p-5">
              <h3 className="font-semibold text-surface-100 mb-3 flex items-center gap-2">
                <Layers size={16} className="text-accent-400"/>AI Findings
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-surface-700">
                      {['#','Type','Conf','Area mm²','L×W mm'].map(h => <th key={h} className="text-left py-2 px-2 text-surface-500">{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {insp.defects.map((d: any, i) => (
                      <tr key={i} className={`border-b border-surface-800 ${d.is_glare ? 'opacity-50' : ''}`}>
                        <td className="py-2 px-2 text-surface-400">{i+1}</td>
                        <td className="py-2 px-2 font-medium text-surface-200 capitalize">{(d.class_name||'').replace('_',' ')}</td>
                        <td className="py-2 px-2 text-surface-400">{((d.confidence||0)*100).toFixed(0)}%</td>
                        <td className="py-2 px-2 text-surface-400">{(d.area_mm2||0).toFixed(2)}</td>
                        <td className="py-2 px-2 text-surface-400">{(d.length_mm||0).toFixed(1)}×{(d.width_mm||0).toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
