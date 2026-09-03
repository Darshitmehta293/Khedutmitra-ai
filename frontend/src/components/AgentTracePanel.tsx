import React from 'react'
import { AgentTrace } from '../types'
import { CheckCircle, XCircle, Clock } from 'lucide-react'

interface Props { trace: AgentTrace[]; loading?: boolean }

export default function AgentTracePanel({ trace, loading }: Props) {
  return (
    <div className="card mt-4">
      <div className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <Clock size={15} className="text-primary" />
        AI Agent Analysis
      </div>
      <div className="space-y-2">
        {loading && (
          <div className="flex items-center gap-2 text-sm text-gray-400 animate-pulse">
            <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin" />
            Running agents...
          </div>
        )}
        {trace.map((t, i) => (
          <div key={i} className="flex items-start gap-2.5 text-sm">
            {t.status.startsWith('✓') ? (
              <CheckCircle size={15} className="text-green-500 mt-0.5 flex-shrink-0" />
            ) : (
              <XCircle size={15} className="text-red-400 mt-0.5 flex-shrink-0" />
            )}
            <div className="flex-1">
              <span className="text-gray-700">{t.label || t.agent}</span>
              {t.latency_ms ? (
                <span className="ml-2 text-xs text-gray-400">{t.latency_ms.toFixed(0)}ms</span>
              ) : null}
              {t.error && <div className="text-xs text-red-400 mt-0.5">{t.error}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
