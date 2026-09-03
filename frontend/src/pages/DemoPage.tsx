import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { aiService } from '../services/api'
import { RecommendationResult, RecommendationAction, AgentTrace } from '../types'
import { Loader2, Play, CheckCircle, AlertTriangle, Info, Users, TrendingUp } from 'lucide-react'
import RecommendationBadge from '../components/RecommendationBadge'
import AgentTracePanel from '../components/AgentTracePanel'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Link } from 'react-router-dom'

const fmt = (n: number) => `₹${Math.abs(n).toLocaleString('en-IN')}`

export default function DemoPage() {
  const { t } = useTranslation()
  const [result, setResult] = useState<RecommendationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(0)
  const [stepLabels, setStepLabels] = useState<string[]>([])

  const DEMO_STEPS = [
    'Loading current cotton prices from Gujarat mandis...',
    'Running Mandi Price Intelligence Agent...',
    'Generating 7-day price forecast...',
    'Calculating storage vs. selling economics...',
    'Finding matched buyers in Ahmedabad area...',
    'Computing income scenarios...',
    'IBM Granite generating recommendation...',
    'Analysis complete!',
  ]

  const runDemo = async () => {
    setLoading(true)
    setResult(null)
    setStep(0)

    // Animate steps
    for (let i = 0; i < DEMO_STEPS.length - 1; i++) {
      setStep(i)
      await new Promise(r => setTimeout(r, 600))
    }

    try {
      const res = await aiService.demoScenario('crop_cotton', 50, 'Ahmedabad')
      setResult(res.data)
      setStep(DEMO_STEPS.length - 1)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { runDemo() }, [])

  const chartData = result ? [
    { label: 'Sell Now', value: result.current_revenue, color: '#6b7280' },
    { label: `Store ${result.recommended_days || 7}d`, value: result.expected_net_revenue, color: '#1a7a4a' },
  ] : []

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <div className="bg-primary text-white px-4 py-5 text-center">
        <div className="max-w-2xl mx-auto">
          <div className="text-xs font-semibold opacity-70 mb-1 uppercase tracking-wider">IBM Hackathon Challenge 13 — Demo</div>
          <h1 className="text-3xl font-black mb-1">KhedutMitra AI</h1>
          <p className="text-green-100 text-sm">Know the Price. Find the Buyer. Sell Smarter.</p>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-5">
        {/* Demo scenario card */}
        <div className="card bg-amber-50 border-amber-200">
          <div className="text-xs font-bold text-amber-700 mb-3">🎯 DEMO SCENARIO</div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {[
              { label: 'Farmer', val: 'Ramesh Patel' },
              { label: 'Location', val: 'Ahmedabad, Gujarat' },
              { label: 'Crop', val: 'Cotton (Grade A)' },
              { label: 'Quantity', val: '50 Quintals' },
            ].map(({ label, val }) => (
              <div key={label}>
                <div className="text-gray-500 text-xs">{label}</div>
                <div className="font-semibold">{val}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Loading steps */}
        {(loading || result) && (
          <div className="card">
            <div className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                <span className="text-white text-xs">AI</span>
              </div>
              Multi-Agent Pipeline
            </div>
            <div className="space-y-2">
              {DEMO_STEPS.map((label, i) => (
                <div key={i} className={`flex items-center gap-2 text-sm transition-all ${i <= step ? 'opacity-100' : 'opacity-25'}`}>
                  {i < step || !loading ? (
                    <CheckCircle size={15} className="text-green-500 flex-shrink-0" />
                  ) : i === step && loading ? (
                    <Loader2 size={15} className="animate-spin text-primary flex-shrink-0" />
                  ) : (
                    <div className="w-3.5 h-3.5 rounded-full border-2 border-gray-300 flex-shrink-0" />
                  )}
                  <span className={i <= step ? 'text-gray-700' : 'text-gray-400'}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <>
            {/* Recommendation hero */}
            <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
              <div className="text-center py-2">
                <div className="text-sm text-gray-500 mb-3">AI Recommendation for Ramesh Patel</div>
                <div className="flex justify-center mb-4">
                  <RecommendationBadge action={result.action as RecommendationAction} days={result.recommended_days} size="lg" />
                </div>
                <div className="grid grid-cols-3 gap-3 mt-4">
                  <div className="bg-white/70 rounded-xl p-3">
                    <div className="text-xs text-gray-500">Current Price</div>
                    <div className="font-black text-lg">{fmt(result.current_price)}</div>
                    <div className="text-xs text-gray-400">/quintal</div>
                  </div>
                  <div className="bg-white/70 rounded-xl p-3">
                    <div className="text-xs text-gray-500">7-Day Forecast</div>
                    <div className="font-black text-lg text-primary">{fmt(result.forecast_price)}</div>
                    <div className="text-xs text-gray-400">{Math.round(result.forecast_confidence * 100)}% conf.</div>
                  </div>
                  <div className="bg-white/70 rounded-xl p-3">
                    <div className="text-xs text-gray-500">Potential Gain</div>
                    <div className={`font-black text-lg ${result.potential_gain >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {result.potential_gain >= 0 ? '+' : '-'}{fmt(result.potential_gain)}
                    </div>
                    <div className="text-xs text-gray-400">if stored</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Revenue comparison */}
            <div className="card">
              <h2 className="font-semibold mb-3">Revenue Comparison</h2>
              <ResponsiveContainer width="100%" height={130}>
                <BarChart data={chartData} layout="vertical">
                  <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                  <YAxis type="category" dataKey="label" tick={{ fontSize: 12 }} width={75} />
                  <Tooltip formatter={(v: any) => [fmt(v), 'Revenue']} />
                  <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                    {chartData.map((d, i) => <Cell key={i} fill={d.color} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
                <div className="bg-gray-50 rounded-xl px-3 py-2">
                  <div className="text-xs text-gray-400">Storage Cost</div>
                  <div className="font-semibold">-{fmt(result.storage_cost)}</div>
                </div>
                <div className="bg-gray-50 rounded-xl px-3 py-2">
                  <div className="text-xs text-gray-400">Net Revenue ({result.recommended_days || 7}d)</div>
                  <div className="font-semibold text-primary">{fmt(result.expected_net_revenue)}</div>
                </div>
              </div>
            </div>

            {/* Granite explanation */}
            <div className="card border-blue-100 bg-blue-50">
              <div className="flex items-start gap-2">
                <Info size={16} className="text-blue-500 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-xs font-semibold text-blue-600 mb-1">IBM Granite Explanation</div>
                  <p className="text-sm text-gray-700 leading-relaxed">{result.granite_explanation}</p>
                </div>
              </div>
            </div>

            {/* Top Buyers */}
            {result.buyer_matches?.length > 0 && (
              <div className="card">
                <h2 className="font-semibold mb-3 flex items-center gap-2"><Users size={15} className="text-primary" /> Matched Buyers</h2>
                {result.buyer_matches.map((b, i) => (
                  <div key={i} className="flex items-center justify-between border-b border-gray-50 py-2.5 last:border-0">
                    <div>
                      <div className="font-medium text-sm">{b.buyer_name}</div>
                      <div className="text-xs text-gray-400">{b.district} • {b.distance_km}km • Grade {b.quality_requirement}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-primary">{fmt(b.offered_price)}/q</div>
                      <div className="text-xs text-gray-400">{b.match_score.toFixed(0)}% match</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Agent trace */}
            <AgentTracePanel trace={result.agent_trace} />

            {/* Disclaimer */}
            <div className="card border-amber-100 bg-amber-50">
              <div className="flex items-start gap-2">
                <AlertTriangle size={14} className="text-amber-500 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-amber-700">{result.disclaimer}</p>
              </div>
            </div>

            {/* Re-run + Login CTAs */}
            <div className="grid grid-cols-2 gap-3">
              <button onClick={runDemo} className="btn-secondary text-sm py-3">
                🔄 Re-run Demo
              </button>
              <Link to="/register" className="btn-primary text-sm py-3 text-center">
                Create Account →
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
