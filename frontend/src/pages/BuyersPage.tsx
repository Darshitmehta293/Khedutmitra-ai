import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { buyerService } from '../services/api'
import { BuyerMatch } from '../types'
import { MapPin, Package, Star, Phone, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

const CROPS = [
  { id: 'crop_cotton', label: 'Cotton 🌸' },
  { id: 'crop_groundnut', label: 'Groundnut 🥜' },
]
const DISTRICTS = ['Ahmedabad','Rajkot','Junagadh','Bhavnagar','Amreli','Surendranagar','Anand']
const GRADES = ['A', 'B', 'C']
const fmt = (n: number) => `₹${n.toLocaleString('en-IN')}`

function ScoreBar({ score }: { score: number }) {
  const color = score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-amber-500' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-100 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs font-bold text-gray-700 w-8">{score.toFixed(0)}%</span>
    </div>
  )
}

export default function BuyersPage() {
  const { t } = useTranslation()
  const [cropId, setCropId] = useState('crop_cotton')
  const [quantity, setQuantity] = useState('50')
  const [grade, setGrade] = useState('B')
  const [district, setDistrict] = useState('Ahmedabad')
  const [matches, setMatches] = useState<BuyerMatch[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [contactedId, setContactedId] = useState<string | null>(null)
  const [submittingId, setSubmittingId] = useState<string | null>(null)

  const search = async () => {
    setLoading(true)
    setSearched(true)
    try {
      const res = await buyerService.getMatches({ crop_id: cropId, quantity: parseFloat(quantity), quality_grade: grade, district })
      setMatches(res.data.matches || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { search() }, [])

  const sendEnquiry = async (listing: BuyerMatch) => {
    setSubmittingId(listing.listing_id)
    try {
      await buyerService.createOffer({
        buyer_listing_id: listing.listing_id,
        quantity: Math.max(parseFloat(quantity), listing.min_quantity),
        offered_price: listing.offered_price,
        message: 'Farmer enquiry from KhedutMitra marketplace',
      })
      setContactedId(listing.listing_id)
      toast.success('Enquiry sent to buyer')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Could not contact buyer')
    } finally {
      setSubmittingId(null)
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-black">{t('buyers.title')}</h1>
        <div className="badge-demo">⚠ {t('common.demo_badge')}</div>
      </div>

      {/* Filter */}
      <div className="card">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <select value={cropId} onChange={e => setCropId(e.target.value)} className="select-field">
            {CROPS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
          </select>
          <input value={quantity} onChange={e => setQuantity(e.target.value)}
            type="number" min="1" className="input-field" placeholder="Quantity (q)" />
          <select value={grade} onChange={e => setGrade(e.target.value)} className="select-field">
            {GRADES.map(g => <option key={g} value={g}>Grade {g}</option>)}
          </select>
          <select value={district} onChange={e => setDistrict(e.target.value)} className="select-field">
            {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <button onClick={search} disabled={loading} className="btn-primary w-full mt-3">
          {loading ? 'Searching...' : 'Find Buyers'}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center h-32 items-center"><Loader2 className="animate-spin text-primary" size={28} /></div>
      ) : searched && matches.length === 0 ? (
        <div className="card text-center py-10 text-gray-400">No buyers found for this search</div>
      ) : (
        <div className="space-y-3">
          {matches.map((m, i) => (
            <div key={m.listing_id} className={`card ${i === 0 ? 'border-primary/40 bg-green-50/30' : ''}`}>
              {i === 0 && <div className="text-xs font-bold text-primary mb-2">⭐ Best Match</div>}
              <div className="flex items-start justify-between gap-3 flex-wrap">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="font-bold">{m.buyer_name}</div>
                    {m.is_demo && <span className="badge-demo text-xs">DEMO</span>}
                  </div>
                  <div className="text-xs text-gray-500 capitalize">{m.buyer_type.replace('_', ' ')}</div>
                  <div className="flex items-center gap-3 mt-2 flex-wrap text-xs text-gray-500">
                    <span className="flex items-center gap-1"><MapPin size={12} /> {m.district} ({m.distance_km}km)</span>
                    <span className="flex items-center gap-1"><Package size={12} /> {m.min_quantity}–{m.max_quantity}q</span>
                    <span>Grade {m.quality_requirement}</span>
                    <span>{m.delivery_days}d delivery</span>
                  </div>
                  <div className="mt-2 text-xs text-gray-500 italic">{m.reason}</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-black text-primary">{fmt(m.offered_price)}</div>
                  <div className="text-xs text-gray-400">/quintal</div>
                  <div className="mt-2">
                    <ScoreBar score={m.match_score} />
                  </div>
                </div>
              </div>

              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => sendEnquiry(m)}
                  disabled={submittingId === m.listing_id || contactedId === m.listing_id}
                  className={`flex-1 py-2 rounded-xl text-sm font-semibold border transition-all ${
                    contactedId === m.listing_id
                      ? 'bg-primary text-white border-primary'
                      : 'border-primary text-primary hover:bg-primary/5'
                  }`}
                >
                  {submittingId === m.listing_id ? 'Sending...' : contactedId === m.listing_id ? '✓ Enquiry Sent' : t('buyers.contact_buyer')}
                </button>
                <button onClick={() => sendEnquiry(m)} disabled={submittingId === m.listing_id}
                  className="px-4 py-2 bg-gray-100 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-200 transition disabled:opacity-50">
                  {t('buyers.request_quote')}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
