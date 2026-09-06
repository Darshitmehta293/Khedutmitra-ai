import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { farmerService, intelligenceService } from '../services/api'
import { DashboardData } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts'
import { Loader2, TrendingUp, DollarSign, Trash2, Plus } from 'lucide-react'
import toast from 'react-hot-toast'

const fmt = (n: number) => `₹${n.toLocaleString('en-IN')}`

const EXPENSE_CATEGORIES = ['Seed', 'Fertilizer', 'Pesticide', 'Irrigation', 'Labor', 'Transport', 'Storage', 'Other']

export default function IncomePage() {
  const { t } = useTranslation()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  // Expense state
  const [expenses, setExpenses] = useState<any[]>([])
  const [category, setCategory] = useState('Seed')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')
  const [addingExpense, setAddingExpense] = useState(false)

  const loadExpenses = async () => {
    try {
      const res = await intelligenceService.getExpenses()
      setExpenses(res.data || [])
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    Promise.all([
      farmerService.getDashboard().then(r => setData(r.data)),
      loadExpenses(),
    ]).finally(() => setLoading(false))
  }, [])

  const handleAddExpense = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!amount || parseFloat(amount) <= 0) {
      toast.error('Enter a valid amount')
      return
    }
    setAddingExpense(true)
    try {
      await intelligenceService.createExpense({ category, amount: parseFloat(amount), notes })
      toast.success('Expense recorded')
      setAmount('')
      setNotes('')
      loadExpenses()
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Failed to add expense')
    } finally {
      setAddingExpense(false)
    }
  }

  const handleDeleteExpense = async (id: string) => {
    try {
      await intelligenceService.deleteExpense(id)
      toast.success('Expense removed')
      loadExpenses()
    } catch (e) {
      toast.error('Failed to remove expense')
    }
  }

  if (loading) return <div className="flex justify-center h-40 items-center"><Loader2 className="animate-spin text-primary" size={28} /></div>

  const totalExpenses = expenses.reduce((sum, e) => sum + (e.amount || 0), 0)
  const estVal = data?.current_estimated_value || 0
  const netProfit = estVal - totalExpenses

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
          { label: t('income.current_value'), val: fmt(estVal), color: 'text-gray-900' },
          { label: 'Total Expenses', val: fmt(totalExpenses), color: 'text-red-600' },
          { label: 'Estimated Net Profit', val: fmt(netProfit), color: netProfit >= 0 ? 'text-primary' : 'text-red-600' },
          { label: 'Inventory', val: `${data?.total_inventory_quintals || 0}q`, color: 'text-gray-700' },
        ].map(({ label, val, color }) => (
          <div key={label} className="card">
            <div className="text-xs text-gray-500 mb-1">{label}</div>
            <div className={`text-xl font-black ${color}`}>{val}</div>
          </div>
        ))}
      </div>

      {/* Add Expense & History */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <form onSubmit={handleAddExpense} className="card space-y-3">
          <h2 className="font-bold text-gray-900 flex items-center gap-2">
            <DollarSign size={18} className="text-primary" /> Log Farm Expense
          </h2>
          <div>
            <label className="text-xs text-gray-600 font-medium">Category</label>
            <select value={category} onChange={e => setCategory(e.target.value)} className="select-field">
              {EXPENSE_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-600 font-medium">Amount (₹)</label>
            <input type="number" value={amount} onChange={e => setAmount(e.target.value)} className="input-field" placeholder="e.g. 2500" required />
          </div>
          <div>
            <label className="text-xs text-gray-600 font-medium">Notes (optional)</label>
            <input type="text" value={notes} onChange={e => setNotes(e.target.value)} className="input-field" placeholder="Details or vendor" />
          </div>
          <button type="submit" disabled={addingExpense} className="btn-primary w-full flex items-center justify-center gap-1">
            <Plus size={16} /> Add Expense
          </button>
        </form>

        <div className="card space-y-3">
          <h2 className="font-bold text-gray-900">Expense History</h2>
          {expenses.length === 0 ? (
            <div className="text-xs text-gray-400 text-center py-8">No expenses logged yet</div>
          ) : (
            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {expenses.map(e => (
                <div key={e.id} className="flex items-center justify-between border-b pb-2 pt-1 text-sm">
                  <div>
                    <div className="font-bold text-gray-800">{e.category}</div>
                    {e.notes && <div className="text-xs text-gray-400">{e.notes}</div>}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-red-600">{fmt(e.amount)}</span>
                    <button onClick={() => handleDeleteExpense(e.id)} className="text-gray-400 hover:text-red-600 transition">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
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
        </div>
      )}
    </div>
  )
}
