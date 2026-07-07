import { useState } from 'react'
import { CampaignProvider, useCampaign } from './store/CampaignStore'
import { Toaster } from 'react-hot-toast'
import Sidebar from './components/Sidebar'
import StatCards from './components/StatCards'
import UploadZone from './components/UploadZone'
import LeadsTable from './components/LeadsTable'
import CampaignControls from './components/CampaignControls'
import { BarChart3 } from 'lucide-react'

function AnalyticsPlaceholder() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center pt-20 animate-fade-in">
      <div className="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mb-6 shadow-xl border border-gray-800/80">
        <BarChart3 size={28} className="text-gray-600" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Analytics Dashboard</h2>
      <p className="text-sm text-gray-500 max-w-sm text-center">
        Full reporting on open rates, click rates, and reply sentiment will appear here after the campaign completes.
      </p>
    </div>
  )
}

function DashboardContent() {
  const { state } = useCampaign()
  const [showUpload, setShowUpload] = useState(false)
  const isAnalytics = state.view === 'analytics'

  return (
    <div className="flex h-screen overflow-hidden bg-mesh fixed inset-0">
      <Sidebar onImportClick={() => setShowUpload(true)} />
      
      <main className="flex-1 overflow-y-auto w-full relative">
        <div className="max-w-7xl mx-auto p-8 lg:p-10 min-h-full pb-32">
          {/* Header */}
          <header className="mb-10 animate-slide-up">
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              {isAnalytics ? 'Analytics' : 'Campaign Dashboard'}
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              {isAnalytics 
                ? 'Track your outreach performance and conversions.' 
                : 'Manage your automated GTM cold email outreach sequences.'}
            </p>
          </header>

          {isAnalytics ? (
            <AnalyticsPlaceholder />
          ) : (
            <div className="space-y-6">
              <StatCards />
              {state.view === 'campaign' && <CampaignControls />}
              <LeadsTable />
            </div>
          )}
        </div>
      </main>

      {showUpload && <UploadZone onClose={() => setShowUpload(false)} />}
      
      <Toaster 
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#111827',
            color: '#fff',
            border: '1px solid rgba(75, 85, 99, 0.4)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
            fontSize: '14px',
            fontWeight: '500'
          },
          success: { iconTheme: { primary: '#34d399', secondary: '#111827' } },
          error: { iconTheme: { primary: '#f87171', secondary: '#111827' } },
        }}
      />
    </div>
  )
}

export default function App() {
  return (
    <CampaignProvider>
      <DashboardContent />
    </CampaignProvider>
  )
}
