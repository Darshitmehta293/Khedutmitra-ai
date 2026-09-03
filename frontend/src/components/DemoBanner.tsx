import React from 'react'
import { AlertTriangle } from 'lucide-react'

export default function DemoBanner() {
  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center gap-2 text-amber-800 text-xs">
      <AlertTriangle size={13} />
      <span className="font-semibold">DEMO MODE</span>
      <span>— All market data is simulated for demonstration. Not live prices.</span>
    </div>
  )
}
