import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload, Car, Loader2, AlertCircle, CheckCircle, X, Scan } from 'lucide-react';
import { predictApi } from '@/lib/api';

export default function NewInspection() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [form, setForm] = useState({ vehicle_number: '', vehicle_model: '', owner_name: '', inspector_name: '' });
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) {
      setFile(accepted[0]);
      setPreview(URL.createObjectURL(accepted[0]));
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'image/*': ['.jpg','.jpeg','.png','.webp'] }, maxFiles: 1
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) { setError('Please upload a vehicle image.'); return; }
    setLoading(true);
    setError('');
    setProgress(0);

    // Fake progress animation
    const interval = setInterval(() => setProgress(p => Math.min(p + 5, 90)), 250);

    const fd = new FormData();
    fd.append('image', file);
    fd.append('vehicle_number', form.vehicle_number);
    fd.append('vehicle_model', form.vehicle_model);
    fd.append('owner_name', form.owner_name);
    fd.append('inspector_name', form.inspector_name);

    try {
      const { data } = await predictApi.predict(fd);
      clearInterval(interval);
      setProgress(100);
      setTimeout(() => navigate(`/inspection/${data.id}`), 500);
    } catch (err: any) {
      clearInterval(interval);
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
      setProgress(0);
    } finally {
      if (!loading) setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-slide-up">
      <div className="mb-6">
        <h1 className="section-header">New Inspection</h1>
        <p className="section-sub">Upload a vehicle image to detect paint defects using RT-DETR v2 AI</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        {/* Image Upload Zone */}
        <div className="glass-card p-6">
          <h2 className="font-semibold text-surface-100 mb-4 flex items-center gap-2">
            <Upload size={18} className="text-primary-400" />Vehicle Image
          </h2>

          <AnimatePresence mode="wait">
            {!preview ? (
              <motion.div key="dropzone" initial={{ opacity: 1 }} animate={{ opacity: 1 }}>
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 ${
                    isDragActive ? 'border-primary-500 bg-primary-500/10' : 'border-surface-700 hover:border-surface-600 hover:bg-surface-800/50'
                  }`}
                >
                  <input {...getInputProps()} />
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 bg-primary-600/20 rounded-2xl flex items-center justify-center">
                      <Upload size={28} className="text-primary-400" />
                    </div>
                    <div>
                      <p className="text-surface-200 font-medium">{isDragActive ? 'Drop the image here' : 'Drag & drop your vehicle image'}</p>
                      <p className="text-surface-500 text-sm mt-1">or click to browse — JPG, PNG, WEBP up to 20MB</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div key="preview" initial={{ opacity:0 }} animate={{ opacity:1 }} className="relative rounded-2xl overflow-hidden">
                <img src={preview} alt="Preview" className="w-full max-h-72 object-cover rounded-2xl" />
                <button
                  type="button"
                  onClick={() => { setFile(null); setPreview(null); }}
                  className="absolute top-3 right-3 w-8 h-8 bg-surface-900/80 rounded-full flex items-center justify-center hover:bg-red-500 transition-colors"
                >
                  <X size={16} className="text-white" />
                </button>
                <div className="absolute bottom-3 left-3 bg-surface-900/80 backdrop-blur rounded-lg px-3 py-1 text-xs text-surface-300">
                  {file?.name} ({(file!.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Vehicle Details */}
        <div className="glass-card p-6">
          <h2 className="font-semibold text-surface-100 mb-4 flex items-center gap-2">
            <Car size={18} className="text-primary-400" />Vehicle Details
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Vehicle Number *</label>
              <input type="text" required placeholder="MH 01 AB 1234" className="input-field"
                value={form.vehicle_number} onChange={e => setForm(p=>({...p,vehicle_number:e.target.value}))} />
            </div>
            <div>
              <label className="label">Vehicle Model</label>
              <input type="text" placeholder="Maruti Swift, Honda City..." className="input-field"
                value={form.vehicle_model} onChange={e => setForm(p=>({...p,vehicle_model:e.target.value}))} />
            </div>
            <div>
              <label className="label">Owner Name</label>
              <input type="text" placeholder="Full name" className="input-field"
                value={form.owner_name} onChange={e => setForm(p=>({...p,owner_name:e.target.value}))} />
            </div>
            <div>
              <label className="label">Inspector Name</label>
              <input type="text" placeholder="Inspector full name" className="input-field"
                value={form.inspector_name} onChange={e => setForm(p=>({...p,inspector_name:e.target.value}))} />
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-4 py-3 text-sm">
            <AlertCircle size={16} />{error}
          </div>
        )}

        {/* Progress */}
        {loading && (
          <div className="glass-card p-5">
            <div className="flex items-center gap-3 mb-3">
              <Scan size={18} className="text-primary-400 animate-spin-slow" />
              <span className="text-surface-200 font-medium">Analysing vehicle surface with RT-DETR v2 AI...</span>
              <span className="ml-auto text-primary-400 font-bold">{progress}%</span>
            </div>
            <div className="w-full bg-surface-700 rounded-full h-2 overflow-hidden">
              <motion.div animate={{ width: `${progress}%` }} transition={{ duration: 0.3 }} className="h-2 bg-gradient-to-r from-primary-600 to-accent-500 rounded-full" />
            </div>
            <p className="text-xs text-surface-500 mt-2">Detection → Glare Filter → Measurement → Severity → Cost Estimation</p>
          </div>
        )}

        <button type="submit" disabled={loading} className="btn-primary flex items-center justify-center gap-2 text-lg py-4">
          {loading ? <><Loader2 size={20} className="animate-spin"/>Analysing...</> : <><Scan size={20}/>Analyse Defects</>}
        </button>
      </form>
    </div>
  );
}
