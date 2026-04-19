import { CheckCircle2, AlertCircle } from 'lucide-react'

/**
 * @typedef {Object} ValidationResult
 * @property {string} invoice_id
 * @property {boolean} is_valid
 * @property {string[]} errors
 */

/**
 * Shared component for displaying an invoice validation result.
 * @param {Object} props
 * @param {ValidationResult} props.result
 */
export default function InvoiceResultCard({ result }) {
  return (
    <div className="card" style={{ padding: '1.25rem', borderLeft: `4px solid ${result.is_valid ? 'var(--success)' : 'var(--danger)'}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Invoice #{result.invoice_id}</span>
        <span className={`status-badge ${result.is_valid ? 'status-valid' : 'status-invalid'}`}>
          {result.is_valid ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />} {result.is_valid ? 'Pass' : 'Reject'}
        </span>
      </div>
      {!result.is_valid && (
        <div style={{ fontSize: '0.85rem', color: 'var(--danger)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {result.errors.map((err, j) => (
            <div key={j} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              • {err.replace(/_/g, ' ')}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
