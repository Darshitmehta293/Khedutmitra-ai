import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'
import { farmerService } from '../services/api'
import { DashboardData, RecommendationAction } from '../types'
import { TrendingUp, TrendingDown, Users, PiggyBank, BarChart3, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import RecommendationBadge from '../components/RecommendationBadge'

const fmt = (n: number) => `₹${n.toLocaleString('en-IN')}`

function StatCard({ label, value, sub, color = 'text-gray-900' }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <div className="card relative overflow-hidden">
      <div className="absolute right-0 top-0 h-16 w-16 translate-x-5 -translate-y-5 rounded-full bg-primary/5" />
      <div className="relative text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-400 mb-2">{label}</div>
      <div className={`relative text-2xl font-black ${color}`}>{value}</div>
      {sub && <div className="relative text-xs text-gray-400 mt-1">{sub}</div>}
    </div>
  )
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    farmerService.getDashboard().then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="animate-spin text-primary" size={32} />
    </div>
  )

  const lang = user?.language || 'gu'
  const greeting = t('dashboard.greeting')

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-gray-200/80 pb-5">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-primary/70 mb-2">Your market brief</div>
          <h1 className="text-3xl font-black text-gray-900">{greeting}, {user?.name?.split(' ')[0]} <span className="text-primary">.</span></h1>
          <p className="text-sm text-gray-500 mt-0.5">{data?.district} • Gujarat</p>
        </div>
        <div className="badge-demo">⚠ {t('common.demo_badge')}</div>
      </div>

      {/* Recommendation Hero */}
      {data?.recommendation_action && (
        <div className="card bg-gradient-to-br from-[#eff8ef] via-white to-[#fff8e8] border-primary/15">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-primary/70 mb-2">{t('dashboard.recommendation')}</div>
              <RecommendationBadge action={data.recommendation_action as RecommendationAction} size="lg" />
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Potential Gain</div>
              <div className="text-2xl font-black text-primary">+{fmt(data.potential_gain)}</div>
              <Link to="/sell-or-store" className="text-xs text-primary underline mt-1 inline-block">Full Analysis →</Link>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label={t('dashboard.current_value')} value={fmt(data?.current_estimated_value || 0)} sub={`${data?.total_inventory_quintals || 0} quintals`} color="text-primary" />
        <StatCard label={t('dashboard.expected_value')} value={fmt(data?.expected_value_7d || 0)} sub="7-day forecast" />
        <StatCard label={t('dashboard.buyers_available')} value={String(data?.active_buyer_opportunities || 0)} sub="matched buyers" color="text-blue-600" />
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Today's Price</div>
          <div className="text-2xl font-black text-gray-900">{fmt(data?.current_price || 0)}</div>
          <div className="text-xs text-gray-400">/ quintal</div>
        </div>
      </div>

      {/* Inventory */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">{t('dashboard.total_inventory')}</h2>
          <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-gray-400">Live snapshot</span>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-amber-50 rounded-xl p-4">
            <div className="text-sm text-amber-700 font-medium">{t('dashboard.cotton')} 🌸</div>
            <div className="text-2xl font-black text-amber-900">{data?.cotton_quintals || 0} q</div>
          </div>
          <div className="bg-green-50 rounded-xl p-4">
            <div className="text-sm text-green-700 font-medium">{t('dashboard.groundnut')} 🥜</div>
            <div className="text-2xl font-black text-green-900">{data?.groundnut_quintals || 0} q</div>
          </div>
        </div>
      </div>

      {/* Revenue Scenarios */}
      {data?.revenue_scenarios && data.revenue_scenarios.length > 0 && (
        <div className="card">
          <h2 className="font-semibold mb-3 flex items-center gap-2"><BarChart3 size={16} className="text-primary" /> Revenue Scenarios</h2>
          <div className="space-y-2">
            {data.revenue_scenarios.map((s, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3">
                <div>
                  <div className="font-medium text-sm">{s.label}</div>
                  <div className="text-xs text-gray-400">Net after costs</div>
                </div>
                <div className={`font-bold ${i === 0 ? 'text-gray-700' : 'text-primary'}`}>{fmt(s.net_revenue)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Buyers */}
      {data?.top_buyers && data.top_buyers.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold flex items-center gap-2"><Users size={16} className="text-primary" /> Top Buyers</h2>
            <Link to="/buyers" className="text-xs text-primary">View All →</Link>
          </div>
          <div className="space-y-2">
            {data.top_buyers.slice(0, 3).map((b, i) => (
              <div key={i} className="flex items-center justify-between border border-gray-100 rounded-xl px-4 py-2.5">
                <div>
                  <div className="font-medium text-sm">{b.buyer_name}</div>
                  <div className="text-xs text-gray-400">{b.district} • {b.distance_km}km</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-primary">{fmt(b.offered_price)}/q</div>
                  <div className="text-xs text-gray-400">{b.match_score.toFixed(0)}% match</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Links */}
      <div className="grid grid-cols-2 gap-3">
        <Link to="/sell-or-store" className="card hover:border-primary transition-colors cursor-pointer text-center py-4">
          <div className="text-2xl mb-1">⚖️</div>
          <div className="font-semibold text-sm">Sell or Store?</div>
          <div className="text-xs text-gray-400">Full AI analysis</div>
        </Link>
        <Link to="/ai" className="card hover:border-primary transition-colors cursor-pointer text-center py-4">
          <div className="text-2xl mb-1">🤖</div>
          <div className="font-semibold text-sm">Ask AI</div>
          <div className="text-xs text-gray-400">In Gujarati/Hindi</div>
        </Link>
      </div>
    </div>
  )
}
