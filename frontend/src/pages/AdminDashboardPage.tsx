import React, { useEffect, useState } from 'react'
import { intelligenceService, adminService } from '../services/api'
import { ShieldCheck, Users, ShoppingBag, Activity, Database, CheckCircle } from 'lucide-react'

export default function AdminDashboardPage() {
  const [analytics, setAnalytics] = useState<any>(null)
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      intelligenceService.getAdminAnalytics().then(r => setAnalytics(r.data)).catch(console.error),
      adminService.getHealth().then(r => setHealth(r.data)).catch(console.error),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="p-8 text-center text-gray-400">Loading admin analytics...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
            <ShieldCheck className="text-primary" /> Admin Control Center
          </h1>
          <p className="text-sm text-gray-500">Platform performance, system health, and analytics</p>
        </div>
        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold flex items-center gap-1">
          <CheckCircle size={14} /> System Healthy
        </span>
      </div>

      {/* Analytics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
            <Users size={16} /> Total Registered Users
          </div>
          <div className="text-2xl font-black text-gray-900">{analytics?.users ?? 0}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
            <ShoppingBag size={16} /> Total Marketplace Offers
          </div>
          <div className="text-2xl font-black text-primary">{analytics?.offers ?? 0}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
            <Activity size={16} /> Tracked Expenses (₹)
          </div>
          <div className="text-2xl font-black text-gray-900">₹{(analytics?.tracked_expenses ?? 0).toLocaleString('en-IN')}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
            <Database size={16} /> Database Driver
          </div>
          <div className="text-lg font-bold text-gray-800 capitalize">{health?.database || 'SQLite / PostgreSQL'}</div>
        </div>
      </div>

      {/* AI Agents Status */}
      <div className="card space-y-3">
        <h2 className="font-bold text-gray-900">Agent Performance & Orchestration</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {Object.entries(analytics?.agent_performance || {}).map(([agent, status]) => (
            <div key={agent} className="p-3 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-between">
              <span className="font-semibold text-gray-700 capitalize">{agent} Agent</span>
              <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-bold capitalize">
                {String(status)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
