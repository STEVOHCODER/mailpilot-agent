import { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import { auth, email, whatsapp, rules, dashboard, billing } from './api/client'

const AuthContext = createContext(null)

function useAuth() { return useContext(AuthContext) }

function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      auth.me().then(u => setUser(u)).catch(() => localStorage.removeItem('token')).finally(() => setLoading(false))
    } else { setLoading(false) }
  }, [])

  const login = async (data) => {
    const res = await auth.login(data)
    localStorage.setItem('token', res.access_token)
    setUser(res.user)
  }
  const register = async (data) => {
    const res = await auth.register(data)
    localStorage.setItem('token', res.access_token)
    setUser(res.user)
  }
  const logout = () => { localStorage.removeItem('token'); setUser(null) }

  return <AuthContext.Provider value={{ user, login, register, logout, loading }}>{children}</AuthContext.Provider>
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}>Loading...</div>
  return user ? children : <Navigate to="/login" />
}

// ─── Landing Page ──────────────────────────────────────────
function Landing() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', color: '#1a1a2e' }}>
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 40px', borderBottom: '1px solid #eee' }}>
        <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>MailPilot</div>
        <div>
          <Link to="/login" style={{ marginRight: 16, textDecoration: 'none', color: '#333' }}>Login</Link>
          <Link to="/register" style={{ padding: '8px 20px', background: '#3b82f6', color: '#fff', borderRadius: 8, textDecoration: 'none' }}>Get Started</Link>
        </div>
      </nav>
      <section style={{ textAlign: 'center', padding: '80px 20px 60px', maxWidth: 700, margin: '0 auto' }}>
        <h1 style={{ fontSize: '3rem', lineHeight: 1.2, marginBottom: 16 }}>Get Your Important Emails Directly on WhatsApp</h1>
        <p style={{ fontSize: '1.2rem', color: '#555', marginBottom: 32 }}>Connect your email and WhatsApp in minutes. Automatically receive the emails that matter most, wherever you are.</p>
        <Link to="/register" style={{ padding: '14px 32px', background: '#3b82f6', color: '#fff', borderRadius: 10, textDecoration: 'none', fontSize: '1.1rem', fontWeight: 600 }}>Get Started Free</Link>
      </section>
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24, maxWidth: 900, margin: '0 auto', padding: '40px 20px' }}>
        {[['Connect Email','Link your Gmail or any email provider'],['Connect WhatsApp','One-click WhatsApp Business connection'],['Smart Rules','Choose which emails forward to WhatsApp'],['AI Summaries','Get concise summaries of long emails'],['Real-time Alerts','Forwarded in under 5 minutes'],['Secure & Private','Your data is encrypted and isolated']].map(([t,d]) => (
          <div key={t} style={{ padding: 24, border: '1px solid #eee', borderRadius: 12 }}>
            <h3 style={{ marginBottom: 8 }}>{t}</h3>
            <p style={{ color: '#666', fontSize: '0.9rem' }}>{d}</p>
          </div>
        ))}
      </section>
      <section style={{ textAlign: 'center', padding: '60px 20px', background: '#f8fafc' }}>
        <h2 style={{ marginBottom: 24 }}>Simple Pricing</h2>
        <div style={{ display: 'flex', gap: 24, justifyContent: 'center', flexWrap: 'wrap' }}>
          {[['Free','$0/mo','100 messages/mo'],['Starter','$9/mo','1,000 messages/mo'],['Pro','$29/mo','5,000 messages/mo'],['Business','$79/mo','20,000 messages/mo']].map(([p,price,limit]) => (
            <div key={p} style={{ padding: 24, border: '1px solid #ddd', borderRadius: 12, width: 200, textAlign: 'center' }}>
              <h3>{p}</h3>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, margin: '8px 0' }}>{price}</div>
              <p style={{ color: '#666', fontSize: '0.85rem' }}>{limit}</p>
            </div>
          ))}
        </div>
      </section>
      <footer style={{ textAlign: 'center', padding: 24, color: '#999', fontSize: '0.85rem' }}>MailPilot &copy; 2026. All rights reserved.</footer>
    </div>
  )
}

// ─── Auth Pages ────────────────────────────────────────────
function Login() {
  const { login } = useAuth()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const nav = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try { await login(form); nav('/dashboard') } catch (err) { setError(err.message) }
  }
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc' }}>
      <form onSubmit={handleSubmit} style={{ padding: 40, background: '#fff', borderRadius: 16, boxShadow: '0 4px 24px rgba(0,0,0,0.08)', width: 380 }}>
        <h2 style={{ marginBottom: 24, textAlign: 'center' }}>Sign in to MailPilot</h2>
        {error && <div style={{ padding: '8px 12px', background: '#fef2f2', color: '#dc2626', borderRadius: 8, marginBottom: 16, fontSize: '0.9rem' }}>{error}</div>}
        <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Email</label>
        <input type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
        <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Password</label>
        <input type="password" required value={form.password} onChange={e => setForm({...form, password: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 24, boxSizing: 'border-box' }} />
        <button type="submit" style={{ width: '100%', padding: 12, background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Sign In</button>
        <p style={{ textAlign: 'center', marginTop: 16, fontSize: '0.9rem' }}>Don't have an account? <Link to="/register" style={{ color: '#3b82f6' }}>Sign up</Link></p>
      </form>
    </div>
  )
}

function Register() {
  const { register } = useAuth()
  const [form, setForm] = useState({ email: '', password: '', name: '' })
  const [error, setError] = useState('')
  const nav = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try { await register(form); nav('/dashboard') } catch (err) { setError(err.message) }
  }
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc' }}>
      <form onSubmit={handleSubmit} style={{ padding: 40, background: '#fff', borderRadius: 16, boxShadow: '0 4px 24px rgba(0,0,0,0.08)', width: 380 }}>
        <h2 style={{ marginBottom: 24, textAlign: 'center' }}>Create your MailPilot account</h2>
        {error && <div style={{ padding: '8px 12px', background: '#fef2f2', color: '#dc2626', borderRadius: 8, marginBottom: 16, fontSize: '0.9rem' }}>{error}</div>}
        <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Name</label>
        <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
        <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Email</label>
        <input type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
        <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Password</label>
        <input type="password" required value={form.password} onChange={e => setForm({...form, password: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 24, boxSizing: 'border-box' }} />
        <button type="submit" style={{ width: '100%', padding: 12, background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Create Account</button>
        <p style={{ textAlign: 'center', marginTop: 16, fontSize: '0.9rem' }}>Already have an account? <Link to="/login" style={{ color: '#3b82f6' }}>Sign in</Link></p>
      </form>
    </div>
  )
}

// ─── Dashboard ─────────────────────────────────────────────
function Dashboard() {
  const { user, logout } = useAuth()
  const [data, setData] = useState(null)
  const [step, setStep] = useState(0) // 0=dashboard, 1=email, 2=whatsapp, 3=rules, 4=billing

  useEffect(() => { dashboard.get().then(setData).catch(console.error) }, [])

  const nav = useNavigate()
  const sidebar = (
    <div style={{ width: 220, background: '#0f172a', color: '#94a3b8', minHeight: '100vh', padding: '20px 0' }}>
      <div style={{ padding: '0 20px 20px', fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>MailPilot</div>
      {[['Overview',0],['Email',1],['WhatsApp',2],['Rules',3],['Billing',4]].map(([label,s]) => (
        <div key={label} onClick={() => setStep(s)} style={{ padding: '10px 20px', cursor: 'pointer', background: step===s ? '#1e293b' : 'transparent', color: step===s ? '#fff' : '#94a3b8', borderLeft: step===s ? '3px solid #3b82f6' : '3px solid transparent' }}>{label}</div>
      ))}
      <div style={{ position: 'absolute', bottom: 20, width: 220 }}>
        <div style={{ padding: '10px 20px', fontSize: '0.85rem' }}>{user?.email}</div>
        <div onClick={logout} style={{ padding: '10px 20px', cursor: 'pointer', color: '#ef4444' }}>Logout</div>
      </div>
    </div>
  )

  return (
    <div style={{ display: 'flex', fontFamily: 'system-ui, sans-serif' }}>
      {sidebar}
      <div style={{ flex: 1, padding: 32, background: '#f8fafc', minHeight: '100vh' }}>
        {step === 0 && data && <Overview data={data} />}
        {step === 1 && <EmailStep />}
        {step === 2 && <WhatsAppStep />}
        {step === 3 && <RulesStep />}
        {step === 4 && <BillingStep />}
      </div>
    </div>
  )
}

function Overview({ data }) {
  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Dashboard</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        {[
          ['Status', data.status === 'active' ? '🟢 Active' : '🔴 Inactive'],
          ['Email Accounts', data.email_connections],
          ['Messages Today', data.messages_today],
          ['This Month', data.messages_this_month],
        ].map(([label, val]) => (
          <div key={label} style={{ padding: 20, background: '#fff', borderRadius: 12, border: '1px solid #eee' }}>
            <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{val}</div>
          </div>
        ))}
      </div>
      <h3 style={{ marginBottom: 12 }}>Recent Activity</h3>
      <div style={{ background: '#fff', borderRadius: 12, border: '1px solid #eee', overflow: 'hidden' }}>
        {data.recent_messages.length === 0 && <div style={{ padding: 20, color: '#999', textAlign: 'center' }}>No messages yet. Connect your email and WhatsApp to get started.</div>}
        {data.recent_messages.map(m => (
          <div key={m.id} style={{ padding: '12px 20px', borderBottom: '1px solid #f0f0f0', display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ color: m.delivery_status === 'sent' ? '#22c55e' : m.delivery_status === 'failed' ? '#ef4444' : '#f59e0b' }}>{m.delivery_status === 'sent' ? '✓' : m.delivery_status === 'failed' ? '✗' : '○'}</span>
            <span style={{ fontWeight: 500 }}>{m.email_sender || 'Unknown'}</span>
            <span style={{ color: '#666', flex: 1 }}>{m.email_subject || 'No subject'}</span>
            <span style={{ color: '#999', fontSize: '0.85rem' }}>{m.created_at ? new Date(m.created_at).toLocaleTimeString() : ''}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function EmailStep() {
  const [conns, setConns] = useState([])
  const [form, setForm] = useState({ provider: 'gmail', email_address: '', password: '' })

  useEffect(() => { email.list().then(setConns).catch(console.error) }, [])

  const handleConnect = async (e) => {
    e.preventDefault()
    try {
      await email.connect(form)
      const updated = await email.list()
      setConns(updated)
      setForm({ provider: 'gmail', email_address: '', password: '' })
    } catch (err) { alert(err.message) }
  }

  const handleDisconnect = async (id) => {
    if (!confirm('Disconnect this email?')) return
    await email.disconnect(id)
    setConns(conns.filter(c => c.id !== id))
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Connect Email</h2>
      <div style={{ padding: 24, background: '#fff', borderRadius: 12, border: '1px solid #eee', marginBottom: 24, maxWidth: 500 }}>
        <h3 style={{ marginBottom: 16 }}>Add Email Account</h3>
        <form onSubmit={handleConnect}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Provider</label>
          <select value={form.provider} onChange={e => setForm({...form, provider: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16 }}>
            <option value="gmail">Gmail</option>
            <option value="outlook">Outlook</option>
            <option value="imap">IMAP (Other)</option>
          </select>
          <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Email Address</label>
          <input type="email" required value={form.email_address} onChange={e => setForm({...form, email_address: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
          {form.provider === 'imap' && <>
            <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>App Password</label>
            <input type="password" required value={form.password} onChange={e => setForm({...form, password: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
          </>}
          {form.provider === 'gmail' && <p style={{ fontSize: '0.85rem', color: '#666', marginBottom: 16 }}>You'll be redirected to Google to authorize access.</p>}
          <button type="submit" style={{ padding: '10px 24px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>Connect</button>
        </form>
      </div>
      <h3 style={{ marginBottom: 12 }}>Connected Accounts</h3>
      {conns.length === 0 && <p style={{ color: '#999' }}>No email accounts connected yet.</p>}
      {conns.map(c => (
        <div key={c.id} style={{ padding: '12px 20px', background: '#fff', borderRadius: 8, border: '1px solid #eee', marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span style={{ fontWeight: 500 }}>{c.email_address}</span>
            <span style={{ marginLeft: 8, padding: '2px 8px', background: '#f0fdf4', color: '#16a34a', borderRadius: 4, fontSize: '0.8rem' }}>{c.provider}</span>
          </div>
          <button onClick={() => handleDisconnect(c.id)} style={{ padding: '6px 12px', background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca', borderRadius: 6, cursor: 'pointer', fontSize: '0.85rem' }}>Disconnect</button>
        </div>
      ))}
    </div>
  )
}

function WhatsAppStep() {
  const [conn, setConn] = useState(null)
  const [form, setForm] = useState({ phone_number: '', meta_phone_number_id: '', meta_access_token: '' })
  const [testResult, setTestResult] = useState('')

  useEffect(() => { whatsapp.get().then(setConn).catch(() => {}) }, [])

  const handleConnect = async (e) => {
    e.preventDefault()
    try {
      const c = await whatsapp.connect(form)
      setConn(c)
    } catch (err) { alert(err.message) }
  }

  const handleDisconnect = async () => {
    if (!confirm('Disconnect WhatsApp?')) return
    await whatsapp.disconnect()
    setConn(null)
  }

  const handleTest = async () => {
    setTestResult('Sending...')
    try {
      await whatsapp.test()
      setTestResult('Test message sent! Check your WhatsApp.')
    } catch (err) { setTestResult('Failed: ' + err.message) }
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Connect WhatsApp</h2>
      {conn ? (
        <div style={{ padding: 24, background: '#fff', borderRadius: 12, border: '1px solid #eee', maxWidth: 500 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <span style={{ color: '#22c55e', fontSize: '1.2rem' }}>✓</span>
            <span style={{ fontWeight: 600 }}>Connected</span>
          </div>
          <p style={{ marginBottom: 8 }}><strong>Number:</strong> {conn.phone_number}</p>
          <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
            <button onClick={handleTest} style={{ padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer' }}>Send Test Message</button>
            <button onClick={handleDisconnect} style={{ padding: '8px 16px', background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca', borderRadius: 8, cursor: 'pointer' }}>Disconnect</button>
          </div>
          {testResult && <p style={{ marginTop: 12, color: testResult.includes('Failed') ? '#dc2626' : '#16a34a' }}>{testResult}</p>}
        </div>
      ) : (
        <div style={{ padding: 24, background: '#fff', borderRadius: 12, border: '1px solid #eee', maxWidth: 500 }}>
          <p style={{ color: '#666', marginBottom: 16 }}>Enter your WhatsApp Business API credentials to connect.</p>
          <form onSubmit={handleConnect}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Phone Number</label>
            <input type="text" required placeholder="+1234567890" value={form.phone_number} onChange={e => setForm({...form, phone_number: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
            <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Phone Number ID</label>
            <input type="text" required value={form.meta_phone_number_id} onChange={e => setForm({...form, meta_phone_number_id: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
            <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Access Token</label>
            <input type="password" required value={form.meta_access_token} onChange={e => setForm({...form, meta_access_token: e.target.value})} style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 24, boxSizing: 'border-box' }} />
            <button type="submit" style={{ padding: '10px 24px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>Connect WhatsApp</button>
          </form>
        </div>
      )}
    </div>
  )
}

function RulesStep() {
  const [ruleList, setRuleList] = useState([])
  const [form, setForm] = useState({ name: '', sender_emails: '', subject_contains: '' })

  useEffect(() => { rules.list().then(setRuleList).catch(console.error) }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      const data = {
        name: form.name || 'My Rule',
        sender_emails: form.sender_emails ? form.sender_emails.split(',').map(s => s.trim()) : [],
        subject_contains: form.subject_contains ? form.subject_contains.split(',').map(s => s.trim()) : [],
      }
      await rules.create(data)
      const updated = await rules.list()
      setRuleList(updated)
      setForm({ name: '', sender_emails: '', subject_contains: '' })
    } catch (err) { alert(err.message) }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this rule?')) return
    await rules.delete(id)
    setRuleList(ruleList.filter(r => r.id !== id))
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Forwarding Rules</h2>
      <div style={{ padding: 24, background: '#fff', borderRadius: 12, border: '1px solid #eee', marginBottom: 24, maxWidth: 500 }}>
        <h3 style={{ marginBottom: 16 }}>Create Rule</h3>
        <form onSubmit={handleCreate}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Rule Name</label>
          <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g. Important emails" style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
          <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Sender Emails (comma separated)</label>
          <input type="text" value={form.sender_emails} onChange={e => setForm({...form, sender_emails: e.target.value})} placeholder="boss@company.com, client@example.com" style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
          <label style={{ display: 'block', marginBottom: 4, fontSize: '0.85rem', color: '#666' }}>Subject Contains (comma separated)</label>
          <input type="text" value={form.subject_contains} onChange={e => setForm({...form, subject_contains: e.target.value})} placeholder="urgent, invoice, payment" style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16, boxSizing: 'border-box' }} />
          <button type="submit" style={{ padding: '10px 24px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>Create Rule</button>
        </form>
      </div>
      <h3 style={{ marginBottom: 12 }}>Your Rules</h3>
      {ruleList.length === 0 && <p style={{ color: '#999' }}>No rules yet. Create one above.</p>}
      {ruleList.map(r => (
        <div key={r.id} style={{ padding: '12px 20px', background: '#fff', borderRadius: 8, border: '1px solid #eee', marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong>{r.name}</strong>
            {r.sender_emails.length > 0 && <span style={{ marginLeft: 8, color: '#666', fontSize: '0.85rem' }}>Senders: {r.sender_emails.join(', ')}</span>}
            {r.subject_contains.length > 0 && <span style={{ marginLeft: 8, color: '#666', fontSize: '0.85rem' }}>Subjects: {r.subject_contains.join(', ')}</span>}
          </div>
          <button onClick={() => handleDelete(r.id)} style={{ padding: '6px 12px', background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca', borderRadius: 6, cursor: 'pointer', fontSize: '0.85rem' }}>Delete</button>
        </div>
      ))}
    </div>
  )
}

function BillingStep() {
  const [plans, setPlans] = useState([])
  const [sub, setSub] = useState(null)

  useEffect(() => {
    billing.plans().then(setPlans).catch(console.error)
    billing.subscription().then(setSub).catch(console.error)
  }, [])

  const handleUpgrade = async (plan) => {
    try {
      const res = await billing.checkout(plan)
      window.location.href = res.url
    } catch (err) { alert(err.message) }
  }

  const handlePortal = async () => {
    try {
      const res = await billing.portal()
      window.location.href = res.url
    } catch (err) { alert(err.message) }
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Billing & Subscription</h2>
      {sub && (
        <div style={{ padding: 20, background: '#fff', borderRadius: 12, border: '1px solid #eee', marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <strong>Current Plan: {sub.plan?.toUpperCase()}</strong>
              <span style={{ marginLeft: 8, padding: '2px 8px', background: sub.status === 'active' ? '#f0fdf4' : '#fef2f2', color: sub.status === 'active' ? '#16a34a' : '#dc2626', borderRadius: 4, fontSize: '0.8rem' }}>{sub.status}</span>
            </div>
            {sub.plan !== 'free' && <button onClick={handlePortal} style={{ padding: '8px 16px', background: '#f1f5f9', border: '1px solid #ddd', borderRadius: 8, cursor: 'pointer' }}>Manage Subscription</button>}
          </div>
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
        {plans.map(p => (
          <div key={p.id} style={{ padding: 28, background: '#fff', borderRadius: 12, border: sub?.plan === p.id ? '2px solid #3b82f6' : '1px solid #eee', textAlign: 'center' }}>
            <h3 style={{ marginBottom: 8 }}>{p.name}</h3>
            <div style={{ fontSize: '2rem', fontWeight: 700, marginBottom: 8 }}>${p.price}<span style={{ fontSize: '0.9rem', fontWeight: 400, color: '#666' }}>/mo</span></div>
            <p style={{ color: '#666', marginBottom: 16 }}>{p.messages_day === -1 ? 'Unlimited' : p.messages_day} messages/day</p>
            <ul style={{ listStyle: 'none', padding: 0, marginBottom: 20, textAlign: 'left' }}>
              {p.features.map(f => <li key={f} style={{ padding: '4px 0', fontSize: '0.9rem' }}>✓ {f}</li>)}
            </ul>
            {sub?.plan === p.id ? (
              <button disabled style={{ width: '100%', padding: 10, background: '#e2e8f0', border: 'none', borderRadius: 8, color: '#64748b', cursor: 'default' }}>Current Plan</button>
            ) : sub?.plan === 'free' || !sub ? (
              <button onClick={() => handleUpgrade(p.id)} style={{ width: '100%', padding: 10, background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>{p.price === 0 ? 'Get Started' : 'Upgrade'}</button>
            ) : (
              <button onClick={() => handleUpgrade(p.id)} style={{ width: '100%', padding: 10, background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>Switch Plan</button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── App ───────────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
