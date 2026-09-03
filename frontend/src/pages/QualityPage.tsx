import React, { useState, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { aiService } from '../services/api'
import { QualityAssessmentResult } from '../types'
import { Upload, Camera, AlertTriangle, Loader2, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const CROPS = [
  { id: 'cotton', label: 'Cotton 🌸', gu: 'કપાસ' },
  { id: 'groundnut', label: 'Groundnut 🥜', gu: 'મગફળી' },
]

const GRADE_COLORS: Record<string, string> = {
  A: 'text-green-600 bg-green-50 border-green-200',
  B: 'text-amber-600 bg-amber-50 border-amber-200',
  C: 'text-red-500 bg-red-50 border-red-200',
}

export default function QualityPage() {
  const { t } = useTranslation()
  const [cropType, setCropType] = useState('cotton')
  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<QualityAssessmentResult | null>(null)
  const [loading, setLoading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

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
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Assessment failed')
    } finally {
      setLoading(false)
    }
  }

  const gradeClass = result?.suggested_grade ? GRADE_COLORS[result.suggested_grade] || 'text-gray-600 bg-gray-50 border-gray-200' : ''

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-black">{t('quality.title')}</h1>
        <div className="badge-demo">⚠ Mock AI</div>
      </div>

      {/* Crop selector */}
      <div className="card">
        <label className="block text-sm font-medium text-gray-700 mb-2">Crop Type</label>
        <div className="grid grid-cols-2 gap-3">
          {CROPS.map(c => (
            <button key={c.id} onClick={() => setCropType(c.id)}
              className={`py-3 px-4 rounded-xl border-2 text-sm font-semibold transition-all ${
                cropType === c.id ? 'border-primary bg-green-50 text-primary' : 'border-gray-200 text-gray-600'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* Upload */}
      <div className="card">
        <label className="block text-sm font-medium text-gray-700 mb-3">{t('quality.upload_image')}</label>
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-gray-200 rounded-2xl p-8 text-center cursor-pointer hover:border-primary transition-colors"
        >
          {preview ? (
            <img src={preview} alt="crop" className="max-h-40 mx-auto rounded-xl object-cover" />
          ) : (
            <div className="flex flex-col items-center gap-2 text-gray-400">
              <Camera size={32} />
              <span className="text-sm">Click to upload crop photo</span>
              <span className="text-xs">JPEG, PNG, WebP — max 5MB</span>
            </div>
          )}
        </div>
        <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={handleFileChange} className="hidden" />

        <button onClick={analyze} disabled={loading}
          className="btn-primary w-full mt-4 flex items-center justify-center gap-2">
          {loading ? <><Loader2 size={16} className="animate-spin" /> Analyzing...</> : t('quality.analyze_btn')}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="space-y-4">
          <div className={`card border-2 ${gradeClass}`}>
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm text-gray-500 mb-1">{t('quality.suggested_grade')}</div>
                <div className="text-5xl font-black">Grade {result.suggested_grade}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">{t('quality.confidence')}</div>
                <div className="text-2xl font-bold">{Math.round(result.confidence * 100)}%</div>
                <div className="text-xs text-gray-400 mt-1">AI Confidence</div>
              </div>
            </div>

            {/* Assessment details */}
            <div className="grid grid-cols-2 gap-2 mt-3">
              {Object.entries(result.assessment_details || {}).map(([key, value]) => {
                if (key === 'visual_notes') return null
                return (
                  <div key={key} className="bg-white/50 rounded-lg px-3 py-2">
                    <div className="text-xs text-gray-400 capitalize">{key.replace(/_/g, ' ')}</div>
                    <div className="text-sm font-medium">{String(value)}</div>
                  </div>
                )
              })}
            </div>

            {result.assessment_details?.visual_notes && (
              <div className="mt-3 bg-white/50 rounded-xl p-3">
                <div className="text-xs text-gray-400 mb-1">Visual Notes</div>
                <div className="text-sm text-gray-700">{String(result.assessment_details.visual_notes)}</div>
              </div>
            )}
          </div>

          {/* Disclaimer */}
          <div className="card border-amber-200 bg-amber-50">
            <div className="flex items-start gap-2">
              <AlertTriangle size={15} className="text-amber-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-amber-800">{result.disclaimer}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
