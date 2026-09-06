import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { buyerService } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { BuyerMatch } from '../types'
import { MapPin, Package, Loader2, Inbox, PlusCircle, ShoppingBag, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const CROPS = [
  { id: 'crop_cotton', label: 'Cotton 🌸' },
  { id: 'crop_groundnut', label: 'Groundnut 🥜' },
]
const DISTRICTS = ['Ahmedabad', 'Rajkot', 'Junagadh', 'Bhavnagar', 'Amreli', 'Surendranagar', 'Anand']
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
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<'marketplace' | 'offers' | 'listings'>('marketplace')

  // Search state
  const [cropId, setCropId] = useState('crop_cotton')
  const [quantity, setQuantity] = useState('50')
  const [grade, setGrade] = useState('B')
  const [district, setDistrict] = useState('Ahmedabad')
  const [matches, setMatches] = useState<BuyerMatch[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [contactedId, setContactedId] = useState<string | null>(null)
  const [submittingId, setSubmittingId] = useState<string | null>(null)

  // Offers state
  const [offers, setOffers] = useState<any[]>([])
  const [offersLoading, setOffersLoading] = useState(false)

  // Buyer Listing creation state
  const [myListings, setMyListings] = useState<any[]>([])
  const [newCropId, setNewCropId] = useState('crop_cotton')
  const [minQty, setMinQty] = useState('10')
  const [maxQty, setMaxQty] = useState('100')
  const [offeredPrice, setOfferedPrice] = useState('7200')
  const [reqGrade, setReqGrade] = useState('B')
  const [delivDays, setDelivDays] = useState('3')
  const [pubDistrict, setPubDistrict] = useState('Ahmedabad')
  const [creatingListing, setCreatingListing] = useState(false)

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

  const loadOffers = async () => {
    setOffersLoading(true)
    try {
      const res = await buyerService.listOffers()
      setOffers(res.data || [])
    } catch (e) {
      console.error(e)
    } finally {
      setOffersLoading(false)
    }
  }

  const loadMyListings = async () => {
    try {
      const res = await buyerService.getMyListings()
      setMyListings(res.data || [])
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    search()
  }, [])

  useEffect(() => {
    if (activeTab === 'offers') loadOffers()
    if (activeTab === 'listings') loadMyListings()
  }, [activeTab])

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
      loadOffers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Could not contact buyer')
    } finally {
      setSubmittingId(null)
    }
  }

  const handleUpdateOfferStatus = async (offerId: string, status: string) => {
    try {
      await buyerService.updateOffer(offerId, status)
      toast.success(`Offer ${status}`)
      loadOffers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Action failed')
    }
  }

  const handleCreateListing = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreatingListing(true)
    try {
      await buyerService.createListing({
        crop_id: newCropId,
        min_quantity: parseFloat(minQty),
        max_quantity: parseFloat(maxQty),
        offered_price: parseFloat(offeredPrice),
        quality_requirement: reqGrade,
        district: pubDistrict,
        delivery_days: parseInt(delivDays),
      })
      toast.success('Buyer listing published!')
      loadMyListings()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create listing')
    } finally {
      setCreatingListing(false)
    }
  }

  const handleDeactivateListing = async (id: string) => {
    try {
      await buyerService.deleteListing(id)
      toast.success('Listing deactivated')
      loadMyListings()
    } catch (e) {
      toast.error('Failed to deactivate listing')
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-black">{t('buyers.title')}</h1>
          <p className="text-sm text-gray-500">Connect, trade, and manage crop orders seamlessly</p>
        </div>
        <div className="badge-demo">⚠ {t('common.demo_badge')}</div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('marketplace')}
          className={`flex items-center gap-2 px-4 py-2 font-semibold text-sm border-b-2 transition ${
            activeTab === 'marketplace' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <ShoppingBag size={16} /> Buyer Directory
        </button>
        <button
          onClick={() => setActiveTab('offers')}
          className={`flex items-center gap-2 px-4 py-2 font-semibold text-sm border-b-2 transition ${
            activeTab === 'offers' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Inbox size={16} /> Offer Inbox ({offers.length})
        </button>
        <button
          onClick={() => setActiveTab('listings')}
          className={`flex items-center gap-2 px-4 py-2 font-semibold text-sm border-b-2 transition ${
            activeTab === 'listings' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <PlusCircle size={16} /> Buyer Portal
        </button>
      </div>

      {/* Marketplace Tab */}
      {activeTab === 'marketplace' && (
        <>
          <div className="card card-hover anim-fade-in-up">
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
                <div key={m.listing_id} className={`card card-hover anim-fade-in-up ${i === 0 ? 'border-primary/40 bg-green-50/30' : ''}`} style={{animationDelay: `${i * 60}ms`}}>
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
                      className={`flex-1 py-2 rounded-xl text-sm font-semibold border transition-all hover:scale-[1.01] ${
                        contactedId === m.listing_id
                          ? 'bg-primary text-white border-primary'
                          : 'border-primary text-primary hover:bg-primary/5'
                      }`}
                    >
                      {submittingId === m.listing_id ? 'Sending...' : contactedId === m.listing_id ? '✓ Enquiry Sent' : t('buyers.contact_buyer')}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Offer Inbox Tab */}
      {activeTab === 'offers' && (
        <div className="space-y-3">
          {offersLoading ? (
            <div className="flex justify-center h-32 items-center"><Loader2 className="animate-spin text-primary" size={28} /></div>
          ) : offers.length === 0 ? (
            <div className="card text-center py-10 text-gray-400">No active offers or enquiries found</div>
          ) : (
            offers.map(o => (
              <div key={o.id} className="card flex items-center justify-between flex-wrap gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-gray-900">{o.quantity} quintals</span>
                    <span className="text-xs px-2 py-0.5 rounded-full font-semibold uppercase bg-blue-100 text-blue-800">
                      {o.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Offered Price: <span className="font-bold text-primary">{fmt(o.offered_price)}</span>/q</div>
                  {o.message && <div className="text-xs text-gray-500 italic mt-1">"{o.message}"</div>}
                  <div className="text-xs text-gray-400 mt-1">Created: {new Date(o.created_at).toLocaleDateString()}</div>
                </div>

                {o.status === 'pending' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleUpdateOfferStatus(o.id, 'accepted')}
                      className="px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-bold hover:bg-green-700 flex items-center gap-1"
                    >
                      <CheckCircle size={14} /> Accept
                    </button>
                    <button
                      onClick={() => handleUpdateOfferStatus(o.id, 'rejected')}
                      className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-bold hover:bg-red-700 flex items-center gap-1"
                    >
                      <XCircle size={14} /> Reject
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Buyer Portal Tab */}
      {activeTab === 'listings' && (
        <div className="space-y-5">
          <form onSubmit={handleCreateListing} className="card space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Publish New Buying Requirement</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="text-xs font-semibold text-gray-600">Crop</label>
                <select value={newCropId} onChange={e => setNewCropId(e.target.value)} className="select-field">
                  {CROPS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-600">Min Quantity (q)</label>
                <input type="number" value={minQty} onChange={e => setMinQty(e.target.value)} className="input-field" required />
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-600">Max Quantity (q)</label>
                <input type="number" value={maxQty} onChange={e => setMaxQty(e.target.value)} className="input-field" required />
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-600">Offered Price (₹/q)</label>
                <input type="number" value={offeredPrice} onChange={e => setOfferedPrice(e.target.value)} className="input-field" required />
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-600">Quality Required</label>
                <select value={reqGrade} onChange={e => setReqGrade(e.target.value)} className="select-field">
                  {GRADES.map(g => <option key={g} value={g}>Grade {g}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-600">District</label>
                <select value={pubDistrict} onChange={e => setPubDistrict(e.target.value)} className="select-field">
                  {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
            </div>
            <button type="submit" disabled={creatingListing} className="btn-primary w-full">
              {creatingListing ? 'Publishing...' : 'Publish Listing'}
            </button>
          </form>

          <div className="card space-y-3">
            <h2 className="text-lg font-bold text-gray-900">Your Active Buying Listings</h2>
            {myListings.length === 0 ? (
              <div className="text-gray-400 text-sm text-center py-6">No listings published yet</div>
            ) : (
              myListings.map(l => (
                <div key={l.id} className="flex items-center justify-between border-b pb-3 pt-1">
                  <div>
                    <div className="font-bold text-gray-800">{l.crop_name} ({l.min_quantity}-{l.max_quantity}q)</div>
                    <div className="text-xs text-gray-500">{l.district} • Grade {l.quality_requirement} • {fmt(l.offered_price)}/q</div>
                  </div>
                  {l.is_active && (
                    <button
                      onClick={() => handleDeactivateListing(l.id)}
                      className="px-3 py-1 bg-red-50 text-red-600 rounded-lg text-xs font-semibold hover:bg-red-100"
                    >
                      Deactivate
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
