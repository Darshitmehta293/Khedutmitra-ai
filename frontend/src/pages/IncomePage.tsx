import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { farmerService, marketService } from '../services/api'
import { DashboardData, RevenueScenario } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts'
import { Loader2, TrendingUp } from 'lucide-react'

const fmt = (n: number) => `₹${n.toLocaleString('en-IN')}`

export default function IncomePage() {
  const { t } = useTranslation()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    farmerService.getDashboard().then(r => setData(r.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center h-40 items-center"><Loader2 className="animate-spin text-primary" size={28} /></div>

  const scenarioData = (data?.revenue_scenarios || []).map((s, i) => ({
    name: s.label,
    net: s.net_revenue,
    gross: s.gross_revenue,
    fill: i === 0 ? '#6b7280' : i === 1 ? '#1a7a4a' : '#22a05e',
  }))

  const cropPieData = [
    { name: 'Cotton', value: data?.cotton_quintals || 0, fill: '#f59e0b' },
    { name: 'Groundnut', value: data?.groundnut_quintals || 0, fill: '#1a7a4a' },
  ].filter(d => d.value > 0)

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-black">{t('income.title')}</h1>
        <div className="badge-demo">⚠ {t('common.demo_badge')}</div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: t('income.current_value'), val: fmt(data?.current_estimated_value || 0), color: 'text-gray-900' },
          { label: '7-Day Value', val: fmt(data?.expected_value_7d || 0), color: 'text-primary' },
          { label: t('income.expected_gain'), val: `+${fmt(data?.potential_gain || 0)}`, color: 'text-green-600' },
          { label: 'Inventory', val: `${data?.total_inventory_quintals || 0}q`, color: 'text-gray-700' },
        ].map(({ label, val, color }) => (
          <div key={label} className="card">
            <div className="text-xs text-gray-500 mb-1">{label}</div>
            <div className={`text-xl font-black ${color}`}>{val}</div>
          </div>
        ))}
      </div>

      {/* Revenue Scenarios Chart */}
      {scenarioData.length > 0 && (
        <div className="card">
          <h2 className="font-semibold mb-4 flex items-center gap-2"><TrendingUp size={16} className="text-primary" /> {t('income.scenarios')}</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={scenarioData} barCategoryGap="30%">
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: any) => [fmt(v), 'Net Revenue']} />
              <Bar dataKey="net" radius={[6, 6, 0, 0]} label={{ position: 'top', formatter: (v: any) => `₹${(v/1000).toFixed(0)}k`, fontSize: 11 }}>
                {scenarioData.map((d, i) => <Cell key={i} fill={d.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-gray-400 text-center mt-2">Net revenue after all estimated costs</p>
        </div>
      )}

      {/* Crop Breakdown Pie */}
      {cropPieData.length > 0 && (
        <div className="card">
          <h2 className="font-semibold mb-3">Inventory Breakdown</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={cropPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}
                label={({ name, value }) => `${name}: ${value}q`} labelLine>
                {cropPieData.map((d, i) => <Cell key={i} fill={d.fill} />)}
              </Pie>
              <Legend />
              <Tooltip formatter={(v: any) => [`${v} quintals`]} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Buyer Opportunities */}
      {data?.top_buyers && data.top_buyers.length > 0 && (
        <div className="card">
          <h2 className="font-semibold mb-3">Best Buyer Prices</h2>
          <div className="space-y-2">
            {data.top_buyers.map((b, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-2.5">
                <div>
                  <div className="text-sm font-medium">{b.buyer_name}</div>
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
    </div>
  )
}
