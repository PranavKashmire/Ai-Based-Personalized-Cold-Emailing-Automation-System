import { useCampaign } from '../store/CampaignStore'
import { Users, CheckCircle2, XCircle, Clock, TrendingUp } from 'lucide-react'
import clsx from 'clsx'

const cards = [
  {
    key: 'total',
    label: 'Total Leads',
    icon: Users,
    color: 'brand',
    bg: 'bg-brand-500/10',
    iconColor: 'text-brand-400',
    border: 'border-brand-500/20',
    trend: null,
  },
  {
    key: 'sent',
    label: 'Emails Sent',
    icon: CheckCircle2,
    color: 'emerald',
    bg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-400',
    border: 'border-emerald-500/20',
  },
  {
    key: 'pending',
    label: 'Pending',
    icon: Clock,
    color: 'amber',
    bg: 'bg-amber-500/10',
    iconColor: 'text-amber-400',
    border: 'border-amber-500/20',
  },
  {
    key: 'failed',
    label: 'Failed',
    icon: XCircle,
    color: 'red',
    bg: 'bg-red-500/10',
    iconColor: 'text-red-400',
    border: 'border-red-500/20',
  },
]

function StatCard({ label, value, icon: Icon, bg, iconColor, border, total }) {
  const pct = total > 0 && label !== 'Total Leads' ? Math.round((value / total) * 100) : null

  return (
    <div className={clsx('stat-card border', border, 'animate-fade-in')}>
      <div className="flex items-start justify-between">
        <div className={clsx('w-10 h-10 rounded-xl flex items-center justify-center', bg)}>
          <Icon size={19} className={iconColor} />
        </div>
        {pct !== null && (
          <span className={clsx('text-xs font-semibold px-2 py-0.5 rounded-full', bg, iconColor)}>
            {pct}%
          </span>
        )}
      </div>
      <div>
        <p className="text-3xl font-extrabold text-white tabular-nums">{value.toLocaleString()}</p>
        <p className="text-sm text-gray-500 mt-0.5">{label}</p>
      </div>
      {label !== 'Total Leads' && total > 0 && (
        <div className="mt-1">
          <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
            <div
              className={clsx('h-full rounded-full transition-all duration-700', bg.replace('/10', '/80'))}
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default function StatCards() {
  const { state: { stats } } = useCampaign()
  return (
    <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
      {cards.map(c => (
        <StatCard key={c.key} {...c} value={stats[c.key] ?? 0} total={stats.total} />
      ))}
    </div>
  )
}
