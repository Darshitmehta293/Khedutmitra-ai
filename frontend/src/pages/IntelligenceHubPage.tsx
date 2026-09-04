import React, { useEffect, useState } from 'react'
import { intelligenceService } from '../services/api'
import { Bell, CloudRain, IndianRupee, Mic, Truck, Warehouse, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

const crop = 'crop_cotton'
const money = (value: number) => `₹${Number(value || 0).toLocaleString('en-IN')}`

export default function IntelligenceHubPage() {
  const [weather, setWeather] = useState<any>(null)
  const [mandis, setMandis] = useState<any>(null)
  const [demand, setDemand] = useState<any>(null)
  const [profit, setProfit] = useState<any>(null)
  const [risk, setRisk] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [alertPrice, setAlertPrice] = useState('7200')
  const [expense, setExpense] = useState({ category: 'fertilizer', amount: '' })
  const [negotiation, setNegotiation] = useState<any>(null)

  const load = async () => {
    setLoading(true)
    try {
      const results = await Promise.all([
        intelligenceService.weather('Ahmedabad'), intelligenceService.mandiComparison(crop, 50, 'Ahmedabad'),
        intelligenceService.demand(crop), intelligenceService.getProfit(), intelligenceService.getRisk(crop, 'Ahmedabad'),
      ])
      setWeather(results[0].data); setMandis(results[1].data); setDemand(results[2].data); setProfit(results[3].data); setRisk(results[4].data)
    } catch (error: any) { toast.error(error.response?.data?.detail || 'Could not load intelligence') } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const createAlert = async (event: React.FormEvent) => {
    event.preventDefault()
    try { await intelligenceService.createAlert({ crop_id: crop, threshold_price: Number(alertPrice), direction: 'above' }); toast.success('Price alert created') } catch { toast.error('Could not create alert') }
  }
  const addExpense = async (event: React.FormEvent) => {
    event.preventDefault()
    try { await intelligenceService.createExpense({ ...expense, amount: Number(expense.amount), crop_id: crop }); toast.success('Expense recorded'); setExpense({ ...expense, amount: '' }); await load() } catch { toast.error('Could not record expense') }
  }
  const negotiate = async () => {
    try { const result = await intelligenceService.negotiate({ crop_id: crop, offered_price: mandis?.markets?.[0]?.modal_price || 7000 }); setNegotiation(result.data) } catch { toast.error('Negotiation analysis unavailable') }
  }
  const voiceInput = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) return toast.error('Voice input is not supported in this browser')
    const recognition = new SpeechRecognition(); recognition.lang = 'gu-IN'; recognition.onresult = (event: any) => toast.success(`Heard: ${event.results[0][0].transcript}`); recognition.start()
  }

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin text-primary" /></div>
  return <div className="space-y-5">
    <div className="flex items-center justify-between gap-3"><div><h1 className="text-2xl font-black">Farmer Intelligence Hub</h1><p className="text-sm text-gray-500">Weather, demand, true market value, costs, alerts and financial clarity.</p></div><button title="Gujarati voice input" onClick={voiceInput} className="p-3 rounded-full bg-primary text-white"><Mic size={19} /></button></div>
    <div className="grid md:grid-cols-3 gap-4">
      <section className="card"><div className="flex items-center gap-2 font-bold"><CloudRain className="text-primary" size={18} /> Weather</div><div className="mt-3 text-sm">{weather?.forecast?.slice(0, 3).map((day: any) => <div className="flex justify-between py-1" key={day.date}><span>{day.date}</span><span>{day.temperature_c}°C · {day.rainfall_mm}mm</span></div>)}</div><p className="text-xs text-amber-600 mt-2">{weather?.forecast?.[0]?.alert}</p></section>
      <section className="card"><div className="font-bold">Demand outlook</div><div className="text-3xl font-black text-primary mt-3">{demand?.current_demand_index}/100</div><p className="text-sm text-gray-500">{demand?.outlook} · peak window {demand?.peak_window_days} days</p><div className="text-sm mt-2">Signal: {money(demand?.expected_price_signal)}/q</div></section>
      <section className="card"><div className="flex items-center gap-2 font-bold"><IndianRupee className="text-primary" size={18} /> Estimated profit</div><div className="text-2xl font-black mt-3">{money(profit?.estimated_profit)}</div><p className="text-sm text-gray-500">Revenue {money(profit?.estimated_revenue)} · Expenses {money(profit?.expenses)}</p></section>
    </div>
    <section className="card"><div className="flex items-center gap-2 font-bold"><Truck className="text-primary" size={18} /> Mandi comparison after transport</div><div className="overflow-x-auto mt-3"><table className="w-full text-sm"><thead><tr className="text-left text-gray-500"><th className="py-2">Market</th><th>Price</th><th>Transport</th><th>True net</th></tr></thead><tbody>{mandis?.markets?.map((market: any) => <tr className="border-t border-gray-100" key={market.market_id}><td className="py-2">{market.market_name}</td><td>{money(market.modal_price)}</td><td>{money(market.transport_cost)}</td><td className="font-bold text-primary">{money(market.net_revenue)}</td></tr>)}</tbody></table></div></section>
    <div className="grid md:grid-cols-2 gap-4">
      <section className="card"><div className="flex items-center gap-2 font-bold"><Warehouse className="text-primary" size={18} /> Storage and negotiation</div><p className="text-sm text-gray-500 mt-2">Compare nearby warehouses and prepare a fair asking price.</p><div className="flex gap-2 mt-3"><button onClick={negotiate} className="btn-primary">Suggest negotiation range</button></div>{negotiation && <div className="mt-3 text-sm">Ask {money(negotiation.asking_price)} · Walk away {money(negotiation.walk_away_price)}<p className="text-gray-500 mt-1">{negotiation.talking_points.join(' · ')}</p></div>}</section>
      <section className="card"><div className="flex items-center gap-2 font-bold"><Bell className="text-primary" size={18} /> Price alert</div><form onSubmit={createAlert} className="flex gap-2 mt-3"><input className="input-field" type="number" value={alertPrice} onChange={e => setAlertPrice(e.target.value)} /><button className="btn-primary">Create alert</button></form><p className="text-xs text-gray-500 mt-2">In-app alert for cotton above your threshold.</p></section>
    </div>
    <div className="grid md:grid-cols-2 gap-4"><section className="card"><h2 className="font-bold">Record an expense</h2><form onSubmit={addExpense} className="flex gap-2 mt-3"><select className="select-field" value={expense.category} onChange={e => setExpense({ ...expense, category: e.target.value })}>{['seeds', 'fertilizer', 'labour', 'irrigation', 'harvesting', 'other'].map(item => <option key={item}>{item}</option>)}</select><input className="input-field" type="number" placeholder="Amount" value={expense.amount} onChange={e => setExpense({ ...expense, amount: e.target.value })} required /><button className="btn-primary">Save</button></form></section><section className="card"><h2 className="font-bold">Risk advisor</h2>{risk?.risks?.map((item: any) => <div className="mt-2 text-sm" key={item.name}><span className="font-semibold">{item.name}</span> <span className="text-amber-600">{item.level}</span><div className="text-gray-500">{item.mitigation}</div></div>)}</section></div>
    <p className="text-xs text-gray-400">Intelligence marked demo uses deterministic local data until live weather, market, transport and government providers are configured.</p>
  </div>
}
