import { useCallback, useState, useRef } from 'react'
import { useCampaign } from '../store/CampaignStore'
import Papa from 'papaparse'
import * as XLSX from 'xlsx'
import { Upload, FileSpreadsheet, X, CheckCircle2, AlertCircle } from 'lucide-react'
import clsx from 'clsx'
import toast from 'react-hot-toast'

const DEMO_LEADS = [
  { name: 'Sarah Mitchell',  email: 'sarah@bloomcraft.com',     company: 'BloomCraft', niche: 'Home Decor',    store_url: 'https://bloomcraft.com' },
  { name: 'James Okafor',    email: 'james@kiterunner.co',      company: 'KiteRunner', niche: 'Outdoor Gear',  store_url: 'https://kiterunner.co' },
  { name: 'Priya Nair',      email: 'priya@velvetleaf.in',      company: 'VelvetLeaf', niche: 'Skincare',      store_url: 'https://velvetleaf.in' },
  { name: 'Lucas Fernandez', email: 'lucas@urbanframe.store',   company: 'UrbanFrame', niche: 'Photography',   store_url: 'https://urbanframe.store' },
  { name: 'Emma Tran',       email: 'emma@silkroutebags.com',  company: 'SilkRoute',  niche: 'Fashion',       store_url: 'https://silkroutebags.com' },
  { name: 'Omar Hassan',     email: 'omar@speedgear.shop',      company: 'SpeedGear',  niche: 'Sports',        store_url: 'https://speedgear.shop' },
  { name: 'Lily Zhao',       email: 'lily@minimalwear.co',      company: 'MinimalWear',niche: 'Clothing',      store_url: 'https://minimalwear.co' },
  { name: 'Aiden Walsh',     email: 'aiden@brewbottle.com',     company: 'BrewBottle', niche: 'Food & Bev',    store_url: 'https://brewbottle.com' },
  { name: 'Nina Petrov',     email: 'nina@petalcraft.eu',       company: 'PetalCraft', niche: 'Floral',        store_url: 'https://petalcraft.eu' },
  { name: 'Marco Villa',     email: 'marco@lightbrand.co',      company: 'LightBrand', niche: 'Electronics',   store_url: 'https://lightbrand.co' },
  { name: 'Zara Ahmed',      email: 'zara@zenvibe.store',       company: 'ZenVibe',    niche: 'Wellness',      store_url: 'https://zenvibe.store' },
  { name: 'Tyler Brooks',    email: 'tyler@packcraft.io',       company: 'PackCraft',  niche: 'Travel',        store_url: 'https://packcraft.io' },
]

export default function UploadZone({ onClose }) {
  const { loadLeads, dispatch, state } = useCampaign()
  const [dragOver, setDragOver] = useState(false)
  const [preview, setPreview] = useState(null)
  const [fileName, setFileName] = useState('')
  const fileInputRef = useRef(null)

  const parseFile = useCallback((file) => {
    setFileName(file.name)
    const ext = file.name.split('.').pop().toLowerCase()

    if (ext === 'csv') {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => setPreview(results.data),
        error: () => toast.error('Failed to parse CSV'),
      })
    } else if (['xlsx', 'xls'].includes(ext)) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const wb = XLSX.read(e.target.result, { type: 'array' })
        const ws = wb.Sheets[wb.SheetNames[0]]
        const data = XLSX.utils.sheet_to_json(ws)
        setPreview(data)
      }
      reader.readAsArrayBuffer(file)
    } else {
      toast.error('Please upload a CSV or Excel file')
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) parseFile(file)
  }, [parseFile])

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) parseFile(file)
  }

  const handleConfirm = () => {
    loadLeads(preview)
    toast.success(`${preview.length} leads imported successfully!`)
    onClose()
  }

  const handleDemo = () => {
    loadLeads(DEMO_LEADS)
    toast.success('Demo leads loaded — 12 Shopify stores ready to outreach!')
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="glass-card w-full max-w-2xl border border-gray-700/60 shadow-2xl shadow-black/60 animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-800/60">
          <div>
            <h2 className="text-lg font-bold text-white">Import Lead List</h2>
            <p className="text-sm text-gray-500 mt-0.5">Upload CSV or Excel with name, email, company columns</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg bg-gray-800 hover:bg-gray-700 flex items-center justify-center transition-colors">
            <X size={15} className="text-gray-400" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {!preview ? (
            <>
              {/* Drop zone */}
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={clsx(
                  'border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200',
                  dragOver ? 'border-brand-400 bg-brand-500/10' : 'border-gray-700 hover:border-gray-600 hover:bg-gray-800/30'
                )}
              >
                <FileSpreadsheet size={36} className={clsx('mx-auto mb-3', dragOver ? 'text-brand-400' : 'text-gray-600')} />
                <p className="text-sm font-medium text-gray-300">Drop your CSV or Excel file here</p>
                <p className="text-xs text-gray-600 mt-1">or click to browse your files</p>
                <input ref={fileInputRef} type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handleFileChange} />
              </div>

              {/* Demo option */}
              <div className="flex items-center gap-3">
                <div className="flex-1 h-px bg-gray-800" />
                <span className="text-xs text-gray-600">or</span>
                <div className="flex-1 h-px bg-gray-800" />
              </div>
              <button
                onClick={handleDemo}
                className="w-full btn-secondary justify-center py-3 border-dashed"
              >
                <CheckCircle2 size={16} className="text-brand-400" />
                Load 12 Demo Shopify Leads
              </button>

              {/* Column guide */}
              <div className="p-4 bg-gray-800/40 rounded-xl border border-gray-700/40">
                <p className="text-xs font-semibold text-gray-400 mb-2">Expected columns (auto-detected):</p>
                <div className="flex flex-wrap gap-2">
                  {['name', 'email', 'company', 'niche', 'store_url'].map(col => (
                    <code key={col} className="text-xs bg-gray-700/60 text-brand-300 px-2 py-0.5 rounded font-mono">{col}</code>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Preview table */}
              <div className="flex items-center gap-3 p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                <CheckCircle2 size={18} className="text-emerald-400 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-emerald-300">{preview.length} leads detected in "{fileName}"</p>
                  <p className="text-xs text-emerald-500/80">Review the preview below before importing</p>
                </div>
              </div>

              <div className="max-h-64 overflow-auto rounded-xl border border-gray-800/60">
                <table className="w-full text-xs">
                  <thead className="bg-gray-800/80 sticky top-0">
                    <tr>
                      {['Name', 'Email', 'Company', 'Niche'].map(h => (
                        <th key={h} className="text-left px-4 py-2.5 text-gray-400 font-semibold">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.slice(0, 8).map((row, i) => (
                      <tr key={i} className="border-t border-gray-800/40 hover:bg-gray-800/30 transition-colors">
                        <td className="px-4 py-2.5 text-gray-200">{row.name || row.Name || `Lead ${i+1}`}</td>
                        <td className="px-4 py-2.5 text-gray-400 font-mono">{row.email || row.Email || '—'}</td>
                        <td className="px-4 py-2.5 text-gray-300">{row.company || row.Company || '—'}</td>
                        <td className="px-4 py-2.5 text-gray-500">{row.niche || row.Niche || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {preview.length > 8 && (
                  <p className="text-center text-xs text-gray-600 py-2">+ {preview.length - 8} more leads</p>
                )}
              </div>

              <div className="flex gap-3">
                <button onClick={() => setPreview(null)} className="btn-secondary flex-1 justify-center">
                  Re-upload
                </button>
                <button onClick={handleConfirm} className="btn-primary flex-1 justify-center">
                  <Upload size={15} />
                  Import {preview.length} Leads
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
