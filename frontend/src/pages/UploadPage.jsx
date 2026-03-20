import { useState, useRef } from 'react'
import { extractAndValidatePdfs } from '../api/client'
import { Upload, X, CheckCircle2, AlertCircle, FileText, ChevronRight, Info } from 'lucide-react'

export default function UploadPage() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef()

  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files).filter(f => f.type === 'application/pdf')
    setFiles(p => [...p, ...selected])
  }

  const removeFile = (idx) => setFiles(p => p.filter((_, i) => i !== idx))

  const handleUpload = async () => {
    if (files.length === 0) return
    setLoading(true); setResults(null); setError(null)
    try {
      const data = await extractAndValidatePdfs(files)
      setResults(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Extraction failed. Make sure the backend is running.')
    } finally { setLoading(false) }
  }

  return (
    <div className="animate-fade">
      <div className="page-header" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>PDF Extraction & QC</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Upload invoices in PDF format to be processed. The service will extract data and run quality checks.</p>
      </div>

      <div className="grid">
        <div className="card">
          <div className="upload-zone" onClick={() => fileInputRef.current.click()} onDragOver={(e) => e.preventDefault()}>
            <input type="file" multiple accept=".pdf" ref={fileInputRef} onChange={handleFileChange} style={{ display: 'none' }} />
            <div style={{ color: 'var(--accent)', marginBottom: '1rem' }}><Upload size={48} /></div>
            <h3 style={{ marginBottom: '0.5rem' }}>Drop PDFs here or Click to Browse</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Only PDF files are supported</p>
          </div>

          {files.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>Pending Files ({files.length})</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {files.map((f, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-secondary)', padding: '0.75rem 1rem', borderRadius: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <FileText size={18} color="var(--accent)" />
                      <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{f.name}</span>
                    </div>
                    <button onClick={() => removeFile(i)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={16} /></button>
                  </div>
                ))}
              </div>
              <button onClick={handleUpload} className="btn btn-primary" style={{ width: '100%', marginTop: '1.5rem' }} disabled={loading}>
                {loading ? 'Processing...' : `Extract from ${files.length} Files`}
              </button>
            </div>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Info size={18} color="var(--accent)" /> Processed Results
          </h3>
          
           {!results && !loading && (
            <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
              No data processed yet. Upload PDFs to see results.
            </div>
          )}

          {loading && (
            <div style={{ textAlign: 'center', padding: '4rem 0' }}>
               <div style={{ width: 40, height: 40, border: '3px solid var(--border)', borderTopColor: 'var(--accent)', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 1rem' }}></div>
               <p style={{ color: 'var(--text-secondary)' }}>Running AI extraction and QC validation...</p>
            </div>
          )}

          {results && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <div className="card" style={{ flex: 1, padding: '1rem', textAlign: 'center', background: 'var(--success-bg)' }}>
                  <div style={{ color: 'var(--success)', fontWeight: 800 }}>{results.summary.valid_invoices}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>VALID</div>
                </div>
                <div className="card" style={{ flex: 1, padding: '1rem', textAlign: 'center', background: 'var(--danger-bg)' }}>
                  <div style={{ color: 'var(--danger)', fontWeight: 800 }}>{results.summary.invalid_invoices}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>FLAGGED</div>
                </div>
              </div>

              {results.results.map((res, i) => (
                <div key={i} className="card" style={{ padding: '1.25rem', borderLeft: `4px solid ${res.is_valid ? 'var(--success)' : 'var(--danger)'}` }}>
                   <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Invoice #{res.invoice_id}</span>
                      <span className={`status-badge ${res.is_valid ? 'status-valid' : 'status-invalid'}`}>
                        {res.is_valid ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />} {res.is_valid ? 'Pass' : 'Reject'}
                      </span>
                   </div>
                   {!res.is_valid && (
                     <div style={{ fontSize: '0.85rem', color: 'var(--danger)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        {res.errors.map((err, j) => <div key={j} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>• {err.replace(/_/g, ' ')}</div>)}
                     </div>
                   )}
                </div>
              ))}
            </div>
          )}

          {error && <div style={{ color: 'var(--danger)', padding: '1rem', background: 'var(--danger-bg)', borderRadius: '12px', fontSize: '0.9rem' }}>{error}</div>}
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
