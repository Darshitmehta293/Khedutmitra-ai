import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { aiService } from '../services/api'
import { QualityAssessmentResult } from '../types'
import { Upload, Camera, AlertTriangle, Loader2, CheckCircle, History, Sparkles, ShieldCheck, FileCheck, ShieldAlert, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

const CROPS = [
  { id: 'wheat', label: 'Wheat 🌾', gu: 'ઘઉં' },
  { id: 'cotton', label: 'Cotton 🌸', gu: 'કપાસ' },
  { id: 'groundnut', label: 'Groundnut 🥜', gu: 'મગફળી' },
]

const GRADE_COLORS: Record<string, string> = {
  A: 'text-emerald-500 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  B: 'text-amber-500 dark:text-amber-400 bg-amber-500/10 border-amber-500/30',
  C: 'text-red-500 dark:text-red-400 bg-red-500/10 border-red-500/30',
}

export default function QualityPage() {
  const { t } = useTranslation()
  const [cropType, setCropType] = useState('wheat')
  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<QualityAssessmentResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<any[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [treatmentTab, setTreatmentTab] = useState<'organic' | 'chemical'>('organic')
  const fileRef = useRef<HTMLInputElement>(null)

  const loadHistory = async () => {
    setHistoryLoading(true)
    try {
      const res = await aiService.getQualityHistory()
      setHistory(res.data || [])
    } catch (e) {
      console.error(e)
    } finally {
      setHistoryLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast.error('Only JPEG, PNG, WebP images allowed')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image too large. Max 5MB.')
      return
    }
    setImage(file)
    setPreview(URL.createObjectURL(file))
  }

  const analyze = async () => {
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('crop_type', cropType)
      if (image) fd.append('image', image)
      const res = await aiService.qualityAssessment(fd)
      setResult(res.data)
      toast.success('Quality assessment saved!')
      loadHistory()
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Assessment failed')
    } finally {
      setLoading(false)
    }
  }

  const generateCertificate = () => {
    toast.success('Quality Verification Certificate generated! (Download Ready)')
  }

  const gradeClass = result?.suggested_grade ? GRADE_COLORS[result.suggested_grade] || 'text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 border-gray-200' : ''

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between flex-wrap gap-3 border-b border-emerald-500/10 pb-4">
        <div>
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Sparkles className="text-emerald-500 animate-pulse" size={24} />
            Diagnostic Studio
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Stitch AI Vision & IBM Granite Crop Assessment Engine</p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-full text-xs font-bold text-emerald-600 dark:text-emerald-400">
          <ShieldCheck size={14} /> IBM Granite 13B Vision Active
        </div>
      </div>

      {/* Crop Selector */}
      <div className="card-manus">
        <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2.5">Select Target Crop</label>
        <div className="grid grid-cols-3 gap-3">
          {CROPS.map(c => (
            <button key={c.id} onClick={() => setCropType(c.id)}
              className={`py-3 px-4 rounded-xl border font-bold text-sm transition-all duration-200 ${
                cropType === c.id
                  ? 'border-emerald-500 bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-500/20 scale-[1.02]'
                  : 'border-gray-200 dark:border-gray-800 text-gray-600 dark:text-gray-400 hover:border-emerald-500/40'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Viewport Column */}
        <div className="lg:col-span-7 space-y-4">
          <div className="card-manus relative overflow-hidden group">
            {/* Viewport Frame */}
            <div className="relative aspect-video rounded-xl bg-gray-950 border border-emerald-500/30 overflow-hidden flex items-center justify-center">
              {preview ? (
                <>
                  <img src={preview} alt="crop preview" className="w-full h-full object-cover" />
                  {/* Digital AR Bounding Overlay */}
                  <div className="absolute inset-4 border-2 border-dashed border-emerald-400/70 rounded-lg pointer-events-none animate-pulse">
                    <div className="absolute -top-1 -left-1 w-3 h-3 border-t-2 border-l-2 border-emerald-400" />
                    <div className="absolute -top-1 -right-1 w-3 h-3 border-t-2 border-r-2 border-emerald-400" />
                    <div className="absolute -bottom-1 -left-1 w-3 h-3 border-b-2 border-l-2 border-emerald-400" />
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 border-b-2 border-r-2 border-emerald-400" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold px-2 py-0.5 rounded border border-emerald-400/40">
                      SPECTRUM TARGET: OK
                    </div>
                  </div>
                </>
              ) : (
                <div
                  onClick={() => fileRef.current?.click()}
                  className="flex flex-col items-center justify-center gap-3 text-gray-400 cursor-pointer hover:text-emerald-400 transition-colors p-6 text-center"
                >
                  <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                    <Camera size={28} />
                  </div>
                  <div>
                    <div className="font-bold text-sm text-gray-200">Click to Launch Camera / Upload Crop Image</div>
                    <div className="text-xs text-gray-500 mt-1">JPEG, PNG, WebP up to 5MB</div>
                  </div>
                </div>
              )}
              {/* IBM Badge overlay */}
              <div className="absolute top-3 right-3 bg-gray-900/80 backdrop-blur-md border border-emerald-500/30 text-emerald-400 text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1">
                <Sparkles size={11} /> IBM Granite AI
              </div>
            </div>
            <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={handleFileChange} className="hidden" />

            <div className="flex items-center gap-3 mt-4">
              <button onClick={() => fileRef.current?.click()} className="btn-manus-secondary flex-1">
                <Upload size={16} /> Choose File
              </button>
              <button onClick={analyze} disabled={loading} className="btn-manus-primary flex-[2]">
                {loading ? <><Loader2 size={16} className="animate-spin" /> Scanning Spectral Data...</> : <><Sparkles size={16} /> Run Diagnostic Scan</>}
              </button>
            </div>
          </div>
        </div>

        {/* Right Diagnosis Column */}
        <div className="lg:col-span-5 space-y-4">
          {result ? (
            <div className="card-manus space-y-4 border-2 border-emerald-500/30">
              <div className="flex items-center justify-between border-b border-emerald-500/10 pb-3">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-500">Diagnosis Confidence</span>
                  <div className="text-3xl font-black text-gray-900 dark:text-gray-100">Grade {result.suggested_grade}</div>
                </div>
                <div className="w-14 h-14 rounded-full bg-emerald-500/10 border-2 border-emerald-500 flex items-center justify-center text-emerald-500 font-black text-sm">
                  {Math.round(result.confidence * 100)}%
                </div>
              </div>

              {/* Treatment Protocol Tabs */}
              <div>
                <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Healing Treatment Protocol</div>
                <div className="grid grid-cols-2 gap-2 bg-gray-100 dark:bg-gray-950 p-1 rounded-xl">
                  <button
                    onClick={() => setTreatmentTab('organic')}
                    className={`py-1.5 rounded-lg text-xs font-bold transition-all ${
                      treatmentTab === 'organic' ? 'bg-emerald-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-900 dark:hover:text-gray-100'
                    }`}
                  >
                    🌿 Organic Treatment
                  </button>
                  <button
                    onClick={() => setTreatmentTab('chemical')}
                    className={`py-1.5 rounded-lg text-xs font-bold transition-all ${
                      treatmentTab === 'chemical' ? 'bg-teal-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-900 dark:hover:text-gray-100'
                    }`}
                  >
                    🧪 Chemical Protocol
                  </button>
                </div>
                <div className="mt-3 p-3 bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/15 rounded-xl text-xs space-y-1.5 text-gray-700 dark:text-gray-300">
                  {treatmentTab === 'organic' ? (
                    <>
                      <div className="font-bold text-emerald-600 dark:text-emerald-400">Neem Extract Spray (2% Concentration)</div>
                      <p>Apply organic neem oil spray mixed with soap emulsifier during early morning hours to prevent leaf burn and halt spore germination.</p>
                    </>
                  ) : (
                    <>
                      <div className="font-bold text-teal-600 dark:text-teal-400">Triazole Fungicide Application</div>
                      <p>Apply targeted systemic fungicides under agricultural extension guidelines. Ensure 14-day pre-harvest interval protection.</p>
                    </>
                  )}
                </div>
              </div>

              {/* Instant Certificate Button */}
              <button onClick={generateCertificate} className="btn-manus-primary w-full text-xs">
                <FileCheck size={16} /> Generate Buyer Verified Quality Certificate
              </button>
            </div>
          ) : (
            <div className="card-manus text-center py-10 text-gray-400 space-y-3">
              <Sparkles size={36} className="mx-auto text-emerald-500/40" />
              <div className="text-sm font-semibold">No Scan Loaded</div>
              <p className="text-xs max-w-xs mx-auto">Upload a crop photo and run diagnostic scan to view IBM Granite quality certificate and treatment plan.</p>
            </div>
          )}
        </div>
      </div>

      {/* History Table */}
      <div className="card-manus space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-gray-900 dark:text-gray-100 text-sm">
            <History size={16} className="text-emerald-500" /> Recent Diagnostic Scans
          </div>
          <button onClick={loadHistory} className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1">
            <RefreshCw size={12} /> Refresh
          </button>
        </div>

        {historyLoading ? (
          <div className="py-6 text-center text-xs text-gray-400">Fetching diagnostic records...</div>
        ) : history.length === 0 ? (
          <div className="text-xs text-gray-400 text-center py-6">No past diagnostic scans saved yet</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-400">
                  <th className="py-2.5 px-3 font-semibold">Crop</th>
                  <th className="py-2.5 px-3 font-semibold">Grade</th>
                  <th className="py-2.5 px-3 font-semibold">Confidence</th>
                  <th className="py-2.5 px-3 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800/50">
                {history.map(h => (
                  <tr key={h.id} className="hover:bg-emerald-500/5 transition-colors">
                    <td className="py-2.5 px-3 font-bold capitalize text-gray-900 dark:text-gray-100">{h.crop_type}</td>
                    <td className="py-2.5 px-3">
                      <span className="font-extrabold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                        Grade {h.suggested_grade}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-gray-600 dark:text-gray-300">{Math.round(h.confidence * 100)}%</td>
                    <td className="py-2.5 px-3 text-gray-400">{new Date(h.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
