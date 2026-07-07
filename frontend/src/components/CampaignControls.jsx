import { useEffect, useRef } from 'react'
import { useCampaign } from '../store/CampaignStore'
import { Play, Pause, RotateCcw, Zap } from 'lucide-react'
import clsx from 'clsx'
import toast from 'react-hot-toast'

function simulateSend() {
  return new Promise((resolve) => {
    // Smoother delay for Loom recording (2-3 seconds per email)
    const delay = 2000 + Math.random() * 1000
    setTimeout(() => {
      resolve(true) // 100% success rate for the demo
    }, delay)
  })
}

export default function CampaignControls() {
  const { state, dispatch } = useCampaign()
  const { campaign, leads, stats } = state
  const isRunning = campaign.status === 'running'
  const isDone = stats.sent + stats.failed === stats.total && stats.total > 0

  const timerRef = useRef(null)
  
  // The core campaign runner effect
  useEffect(() => {
    if (campaign.status !== 'running') return
    
    const runNext = async () => {
      // Find next pending lead
      const nextPendingIndex = leads.findIndex(l => l.status === 'pending' || l.status === 'sending')
      
      if (nextPendingIndex === -1) {
        // We are done!
        dispatch({ type: 'SET_CAMPAIGN_STATUS', payload: 'done' })
        toast.success('Campaign completed!', { icon: '🎉' })
        return
      }

      const currentLead = leads[nextPendingIndex]
      
      // Mark as sending
      dispatch({ type: 'SET_CURRENT_INDEX', payload: nextPendingIndex })
      dispatch({ type: 'SET_LEAD_STATUS', payload: { id: currentLead.id, status: 'sending' } })
      
      // Simulate API call
      const success = await simulateSend()
      
      // Update result
      dispatch({ 
        type: 'SET_LEAD_STATUS', 
        payload: { 
          id: currentLead.id, 
          status: success ? 'sent' : 'failed', 
          errorMsg: success ? null : 'SMTP connection timeout' 
        } 
      })
      
      // Schedule next run
      timerRef.current = setTimeout(runNext, campaign.delay)
    }

    timerRef.current = setTimeout(runNext, 500)

    return () => clearTimeout(timerRef.current)
  }, [campaign.status, campaign.delay, leads, dispatch])


  const handleStart = () => {
    if (stats.total === 0) {
      toast.error('Import leads first')
      return
    }
    if (isDone) {
      toast.error('All leads processed. Reset campaign to run again.')
      return
    }
    dispatch({ type: 'SET_CAMPAIGN_STATUS', payload: 'running' })
    toast.success('Campaign started! Sending auto-emails...')
  }

  const handlePause = () => {
    dispatch({ type: 'SET_CAMPAIGN_STATUS', payload: 'paused' })
    clearTimeout(timerRef.current)
    toast('Campaign paused', { icon: '⏸️' })
  }

  const handleReset = () => {
    if (confirm('Are you sure you want to reset all statuses to pending?')) {
      dispatch({ type: 'SET_CAMPAIGN_STATUS', payload: 'idle' })
      clearTimeout(timerRef.current)
      leads.forEach(l => {
        dispatch({ type: 'SET_LEAD_STATUS', payload: { id: l.id, status: 'pending', errorMsg: null } })
      })
      toast.success('Campaign reset')
    }
  }

  return (
    <div className="glass-card p-5 mb-6 flex flex-col md:flex-row items-center justify-between gap-5 animate-fade-in border border-gray-800/60 shadow-xl shadow-black/20">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <div className={clsx(
            'w-8 h-8 rounded-lg flex items-center justify-center shadow-lg',
            isRunning ? 'bg-emerald-500 shadow-emerald-500/30' : 'bg-brand-500 shadow-brand-500/30'
          )}>
            <Zap size={16} className="text-white" />
          </div>
          Auto-Campaign
        </h2>
        <p className="text-sm text-gray-400 mt-1 max-w-lg leading-relaxed">
           Automate sending emails to all pending leads with smart delays to protect deliverability and avoid spam filters.
        </p>
      </div>

      <div className="flex items-center gap-3 w-full md:w-auto">
        <div className="hidden md:flex flex-col items-end mr-4">
          <span className="text-xs text-gray-500 font-medium tracking-wide uppercase">Engine Status</span>
          <span className={clsx(
            'text-sm font-bold',
            isRunning ? 'text-emerald-400' : 
            campaign.status === 'paused' ? 'text-amber-400' : 
            isDone ? 'text-brand-400' : 'text-gray-400'
          )}>
            {isRunning ? 'RUNNING' : 
             campaign.status === 'paused' ? 'PAUSED' : 
             isDone ? 'COMPLETE' : 'IDLE'}
          </span>
        </div>

        {isRunning ? (
          <button onClick={handlePause} className="btn-secondary flex-1 md:flex-none justify-center">
            <Pause size={16} className="text-amber-400" /> Pause Engine
          </button>
        ) : (
          <button 
            onClick={handleStart} 
            disabled={isDone || stats.total === 0}
            className="btn-primary flex-1 md:flex-none justify-center group"
          >
            <Play size={16} className={clsx("fill-white transition-transform group-hover:scale-110", isDone && 'opacity-50')} /> 
            {campaign.status === 'paused' ? 'Resume Campaign' : 'Start Campaign'}
          </button>
        )}

        {(stats.sent > 0 || stats.failed > 0) && (
          <button onClick={handleReset} className="w-10 h-10 rounded-xl bg-gray-800 hover:bg-gray-700 flex items-center justify-center border border-gray-700/60 transition-colors" title="Reset all statuses">
            <RotateCcw size={16} className="text-gray-400" />
          </button>
        )}
      </div>
    </div>
  )
}
