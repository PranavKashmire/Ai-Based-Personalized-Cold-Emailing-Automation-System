import { useState, useRef, useCallback } from 'react'
import { useCampaign } from '../store/CampaignStore'
import {
  Search, Filter, Send, ChevronUp, ChevronDown,
  ExternalLink, Mail, Building2, Tag, Clock, CheckCircle2, XCircle,
  Loader2, MoreHorizontal
} from 'lucide-react'
import clsx from 'clsx'
import toast from 'react-hot-toast'

const STATUS_CONFIG = {
  pending: { label: 'Pending', icon: Clock,        className: 'bg-amber-500/10  text-amber-400  border-amber-500/20' },
  sending: { label: 'Sending', icon: Loader2,       className: 'bg-brand-500/10  text-brand-400  border-brand-500/20' },
  sent:    { label: 'Sent',    icon: CheckCircle2,  className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
  failed:  { label: 'Failed',  icon: XCircle,       className: 'bg-red-500/10    text-red-400    border-red-500/20' },
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.pending
  const Icon = cfg.icon
  return (
    <span className={clsx('status-badge border', cfg.className)}>
      <Icon size={11} className={status === 'sending' ? 'animate-spin' : ''} />
      {cfg.label}
    </span>
  )
}

function simulateSend() {
  return new Promise((resolve) => {
    const delay = 1500 + Math.random() * 1000
    setTimeout(() => {
      resolve(true) // 100% success rate for the demo
    }, delay)
  })
}

export default function LeadsTable() {
  const { state, dispatch } = useCampaign()
  const { leads, searchQuery, statusFilter } = state
  const [sortField, setSortField] = useState('name')
  const [sortDir, setSortDir] = useState('asc')
  const [sendingIds, setSendingIds] = useState(new Set())
  const [emailModal, setEmailModal] = useState(null)

  // Filter + sort
  const filtered = leads
    .filter(l => {
      const q = searchQuery.toLowerCase()
      const matchQ = !q || l.name.toLowerCase().includes(q) || l.email.toLowerCase().includes(q) || l.company.toLowerCase().includes(q)
      const matchS = statusFilter === 'all' || l.status === statusFilter
      return matchQ && matchS
    })
    .sort((a, b) => {
      const va = (a[sortField] || '').toString().toLowerCase()
      const vb = (b[sortField] || '').toString().toLowerCase()
      return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va)
    })

  const toggleSort = (field) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortField(field); setSortDir('asc') }
  }

  const handleManualSend = async (lead) => {
    if (lead.status === 'sent' || sendingIds.has(lead.id)) return
    setSendingIds(prev => new Set(prev).add(lead.id))
    dispatch({ type: 'SET_LEAD_STATUS', payload: { id: lead.id, status: 'sending' } })

    const toastId = toast.loading(`Sending to ${lead.email}...`)
    const success = await simulateSend()

    setSendingIds(prev => { const s = new Set(prev); s.delete(lead.id); return s })
    dispatch({ type: 'SET_LEAD_STATUS', payload: { id: lead.id, status: success ? 'sent' : 'failed', errorMsg: success ? null : 'SMTP timeout' } })

    if (success) toast.success(`Email sent to ${lead.name}!`, { id: toastId })
    else toast.error(`Failed to reach ${lead.email}`, { id: toastId })
  }

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <ChevronUp size={12} className="opacity-20" />
    return sortDir === 'asc' ? <ChevronUp size={12} className="text-brand-400" /> : <ChevronDown size={12} className="text-brand-400" />
  }

  if (leads.length === 0) {
    return (
      <div className="glass-card border border-gray-800/60 flex flex-col items-center justify-center py-20 text-center">
        <div className="w-16 h-16 rounded-2xl bg-gray-800/80 flex items-center justify-center mb-4">
          <Mail size={28} className="text-gray-600" />
        </div>
        <p className="text-lg font-semibold text-gray-300">No leads yet</p>
        <p className="text-sm text-gray-600 mt-1">Import a CSV or load demo data to get started</p>
      </div>
    )
  }

  return (
    <div className="glass-card border border-gray-800/60 overflow-hidden animate-fade-in">
      {/* Table header controls */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-gray-800/60">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search leads..."
            value={searchQuery}
            onChange={e => dispatch({ type: 'SET_SEARCH', payload: e.target.value })}
            className="w-full pl-9 pr-4 py-2 bg-gray-800/60 border border-gray-700/60 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/20 transition-all"
          />
        </div>

        {/* Status filter */}
        <div className="flex items-center gap-1 bg-gray-800/60 rounded-lg p-1 border border-gray-700/40">
          {['all', 'pending', 'sent', 'failed'].map(s => (
            <button
              key={s}
              onClick={() => dispatch({ type: 'SET_STATUS_FILTER', payload: s })}
              className={clsx(
                'px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-150',
                statusFilter === s
                  ? 'bg-gray-700 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-300'
              )}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        <span className="text-xs text-gray-600 ml-auto">{filtered.length} leads</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-800/60 bg-gray-900/50">
              {[
                { key: 'name',    label: 'Lead' },
                { key: 'company', label: 'Company' },
                { key: 'niche',   label: 'Niche' },
                { key: 'email',   label: 'Email' },
                { key: 'status',  label: 'Status' },
                { key: 'sentAt',  label: 'Sent At' },
              ].map(({ key, label }) => (
                <th
                  key={key}
                  className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:text-gray-300 transition-colors select-none"
                  onClick={() => toggleSort(key)}
                >
                  <span className="flex items-center gap-1.5">
                    {label} <SortIcon field={key} />
                  </span>
                </th>
              ))}
              <th className="text-right px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((lead, i) => (
              <tr key={lead.id} className={clsx('lead-row border-b border-gray-800/30', i % 2 === 0 ? '' : 'bg-gray-900/20')}>
                {/* Lead name + avatar */}
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-500/30 to-purple-500/30 flex items-center justify-center text-xs font-bold text-brand-300 flex-shrink-0 border border-brand-500/20">
                      {lead.name.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-200">{lead.name}</p>
                      <p className="text-xs text-gray-600">{lead.storeUrl ? new URL(lead.storeUrl.startsWith('http') ? lead.storeUrl : `https://${lead.storeUrl}`).hostname : ''}</p>
                    </div>
                  </div>
                </td>
                {/* Company */}
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-2">
                    <Building2 size={13} className="text-gray-600 flex-shrink-0" />
                    <span className="text-sm text-gray-300">{lead.company}</span>
                  </div>
                </td>
                {/* Niche */}
                <td className="px-5 py-3.5">
                  {lead.niche ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-gray-800/80 border border-gray-700/40 text-xs text-gray-400">
                      <Tag size={10} />
                      {lead.niche}
                    </span>
                  ) : <span className="text-gray-700 text-sm">—</span>}
                </td>
                {/* Email */}
                <td className="px-5 py-3.5">
                  <span className="text-sm text-gray-400 font-mono">{lead.email}</span>
                </td>
                {/* Status */}
                <td className="px-5 py-3.5">
                  <StatusBadge status={lead.status} />
                  {lead.errorMsg && (
                    <p className="text-[10px] text-red-500 mt-0.5">{lead.errorMsg}</p>
                  )}
                </td>
                {/* Sent At */}
                <td className="px-5 py-3.5 text-xs text-gray-600">
                  {lead.sentAt
                    ? new Date(lead.sentAt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
                    : '—'}
                </td>
                {/* Action */}
                <td className="px-5 py-3.5 text-right">
                  <button
                    onClick={() => handleManualSend(lead)}
                    disabled={lead.status === 'sent' || lead.status === 'sending' || sendingIds.has(lead.id)}
                    className={clsx(
                      'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200',
                      lead.status === 'sent'
                        ? 'bg-emerald-500/10 text-emerald-500 cursor-default border border-emerald-500/20'
                        : lead.status === 'sending' || sendingIds.has(lead.id)
                          ? 'bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700'
                          : 'bg-brand-500/10 hover:bg-brand-500/20 text-brand-400 border border-brand-500/20 hover:shadow-sm hover:shadow-brand-500/10'
                    )}
                  >
                    {lead.status === 'sending' || sendingIds.has(lead.id)
                      ? <><Loader2 size={12} className="animate-spin" /> Sending</>
                      : lead.status === 'sent'
                        ? <><CheckCircle2 size={12} /> Sent</>
                        : <><Send size={12} /> Send</>
                    }
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && leads.length > 0 && (
        <div className="py-12 text-center">
          <p className="text-sm text-gray-500">No leads match your filters</p>
          <button
            onClick={() => { dispatch({ type: 'SET_SEARCH', payload: '' }); dispatch({ type: 'SET_STATUS_FILTER', payload: 'all' }) }}
            className="text-xs text-brand-400 hover:text-brand-300 mt-2 inline-block"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  )
}
