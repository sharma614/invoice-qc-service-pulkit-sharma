import { useState, useEffect } from 'react'
import { checkHealth } from '../api/client'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import { Activity, ShieldCheck, ShieldAlert, FileText, CheckCircle2, AlertCircle } from 'lucide-react'

const COLORS = ['#22c55e', '#ef4444', '#f59e0b', '#38bdf8']

export default function Dashboard() {
  const [health, setHealth] = useState(null)
  
  // Mock data for initial view - would be populated from a history API if available
  const stats = [
    { name: 'Valid', value: 85 },
    { name: 'Invalid', value: 15 },
  ]

  const errorTypes = [
    { name: 'Totals Mismatch', count: 12 },
    { name: 'Missing Fields', count: 8 },
    { name: 'Invalid Date', count: 5 },
    { name: 'Duplicates', count: 3 },
  ]

  useEffect(() => {
    checkHealth().then(setHealth).catch(() => setHealth({ status: 'offline' }))
  }, [])

  return (
    <div className="animate-fade">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>QC Control Center</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: health?.status === 'ok' ? '#22c55e' : '#ef4444' }}></div>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Service Status: {health?.status === 'ok' ? 'Online' : 'Loading or Offline...'}
          </span>
        </div>
      </div>

      <div className="grid">
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: 'rgba(56, 189, 248, 0.1)', padding: '1rem', borderRadius: '16px', color: 'var(--accent)' }}>
            <Activity size={32} />
          </div>
          <div className="summary-stat">
            <span className="stat-value">1,280</span>
            <span className="stat-label">Total Invoices</span>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: 'var(--success-bg)', padding: '1rem', borderRadius: '16px', color: 'var(--success)' }}>
            <CheckCircle2 size={32} />
          </div>
          <div className="summary-stat">
            <span className="stat-value">1,088</span>
            <span className="stat-label">Valid (85%)</span>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: 'var(--danger-bg)', padding: '1rem', borderRadius: '16px', color: 'var(--danger)' }}>
            <AlertCircle size={32} />
          </div>
          <div className="summary-stat">
            <span className="stat-value">192</span>
            <span className="stat-label">Flagged (15%)</span>
          </div>
        </div>
      </div>

      <div className="grid" style={{ marginTop: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck size={20} color="#22c55e" /> Success Distribution
          </h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {stats.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={20} color="#ef4444" /> Common Quality Issues
          </h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={errorTypes} layout="vertical">
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" width={120} tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: 'rgba(56, 189, 248, 0.05)' }} contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="count" fill="var(--accent)" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
