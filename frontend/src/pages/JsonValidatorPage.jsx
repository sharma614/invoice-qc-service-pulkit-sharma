import { useState } from 'react'
import { validateJson } from '../api/client'
import { Binary, Play, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'

const initialJson = [
  {
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-03-20",
    "due_date": "2024-04-20",
    "seller_name": "ACME Corp",
    "buyer_name": "TechGlobal Ltd",
    "currency": "USD",
    "net_total": 1000.0,
    "tax_amount": 200.0,
    "gross_total": 1200.0,
    "line_items": [
      { "description": "Consulting", "quantity": 10, "unit_price": 100, "line_total": 1000 }
    ]
  }
]

export default function JsonValidatorPage() {
  const [json, setJson] = useState(JSON.stringify(initialJson, null, 2))
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleValidate = async () => {
    try {
      setLoading(true); setResults(null); setError(null)
      const parsed = JSON.parse(json)
      const data = await validateJson(parsed)
      setResults(data)
    } catch (err) {
      if (err instanceof SyntaxError) setError('Invalid JSON syntax. Please check your brackets and commas.')
      else setError(err.response?.data?.detail || 'Validation service error. Make sure the backend is running.')
    } finally { setLoading(false) }
  }

  const resetJson = () => setJson(JSON.stringify(initialJson, null, 2))

  return (
    <div className="animate-fade">
      <div className="page-header" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>Schema & QC Validator</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manually test the QC engine by providing raw invoice JSON. Validates schema, business rules, and mathematical totals.</p>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1.2fr 0.8fr' }}>
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Binary size={18} color="var(--accent)" /> JSON Payload
            </h3>
            <button onClick={resetJson} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.85rem' }}>
              <RefreshCw size={14} /> Reset
            </button>
          </div>
          <textarea
            className="json-editor"
            value={json}
            onChange={(e) => setJson(e.target.value)}
            spellCheck="false"
          />
          <button onClick={handleValidate} className="btn btn-primary" style={{ width: '100%', marginTop: '1.5rem' }} disabled={loading}>
            {loading ? 'Validating...' : <><Play size={16} fill="currentColor" /> Run Validation</>}
          </button>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
             Validation Report
          </h3>

          {!results && !error && (
            <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
              Enter JSON and click "Run Validation" to see the QC report.
            </div>
          )}

          {error && <div style={{ color: 'var(--danger)', padding: '1rem', background: 'var(--danger-bg)', borderRadius: '12px', fontSize: '0.9rem' }}>{error}</div>}

          {results && (
            <div>
              <div style={{ background: 'var(--bg-secondary)', borderRadius: '16px', padding: '1.5rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                   <div>
                     <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>TOTAL INVOICES</div>
                     <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{results.summary.total_invoices}</div>
                   </div>
                   <div style={{ textAlign: 'right' }}>
                     <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>SCORE</div>
                     <div style={{ fontSize: '1.5rem', fontWeight: 800, color: results.summary.valid_invoices === results.summary.total_invoices ? 'var(--success)' : 'var(--warning)' }}>
                       {Math.round((results.summary.valid_invoices / results.summary.total_invoices) * 100)}%
                     </div>
                   </div>
                </div>
                <div style={{ height: '8px', background: 'var(--border)', borderRadius: '4px', overflow: 'hidden' }}>
                   <div style={{ height: '100%', width: `${(results.summary.valid_invoices / results.summary.total_invoices) * 100}%`, background: 'var(--success)' }} />
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                 {results.results.map((res, i) => (
                   <div key={i} style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: `1px solid ${res.is_valid ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)'}` }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                         <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{res.invoice_id}</span>
                         {res.is_valid ? <CheckCircle2 size={16} color="var(--success)" /> : <AlertCircle size={16} color="var(--danger)" />}
                      </div>
                      {!res.is_valid && (
                         <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--danger)' }}>
                            {res.errors.join(', ').replace(/_/g, ' ')}
                         </div>
                      )}
                   </div>
                 ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
