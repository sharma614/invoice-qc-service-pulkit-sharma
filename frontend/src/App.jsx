import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import UploadPage from './pages/UploadPage'
import JsonValidatorPage from './pages/JsonValidatorPage'
import { FileText, BarChart3, Binary, LayoutDashboard } from 'lucide-react'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-content">
        <NavLink to="/" className="logo">
          <div className="logo-icon"><FileText size={20} /></div>
          <span>InvoiceFlow QC</span>
        </NavLink>
        <div className="nav-links">
          <NavLink to="/" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`} end>
            <LayoutDashboard size={18} /> Dashboard
          </NavLink>
          <NavLink to="/upload" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <FileText size={18} /> PDF Extraction
          </NavLink>
          <NavLink to="/validate" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <Binary size={18} /> JSON Validator
          </NavLink>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/validate" element={<JsonValidatorPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
