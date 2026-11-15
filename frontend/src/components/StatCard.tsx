import type { ReactNode } from 'react'
import clsx from 'clsx'

interface Props {
  title: string
  value: string | number
  subtitle?: string
  icon?: ReactNode
  accent?: 'blue' | 'green' | 'yellow' | 'purple'
}

const accentMap = {
  blue: 'text-blue-400',
  green: 'text-green-400',
  yellow: 'text-yellow-400',
  purple: 'text-purple-400',
}

export default function StatCard({ title, value, subtitle, icon, accent = 'blue' }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs text-gray-500 uppercase tracking-wider">{title}</span>
        {icon && <span className={clsx('opacity-70', accentMap[accent])}>{icon}</span>}
      </div>
      <p className={clsx('text-3xl font-bold', accentMap[accent])}>{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  )
}
