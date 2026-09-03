import React, { useEffect, useState } from 'react'
import { CalendarDays, Check, ClipboardList, Droplets, Plus, Sprout, Trash2 } from 'lucide-react'

const CROPS = [
  { id: 'cotton', name: 'Cotton', duration: 170, color: 'bg-amber-500' },
  { id: 'groundnut', name: 'Groundnut', duration: 110, color: 'bg-emerald-600' },
]

type Task = { id: string; title: string; timing: string; detail: string; done: boolean }

type Plan = { crop: string; area: string; sowingDate: string; tasks: Task[] }

function buildTasks(crop: typeof CROPS[number], sowingDate: string): Task[] {
  const start = new Date(sowingDate)
  const milestones: Array<[string, number, string]> = crop.id === 'cotton'
    ? [
        ['Land preparation', 0, 'Prepare soil and confirm seed quality before sowing.'],
        ['First irrigation check', 25, 'Inspect moisture and clear blocked irrigation lines.'],
        ['Weed management', 45, 'Walk the field and remove early weed pressure.'],
        ['Pest scouting', 70, 'Check leaves and buds twice this week for pest signs.'],
        ['Harvest readiness', 145, 'Check boll opening and arrange labour or buyer contact.'],
      ]
    : [
        ['Land preparation', 0, 'Prepare a fine seedbed and confirm seed quality.'],
        ['First irrigation check', 18, 'Inspect emergence and maintain even moisture.'],
        ['Weed management', 30, 'Remove weeds before they compete with young plants.'],
        ['Flowering check', 55, 'Monitor crop health and avoid water stress.'],
        ['Harvest readiness', 90, 'Check pod maturity and plan drying space.'],
      ]

  return milestones.map(([title, days, detail]) => {
    const date = new Date(start)
    date.setDate(date.getDate() + Number(days))
    return { id: `${crop.id}-${days}`, title, timing: date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }), detail, done: false }
  })
}

export default function FarmPlannerPage() {
  const [cropId, setCropId] = useState('cotton')
  const [area, setArea] = useState('')
  const [sowingDate, setSowingDate] = useState(new Date().toISOString().slice(0, 10))
  const [plan, setPlan] = useState<Plan | null>(null)
  const crop = CROPS.find(item => item.id === cropId) || CROPS[0]

  useEffect(() => {
    try {
      const stored = localStorage.getItem('km_farm_plan')
      if (stored) setPlan(JSON.parse(stored))
    } catch {
      localStorage.removeItem('km_farm_plan')
    }
  }, [])

  const savePlan = (nextPlan: Plan | null) => {
    setPlan(nextPlan)
    if (nextPlan) localStorage.setItem('km_farm_plan', JSON.stringify(nextPlan))
    else localStorage.removeItem('km_farm_plan')
  }

  const generatePlan = () => savePlan({ crop: crop.name, area, sowingDate, tasks: buildTasks(crop, sowingDate) })
  const toggleTask = (id: string) => {
    if (!plan) return
    savePlan({ ...plan, tasks: plan.tasks.map(task => task.id === id ? { ...task, done: !task.done } : task) })
  }
  const completed = plan?.tasks.filter(task => task.done).length || 0
  const progress = plan ? Math.round((completed / plan.tasks.length) * 100) : 0

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-3 border-b border-gray-200/80 pb-5">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-primary/70 mb-2">Field operations</div>
          <h1 className="text-3xl font-black">Farm Planner<span className="text-primary">.</span></h1>
          <p className="text-sm text-gray-500 mt-1">Turn a sowing date into a simple field checklist.</p>
        </div>
        <div className="rounded-lg bg-primary/10 p-2.5 text-primary"><CalendarDays size={21} /></div>
      </div>

      <section className="card bg-gradient-to-br from-[#eff8ef] via-white to-[#fff8e8] border-primary/15">
        <div className="flex items-center gap-2 mb-4"><Sprout size={17} className="text-primary" /><h2 className="font-semibold">Start a crop plan</h2></div>
        <div className="grid gap-3 md:grid-cols-3">
          <label className="text-sm font-medium text-gray-700">Crop<select value={cropId} onChange={event => setCropId(event.target.value)} className="select-field mt-1.5">{CROPS.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label className="text-sm font-medium text-gray-700">Area (acres)<input value={area} onChange={event => setArea(event.target.value)} type="number" min="0" step="0.1" placeholder="e.g. 4.5" className="input-field mt-1.5" /></label>
          <label className="text-sm font-medium text-gray-700">Sowing date<input value={sowingDate} onChange={event => setSowingDate(event.target.value)} type="date" className="input-field mt-1.5" /></label>
        </div>
        <button onClick={generatePlan} className="btn-primary mt-4 inline-flex items-center gap-2"><Plus size={16} /> Generate plan</button>
      </section>

      {plan ? <>
        <section className="card">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div><div className="text-xs font-semibold uppercase tracking-[0.14em] text-gray-400">Active plan</div><h2 className="text-xl font-bold mt-1">{plan.crop} {plan.area && <span className="text-gray-400 font-normal">· {plan.area} acres</span>}</h2><p className="text-sm text-gray-500 mt-1">Sown {new Date(plan.sowingDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })} · {crop.duration}-day cycle</p></div>
            <button onClick={() => savePlan(null)} className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-red-500"><Trash2 size={14} /> Clear plan</button>
          </div>
          <div className="mt-5"><div className="flex justify-between text-xs font-semibold text-gray-500 mb-1.5"><span>Season progress</span><span>{completed}/{plan.tasks.length} complete</span></div><div className="h-2 rounded-full bg-gray-100 overflow-hidden"><div className="h-full bg-primary transition-all" style={{ width: `${progress}%` }} /></div></div>
        </section>

        <section className="space-y-3">
          {plan.tasks.map((task, index) => <button key={task.id} onClick={() => toggleTask(task.id)} className={`card w-full text-left flex items-start gap-3 transition-colors ${task.done ? 'bg-primary/[.04] border-primary/20' : 'hover:border-primary/30'}`}><span className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border ${task.done ? 'border-primary bg-primary text-white' : 'border-gray-300 text-gray-400'}`}>{task.done ? <Check size={15} /> : <span className="text-xs font-bold">{index + 1}</span>}</span><span className="flex-1"><span className={`flex items-center justify-between gap-3 font-semibold ${task.done ? 'text-primary line-through' : 'text-gray-900'}`}><span>{task.title}</span><span className="text-xs font-medium text-gray-400 no-underline">{task.timing}</span></span><span className="mt-1 block text-xs leading-relaxed text-gray-500">{task.detail}</span></span></button>)}
        </section>
      </> : <section className="card py-12 text-center"><ClipboardList size={28} className="mx-auto text-primary/40" /><h2 className="font-semibold mt-3">No active plan yet</h2><p className="text-sm text-gray-500 mt-1">Create a plan to keep field work visible and on time.</p></section>}

      <div className="flex items-center gap-2 rounded-lg border border-blue-100 bg-blue-50 px-3 py-2.5 text-xs text-blue-800"><Droplets size={14} /> Planning guidance is indicative. Confirm irrigation and pest decisions locally.</div>
    </div>
  )
}
