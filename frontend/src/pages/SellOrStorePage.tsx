import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { aiService } from '../services/api'
import { RecommendationResult, RecommendationAction } from '../types'
import { Loader2, AlertTriangle, Info, TrendingUp, Package, Users } from 'lucide-react'
import RecommendationBadge from '../components/RecommendationBadge'
import AgentTracePanel from '../components/AgentTracePanel'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const CROPS = [
  { id: 'crop_cotton', label: 'Cotton 🌸' },
  { id: 'crop_groundnut', label: 'Groundnut 🥜' },
]
const GRADES = ['A', 'B', 'C', 'ungraded']
const DISTRICTS = ['Ahmedabad','Rajkot','Junagadh','Bhavnagar','Amreli','Surendranagar','Anand']
const fmt = (n: number) => `₹${Math.abs(n).toLocaleString('en-IN')}`

export default function SellOrStorePage() {
  const { t } = useTranslation()
  const [form, setForm] = useState({
    crop_id: 'crop_cotton', quantity: '50', quality_grade: 'B',
    district: 'Ahmedabad', storage_available: true,
    storage_cost_per_quintal_per_day: '0.5', transport_cost_total: '2000', horizon_days: '7',
  })
  const [result, setResult] = useState<RecommendationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const set = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

  const analyze = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await aiService.getRecommendation({
        crop_id: form.crop_id,
        quantity: parseFloat(form.quantity),
        quality_grade: form.quality_grade,
        district: form.district,
        storage_available: form.storage_available,
        storage_cost_per_quintal_per_day: parseFloat(form.storage_cost_per_quintal_per_day),
        transport_cost_total: parseFloat(form.transport_cost_total),
        horizon_days: parseInt(form.horizon_days),
      })
      setResult(res.data)
    } catch (e: any) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const chartData = result ? [
    { label: 'Sell Now', value: result.current_revenue, color: '#6b7280' },
    { label: `Net ${form.horizon_days}d`, value: result.expected_net_revenue, color: result.expected_net_revenue > result.current_revenue ? '#1a7a4a' : '#ef4444' },
  ] : []

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-black">{t('sell_store.title')}</h1>
        <div className="badge-demo">⚠ {t('common.demo_badge')}</div>
      </div>

      {/* Input Form */}
      <div className="card">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Crop</label>
            <select value={form.crop_id} onChange={e => set('crop_id', e.target.value)} className="select-field">
              {CROPS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('sell_store.quantity')}</label>
            <input value={form.quantity} onChange={e => set('quantity', e.target.value)}
              type="number" min="1" className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('sell_store.quality_grade')}</label>
            <select value={form.quality_grade} onChange={e => set('quality_grade', e.target.value)} className="select-field">
              {GRADES.map(g => <option key={g} value={g}>Grade {g.toUpperCase()}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">District</label>
            <select value={form.district} onChange={e => set('district', e.target.value)} className="select-field">
              {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('sell_store.horizon')} (days)</label>
            <select value={form.horizon_days} onChange={e => set('horizon_days', e.target.value)} className="select-field">
              {[3, 7, 15, 30].map(d => <option key={d} value={d}>{d} days</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('sell_store.transport_cost')}</label>
            <input value={form.transport_cost_total} onChange={e => set('transport_cost_total', e.target.value)}
              type="number" className="input-field" />
          </div>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <input type="checkbox" id="storage" checked={form.storage_available}
            onChange={e => set('storage_available', e.target.checked)} className="w-4 h-4 accent-primary" />
          <label htmlFor="storage" className="text-sm text-gray-700">{t('sell_store.storage_available')}</label>
        </div>
        <button onClick={analyze} disabled={loading} className="btn-primary w-full mt-4 flex items-center justify-center gap-2">
          {loading ? <><Loader2 size={16} className="animate-spin" /> Analyzing...</> : t('sell_store.analyze_btn')}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Recommendation Hero */}
          <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-100">
            <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
              <div>
                <div className="text-sm text-gray-500 mb-2">AI Recommendation</div>
                <RecommendationBadge action={result.action as RecommendationAction} days={result.recommended_days} size="lg" />
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Potential Gain</div>
                <div className={`text-3xl font-black ${result.potential_gain >= 0 ? 'text-primary' : 'text-red-500'}`}>
                  {result.potential_gain >= 0 ? '+' : '-'}{fmt(result.potential_gain)}
                </div>
                <div className="text-xs text-gray-400">Confidence: {Math.round(result.confidence * 100)}%</div>
              </div>
            </div>

            {/* Revenue comparison chart */}
            <ResponsiveContainer width="100%" height={120}>
              <BarChart data={chartData} layout="vertical" barCategoryGap={8}>
                <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="label" tick={{ fontSize: 12 }} width={70} />
                <Tooltip formatter={(v: any) => [fmt(v), 'Revenue']} />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {chartData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Financial Breakdown */}
          <div className="card">
            <h2 className="font-semibold mb-3 flex items-center gap-2"><TrendingUp size={16} className="text-primary" /> Financial Breakdown</h2>
            <div className="space-y-2">
              {[
                { label: 'Current Price', val: `${fmt(result.current_price)}/quintal`, highlight: false },
                { label: t('sell_store.current_revenue'), val: fmt(result.current_revenue), highlight: false },
                { label: `${form.horizon_days}-day Forecast Price`, val: `${fmt(result.forecast_price)}/quintal`, highlight: false },
                { label: t('sell_store.future_revenue'), val: fmt(result.expected_future_revenue), highlight: false },
                { label: 'Storage Cost', val: `-${fmt(result.storage_cost)}`, highlight: false },
                { label: 'Transport Cost', val: `-${fmt(result.transport_cost)}`, highlight: false },
                { label: 'Quality Loss Cost', val: `-${fmt(result.quality_loss_cost)}`, highlight: false },
                { label: t('sell_store.net_revenue'), val: fmt(result.expected_net_revenue), highlight: true },
              ].map(({ label, val, highlight }) => (
                <div key={label} className={`flex justify-between py-2 ${highlight ? 'border-t border-primary/20 mt-1' : ''}`}>
                  <span className={`text-sm ${highlight ? 'font-bold text-gray-900' : 'text-gray-600'}`}>{label}</span>
                  <span className={`text-sm font-semibold ${highlight ? 'text-primary' : 'text-gray-900'}`}>{val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Granite Explanation */}
          <div className="card border-blue-100 bg-blue-50">
            <div className="flex items-start gap-2">
              <Info size={16} className="text-blue-500 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-semibold text-blue-600 mb-1">IBM Granite AI Explanation</div>
                <p className="text-sm text-gray-700 leading-relaxed">{result.granite_explanation}</p>
              </div>
            </div>
          </div>

          {/* Reasoning transparency */}
          <div className="card">
            <div className="flex items-start gap-2">
              <AlertTriangle size={15} className="text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-semibold text-amber-700 mb-1">{t('sell_store.reasoning')}</div>
                <p className="text-sm text-gray-600">{result.reasoning}</p>
                <p className="text-xs text-gray-400 mt-2">{result.disclaimer}</p>
              </div>
            </div>
          </div>

          {/* Best Buyer */}
          {result.best_buyer && (
            <div className="card border-primary/30">
              <h2 className="font-semibold mb-3 flex items-center gap-2"><Users size={16} className="text-primary" /> Best Matched Buyer</h2>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold">{result.best_buyer.buyer_name}</div>
                  <div className="text-sm text-gray-500">{result.best_buyer.district} • {result.best_buyer.distance_km}km</div>
                  <div className="text-xs text-gray-400 mt-1">{result.best_buyer.reason}</div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-black text-primary">{fmt(result.best_buyer.offered_price)}/q</div>
                  <div className="text-xs text-gray-400">{result.best_buyer.match_score.toFixed(0)}% match</div>
                </div>
              </div>
            </div>
          )}

          {/* Agent Trace */}
          <AgentTracePanel trace={result.agent_trace} />
        </div>
      )}
    </div>
  )
}
