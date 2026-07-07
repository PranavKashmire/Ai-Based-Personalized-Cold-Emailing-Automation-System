/**
 * Campaign Store — central state using React Context + useReducer
 * Manages leads, campaign status, and sending progress
 */
import { createContext, useContext, useReducer, useCallback } from 'react'

const CampaignContext = createContext(null)

const INITIAL_STATE = {
  leads: [],           // Array of lead objects
  campaign: {
    status: 'idle',    // 'idle' | 'running' | 'paused' | 'done'
    currentIndex: null,
    delay: 3000,       // ms between sends
  },
  stats: {
    total: 0,
    sent: 0,
    failed: 0,
    pending: 0,
  },
  view: 'leads',       // 'leads' | 'campaign' | 'analytics'
  searchQuery: '',
  statusFilter: 'all', // 'all' | 'pending' | 'sent' | 'failed'
}

function computeStats(leads) {
  return {
    total: leads.length,
    sent: leads.filter(l => l.status === 'sent').length,
    failed: leads.filter(l => l.status === 'failed').length,
    pending: leads.filter(l => l.status === 'pending').length,
    sending: leads.filter(l => l.status === 'sending').length,
  }
}

function campaignReducer(state, action) {
  switch (action.type) {
    case 'LOAD_LEADS': {
      const leads = action.payload
      return { ...state, leads, stats: computeStats(leads) }
    }
    case 'CLEAR_LEADS':
      return { ...state, leads: [], stats: computeStats([]), campaign: { ...state.campaign, status: 'idle', currentIndex: null } }

    case 'SET_LEAD_STATUS': {
      const leads = state.leads.map(l =>
        l.id === action.payload.id ? { ...l, status: action.payload.status, sentAt: action.payload.status === 'sent' ? new Date().toISOString() : l.sentAt, errorMsg: action.payload.errorMsg } : l
      )
      return { ...state, leads, stats: computeStats(leads) }
    }

    case 'SET_CAMPAIGN_STATUS':
      return { ...state, campaign: { ...state.campaign, status: action.payload, currentIndex: action.payload === 'idle' ? null : state.campaign.currentIndex } }

    case 'SET_CURRENT_INDEX':
      return { ...state, campaign: { ...state.campaign, currentIndex: action.payload } }

    case 'SET_DELAY':
      return { ...state, campaign: { ...state.campaign, delay: action.payload } }

    case 'SET_VIEW':
      return { ...state, view: action.payload }

    case 'SET_SEARCH':
      return { ...state, searchQuery: action.payload }

    case 'SET_STATUS_FILTER':
      return { ...state, statusFilter: action.payload }

    default:
      return state
  }
}

export function CampaignProvider({ children }) {
  const [state, dispatch] = useReducer(campaignReducer, INITIAL_STATE)

  const loadLeads = useCallback((rawLeads) => {
    const leads = rawLeads.map((row, i) => ({
      id: `lead-${Date.now()}-${i}`,
      name: row.name || row.Name || row['First Name'] || `Lead ${i + 1}`,
      email: row.email || row.Email || row['Email Address'] || '',
      company: row.company || row.Company || row['Company Name'] || row.Store || row.store_url || '—',
      niche: row.niche || row.Niche || row.Industry || '',
      storeUrl: row.store_url || row['Store URL'] || row.website || '',
      status: 'pending',
      sentAt: null,
      errorMsg: null,
    })).filter(l => l.email)
    dispatch({ type: 'LOAD_LEADS', payload: leads })
  }, [])

  return (
    <CampaignContext.Provider value={{ state, dispatch, loadLeads }}>
      {children}
    </CampaignContext.Provider>
  )
}

export function useCampaign() {
  const ctx = useContext(CampaignContext)
  if (!ctx) throw new Error('useCampaign must be used inside CampaignProvider')
  return ctx
}
