import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { marketService } from '../services/api'
import { PriceData, PricePoint } from '../types'
import { TrendingUp, TrendingDown, Minus, Loader2, AlertTriangle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
import toast from 'react-hot-toast'

const CROPS = [
  { id: 'crop_cotton', label: 'Cotton 🌸', gu: 'કપાસ' },
  { id: 'crop_groundnut', label: 'Groundnut 🥜', gu: 'મગફળી' },
]
const DISTRICTS = ['Ahmedabad','Rajkot','Junagadh','Bhavnagar','Amreli','Surendranagar','Anand']
const MANDI_MAP: Record<string, string> = {
  Ahmedabad: 'mkt_ahmedabad', Rajkot: 'mkt_rajkot', Junagadh: 'mkt_junagadh',
  Bhavnagar: 'mkt_bhavnagar', Amreli: 'mkt_amreli', Surendranagar: 'mkt_surendranagar',
  Anand: 'mkt_anand',
}

const fmt = (n: number) => `₹${n.toLocaleString('en-IN')}`

export default function MarketPage() {
  const { t } = useTranslation()
  const [cropId, setCropId] = useState('crop_cotton')
  const [district, setDistrict] = useState('Ahmedabad')
  const [priceData, setPriceData] = useState<PriceData | null>(null)
  const [trendData, setTrendData] = useState<{ date: string; min: number; max: number; modal: number }[]>([])
  const [forecastData, setForecastData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [priceRes, trendRes, fcRes] = await Promise.allSettled([
        marketService.getPrices(cropId, undefined, district),
        marketService.getPriceTrend(cropId, MANDI_MAP[district] || 'mkt_ahmedabad', 30),
        marketService.getForecast(cropId, MANDI_MAP[district] || 'mkt_ahmedabad'),
      ])
      if (priceRes.status === 'fulfilled') {
        setPriceData(priceRes.value.data)
      } else {
        setPriceData(null)
        toast.error('Market prices are unavailable right now')
      }
      setTrendData(trendRes.status === 'fulfilled' ? trendRes.value.data.prices || [] : [])
      setForecastData(fcRes.status === 'fulfilled' ? fcRes.value.data : null)
      if (trendRes.status === 'rejected' || fcRes.status === 'rejected') {
        toast.error('Some market details could not be loaded')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [cropId, district])

  const TrendIcon = priceData?.trend === 'upward' ? TrendingUp : priceData?.trend === 'downward' ? TrendingDown : Minus
  const trendColor = priceData?.trend === 'upward' ? 'text-green-600' : priceData?.trend === 'downward' ? 'text-red-500' : 'text-gray-500'

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-black">{t('market.title')}</h1>
        <div className="badge-demo">⚠ {t('market.demo_label')}</div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-2 gap-3">
        <select value={cropId} onChange={e => setCropId(e.target.value)} className="select-field">
          {CROPS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
        </select>
        <select value={district} onChange={e => setDistrict(e.target.value)} className="select-field">
          {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40"><Loader2 className="animate-spin text-primary" size={28} /></div>
      ) : priceData ? (
        <>
          {/* Price Hero */}
          <div className="card bg-gradient-to-br from-green-50 to-teal-50 border-green-100">
            <div className="flex items-start justify-between flex-wrap gap-4">
              <div>
                <div className="text-sm text-gray-500 mb-1">{t('market.current_price')} — {priceData.primary_market_name}</div>
                <div className="text-4xl font-black text-gray-900">{fmt(priceData.current_price)}</div>
                <div className="text-sm text-gray-500">per quintal</div>
              </div>
              <div className={`flex items-center gap-2 text-lg font-bold ${trendColor}`}>
                <TrendIcon size={22} />
                {priceData.trend_percentage > 0 ? '+' : ''}{priceData.trend_percentage.toFixed(1)}% (14d)
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 mt-4">
              {[
                { label: t('market.min_price'), val: fmt(priceData.min_price) },
                { label: 'Modal', val: fmt(priceData.current_price) },
                { label: t('market.max_price'), val: fmt(priceData.max_price) },
              ].map(({ label, val }) => (
                <div key={label} className="bg-white/70 rounded-xl p-3 text-center">
                  <div className="text-xs text-gray-500">{label}</div>
                  <div className="font-bold text-sm mt-0.5">{val}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Forecast */}
          {forecastData && (
            <div className="card">
              <div className="flex items-center justify-between mb-1">
                <h2 className="font-semibold">{t('market.forecast_7d')}</h2>
                <div className="text-xs text-gray-400">{Math.round(forecastData.confidence * 100)}% confidence</div>
              </div>
              <div className="flex items-baseline gap-2 mb-2">
                <span className="text-3xl font-black text-primary">{fmt(forecastData.predicted_price)}</span>
                <span className="text-sm text-gray-500">predicted</span>
              </div>
              <div className="text-xs text-gray-400 mb-3">Range: {fmt(forecastData.lower_bound)} – {fmt(forecastData.upper_bound)}</div>

              {/* Forecast series chart */}
              {forecastData.forecast_series?.length > 0 && (
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={forecastData.forecast_series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="horizon_days" tickFormatter={d => `+${d}d`} tick={{ fontSize: 11 }} />
                    <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(1)}k`} />
                    <Tooltip formatter={(v: any) => [fmt(v), 'Forecast']} labelFormatter={l => `In ${l} days`} />
                    <Line type="monotone" dataKey="predicted_price" stroke="#1a7a4a" strokeWidth={2} dot={{ r: 3 }} />
                    <Line type="monotone" dataKey="upper_bound" stroke="#a7f3d0" strokeWidth={1} dot={false} strokeDasharray="4 4" />
                    <Line type="monotone" dataKey="lower_bound" stroke="#a7f3d0" strokeWidth={1} dot={false} strokeDasharray="4 4" />
                  </LineChart>
                </ResponsiveContainer>
              )}
              <div className="mt-2 flex items-start gap-1.5 bg-amber-50 rounded-lg px-3 py-2">
                <AlertTriangle size={13} className="text-amber-500 mt-0.5 flex-shrink-0" />
                <span className="text-xs text-amber-700">{t('market.forecast_disclaimer')}</span>
              </div>
            </div>
          )}

          {/* Historical chart */}
          {trendData.length > 0 && (
            <div className="card">
              <h2 className="font-semibold mb-3">30-Day Price History</h2>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tickFormatter={d => d.slice(5)} tick={{ fontSize: 10 }} interval={4} />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(1)}k`} />
                  <Tooltip formatter={(v: any) => [fmt(v)]} />
                  <Line type="monotone" dataKey="modal" stroke="#1a7a4a" strokeWidth={2} dot={false} name="Modal Price" />
                  <Line type="monotone" dataKey="max" stroke="#22a05e" strokeWidth={1} dot={false} strokeDasharray="3 3" name="Max" />
                  <Line type="monotone" dataKey="min" stroke="#d1fae5" strokeWidth={1} dot={false} strokeDasharray="3 3" name="Min" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Nearby Mandis */}
          {priceData.nearby_mandis?.length > 0 && (
            <div className="card">
              <h2 className="font-semibold mb-3">Nearby Mandi Prices</h2>
              <div className="space-y-2">
                {priceData.nearby_mandis.map((m, i) => (
                  <div key={i} className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3">
                    <div>
                      <div className="font-medium text-sm">{m.market_name}</div>
                      <div className="text-xs text-gray-400">{m.arrivals_tonnes}t arrivals</div>
                    </div>
                    <div className="font-bold text-primary">{fmt(m.modal_price)}/q</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="card text-center py-10 text-gray-400">No data available</div>
      )}
    </div>
  )
}
