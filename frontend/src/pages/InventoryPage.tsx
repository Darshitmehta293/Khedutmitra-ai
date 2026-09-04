import React, { useEffect, useState } from 'react'
import { farmerService, aiService } from '../services/api'
import { InventoryItem } from '../types'
import { Archive, Loader2, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

const CROPS = [
  { id: 'crop_cotton', label: 'Cotton' },
  { id: 'crop_groundnut', label: 'Groundnut' },
]

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({ crop_id: 'crop_cotton', quantity: '50', quality_grade: 'B', district: 'Ahmedabad', storage_available: true })

  const load = async () => {
    setLoading(true)
    try {
      const [inventory, history] = await Promise.all([farmerService.getInventory(), aiService.getRecommendationHistory()])
      setItems(inventory.data)
      setRecommendations(history.data.recommendations || [])
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Could not load inventory')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const addItem = async (event: React.FormEvent) => {
    event.preventDefault()
    const quantity = Number(form.quantity)
    if (!Number.isFinite(quantity) || quantity <= 0) return toast.error('Enter a valid quantity')
    setSaving(true)
    try {
      await farmerService.createInventory({ ...form, quantity })
      toast.success('Inventory lot added')
      setForm(f => ({ ...f, quantity: '' }))
      await load()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Could not add inventory')
    } finally {
      setSaving(false)
    }
  }

  const removeItem = async (id: string) => {
    try {
      await farmerService.deleteInventory(id)
      setItems(current => current.filter(item => item.id !== id))
      toast.success('Inventory lot archived')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Could not archive inventory')
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Archive className="text-primary" />
        <div><h1 className="text-2xl font-black">My Inventory</h1><p className="text-sm text-gray-500">Track lots and revisit your selling decisions.</p></div>
      </div>
      <form onSubmit={addItem} className="card">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <select className="select-field" value={form.crop_id} onChange={e => setForm({ ...form, crop_id: e.target.value })}>{CROPS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}</select>
          <input className="input-field" type="number" min="1" placeholder="Quantity (q)" value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} required />
          <select className="select-field" value={form.quality_grade} onChange={e => setForm({ ...form, quality_grade: e.target.value })}>{['A', 'B', 'C', 'ungraded'].map(g => <option key={g} value={g}>Grade {g.toUpperCase()}</option>)}</select>
          <input className="input-field" placeholder="District" value={form.district} onChange={e => setForm({ ...form, district: e.target.value })} />
        </div>
        <label className="flex items-center gap-2 mt-3 text-sm text-gray-600"><input type="checkbox" checked={form.storage_available} onChange={e => setForm({ ...form, storage_available: e.target.checked })} /> Storage available</label>
        <button className="btn-primary mt-4 flex items-center gap-2" disabled={saving}>{saving ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />} Add inventory lot</button>
      </form>
      {loading ? <div className="flex justify-center py-12"><Loader2 className="animate-spin text-primary" /></div> : <>
        <section className="space-y-3">
          <h2 className="font-bold">Active lots</h2>
          {items.length === 0 ? <div className="card text-sm text-gray-500">No inventory lots yet.</div> : items.map(item => <div className="card flex items-center justify-between gap-3" key={item.id}><div><div className="font-bold">{item.crop.name}</div><div className="text-sm text-gray-500">{item.quantity} quintals · Grade {item.quality_grade} · {item.district || 'District not set'}</div></div><button title="Archive lot" onClick={() => removeItem(item.id)} className="p-2 text-gray-400 hover:text-red-500"><Trash2 size={17} /></button></div>)}
        </section>
        <section className="space-y-3"><h2 className="font-bold">Recommendation history</h2>{recommendations.length === 0 ? <div className="card text-sm text-gray-500">Your saved recommendations will appear here.</div> : recommendations.map(item => <div className="card" key={item.id}><div className="flex justify-between"><strong>{item.action.replace('_', ' ')}</strong><span className="text-xs text-gray-400">{new Date(item.created_at).toLocaleDateString()}</span></div><div className="text-sm text-gray-600 mt-1">Net revenue ₹{item.expected_net_revenue.toLocaleString('en-IN')} · Potential gain ₹{item.potential_gain.toLocaleString('en-IN')}</div><p className="text-sm text-gray-500 mt-2">{item.explanation}</p></div>)}</section>
      </>}
    </div>
  )
}
