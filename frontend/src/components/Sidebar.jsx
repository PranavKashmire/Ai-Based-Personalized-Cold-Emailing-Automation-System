import { useCampaign } from '../store/CampaignStore'
import {
  LayoutDashboard, Upload, Send, BarChart3, Settings,
  Zap, Mail, ChevronRight
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { id: 'leads',    icon: LayoutDashboard, label: 'Leads',     badge: null },
  { id: 'campaign', icon: Send,            label: 'Campaign',  badge: null },
  { id: 'analytics',icon: BarChart3,       label: 'Analytics', badge: null },
]

export default function Sidebar({ onImportClick }) {
  const { state, dispatch } = useCampaign()
  const { view, stats, campaign } = state

  return (
    <aside className="w-64 flex-shrink-0 h-screen bg-gray-950 border-r border-gray-800/60 flex flex-col">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-800/60">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center shadow-lg shadow-brand-500/30">
            <Zap size={18} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-white tracking-tight">OutreachAI</p>
            <p className="text-xs text-gray-500">GTM Campaign Engine</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => dispatch({ type: 'SET_VIEW', payload: id })}
            className={clsx('nav-item w-full text-left', view === id ? 'nav-item-active' : 'nav-item-inactive')}
          >
            <Icon size={17} />
            <span className="flex-1">{label}</span>
            {view === id && <ChevronRight size={14} className="opacity-50" />}
          </button>
        ))}

        <div className="pt-3 border-t border-gray-800/60 mt-3">
          <button
            onClick={onImportClick}
            className="nav-item w-full text-left nav-item-inactive"
          >
            <Upload size={17} />
            <span>Import CSV</span>
          </button>
        </div>
      </nav>

      {/* Campaign Status pill */}
      <div className="px-3 pb-4">
        <div className="glass-card p-3.5 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500 font-medium">Campaign Status</span>
            <span className={clsx(
              'status-badge',
              campaign.status === 'running'  && 'bg-emerald-500/15 text-emerald-400',
              campaign.status === 'paused'   && 'bg-amber-500/15 text-amber-400',
              campaign.status === 'done'     && 'bg-brand-500/15 text-brand-400',
              campaign.status === 'idle'     && 'bg-gray-700/50 text-gray-400',
            )}>
              <span className={clsx(
                'w-1.5 h-1.5 rounded-full',
                campaign.status === 'running' && 'bg-emerald-400 animate-pulse',
                campaign.status === 'paused'  && 'bg-amber-400',
                campaign.status === 'done'    && 'bg-brand-400',
                campaign.status === 'idle'    && 'bg-gray-500',
              )} />
              {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
            </span>
          </div>
          {stats.total > 0 && (
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-gray-500">
                <span>{stats.sent} sent</span>
                <span>{stats.total} total</span>
              </div>
              <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500 progress-bar-animated"
                  style={{ width: `${stats.total ? (stats.sent / stats.total) * 100 : 0}%` }}
                />
              </div>
            </div>
          )}
          <div className="grid grid-cols-2 gap-2 pt-0.5">
            <div className="text-center p-2 bg-gray-800/50 rounded-lg">
              <p className="text-lg font-bold text-white">{stats.sent}</p>
              <p className="text-[10px] text-gray-500">Sent</p>
            </div>
            <div className="text-center p-2 bg-gray-800/50 rounded-lg">
              <p className="text-lg font-bold text-white">{stats.failed}</p>
              <p className="text-[10px] text-gray-500">Failed</p>
            </div>
          </div>
        </div>
      </div>

      {/* User footer */}
      <div className="px-3 pb-4 border-t border-gray-800/60 pt-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
            PK
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-200 truncate">Pranav Kashmire</p>
            <p className="text-xs text-gray-500 truncate">GTM Engineer</p>
          </div>
          <Settings size={15} className="text-gray-600 cursor-pointer hover:text-gray-400 transition-colors" />
        </div>
      </div>
    </aside>
  )
}
