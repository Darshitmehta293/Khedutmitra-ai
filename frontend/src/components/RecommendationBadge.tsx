import React from 'react'
import { RecommendationAction } from '../types'

interface Props {
  action: RecommendationAction
  days?: number | null
  size?: 'sm' | 'lg'
}

const CONFIGS = {
  SELL_NOW: { label: 'SELL NOW', labelGu: 'અત્યારે વેચો', bg: 'bg-red-500', ring: 'ring-red-200' },
  STORE:    { label: 'STORE',    labelGu: 'સ્ટોર કરો',    bg: 'bg-primary', ring: 'ring-green-200' },
  WAIT:     { label: 'WAIT',     labelGu: 'રાહ જુઓ',      bg: 'bg-amber-500', ring: 'ring-amber-200' },
}

export default function RecommendationBadge({ action, days, size = 'sm' }: Props) {
  const cfg = CONFIGS[action]
  return (
    <div className={`inline-flex flex-col items-center gap-0.5 ${cfg.bg} text-white rounded-2xl ring-4 ${cfg.ring} ${size === 'lg' ? 'px-8 py-4' : 'px-5 py-2'}`}>
      <span className={`font-black tracking-wider ${size === 'lg' ? 'text-2xl' : 'text-base'}`}>{cfg.label}</span>
      {action === 'STORE' && days && (
        <span className={`font-medium opacity-90 ${size === 'lg' ? 'text-base' : 'text-xs'}`}>FOR {days} DAYS</span>
      )}
    </div>
  )
}
