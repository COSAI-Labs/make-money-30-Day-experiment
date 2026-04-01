'use client'

import { useUser } from '@auth0/nextjs-auth0/client'
import { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export default function Home() {
  const { user, isLoading } = useUser()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMsg] }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.content }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Failed to get response.' }])
    }
    setLoading(false)
  }

  if (isLoading) return <div style={styles.center}>Loading...</div>

  if (!user) {
    return (
      <div style={styles.landing}>
        <div style={styles.hero}>
          <h1 style={styles.title}>DevAgent</h1>
          <p style={styles.subtitle}>AI-Powered Developer Assistant with Secure Tool Access</p>
          <p style={styles.desc}>
            An AI agent that securely accesses 70+ developer tools and your GitHub repos,
            powered by Auth0 Token Vault for credential management.
          </p>
          <a href="/api/auth/login" style={styles.loginBtn}>Sign in with GitHub</a>
          <div style={styles.features}>
            <div style={styles.feature}>
              <h3>70+ Dev Tools</h3>
              <p>JSON, PDF, QR, hash, UUID, DNS, regex, and more via ToolPipe API</p>
            </div>
            <div style={styles.feature}>
              <h3>Secure Token Vault</h3>
              <p>Auth0 Token Vault manages your GitHub tokens. The AI never sees raw credentials.</p>
            </div>
            <div style={styles.feature}>
              <h3>AI-Powered</h3>
              <p>Natural language interface to developer tools. Just ask and the agent does it.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.app}>
      <nav style={styles.nav}>
        <span style={styles.logo}>DevAgent</span>
        <div style={styles.navRight}>
          <img src={user.picture || ''} alt="" style={styles.avatar} />
          <span>{user.name}</span>
          <a href="/api/auth/logout" style={styles.logoutBtn}>Logout</a>
        </div>
      </nav>
      <div style={styles.chatArea}>
        {messages.length === 0 && (
          <div style={styles.welcome}>
            <h2>Welcome, {user.name}!</h2>
            <p>I can help you with developer tasks. Try asking me to:</p>
            <div style={styles.suggestions}>
              {['Format this JSON: {"name":"test","items":[1,2,3]}',
                'Generate a QR code for https://github.com',
                'Look up DNS records for google.com',
                'Generate a secure password',
                'List my GitHub repos'].map((s, i) => (
                <button key={i} onClick={() => { setInput(s) }} style={styles.suggestion}>{s}</button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={m.role === 'user' ? styles.userMsg : styles.assistantMsg}>
            <div style={styles.msgLabel}>{m.role === 'user' ? 'You' : 'DevAgent'}</div>
            <div style={styles.msgContent} dangerouslySetInnerHTML={{ __html: formatContent(m.content) }} />
          </div>
        ))}
        {loading && <div style={styles.assistantMsg}><div style={styles.msgLabel}>DevAgent</div><div style={styles.typing}>Thinking...</div></div>}
        <div ref={bottomRef} />
      </div>
      <div style={styles.inputArea}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask me anything about dev tools..."
          style={styles.input}
        />
        <button onClick={sendMessage} disabled={loading} style={styles.sendBtn}>Send</button>
      </div>
    </div>
  )
}

function formatContent(text: string): string {
  return text
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre style="background:#1a1a2e;color:#e0e0e0;padding:12px;border-radius:8px;overflow-x:auto;font-size:0.85rem">$2</pre>')
    .replace(/`([^`]+)`/g, '<code style="background:#f4f4f4;padding:2px 6px;border-radius:4px;font-size:0.9rem">$1</code>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

const styles: Record<string, React.CSSProperties> = {
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' },
  landing: { background: '#0a0a0a', color: '#fff', minHeight: '100vh' },
  hero: { maxWidth: 800, margin: '0 auto', padding: '80px 20px', textAlign: 'center' },
  title: { fontSize: '3.5rem', fontWeight: 800, marginBottom: 8, background: 'linear-gradient(135deg, #6c63ff, #3b82f6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
  subtitle: { fontSize: '1.3rem', color: '#94a3b8', marginBottom: 24 },
  desc: { fontSize: '1rem', color: '#64748b', maxWidth: 500, margin: '0 auto 32px', lineHeight: 1.6 },
  loginBtn: { display: 'inline-block', padding: '14px 32px', background: '#6c63ff', color: '#fff', borderRadius: 10, textDecoration: 'none', fontWeight: 600, fontSize: '1.1rem' },
  features: { display: 'flex', gap: 24, marginTop: 64, textAlign: 'left' },
  feature: { flex: 1, padding: 24, background: '#1a1a1a', borderRadius: 12, border: '1px solid #2a2a2a' },
  app: { display: 'flex', flexDirection: 'column', height: '100vh', background: '#f8f9fa' },
  nav: { background: '#1a1a2e', color: '#fff', padding: '12px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  logo: { fontWeight: 700, fontSize: '1.2rem', background: 'linear-gradient(135deg, #6c63ff, #3b82f6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
  navRight: { display: 'flex', alignItems: 'center', gap: 12, fontSize: '0.9rem' },
  avatar: { width: 28, height: 28, borderRadius: '50%' },
  logoutBtn: { color: '#94a3b8', textDecoration: 'none', fontSize: '0.85rem' },
  chatArea: { flex: 1, overflowY: 'auto', padding: 20, maxWidth: 800, margin: '0 auto', width: '100%' },
  welcome: { textAlign: 'center', padding: 40 },
  suggestions: { display: 'flex', flexDirection: 'column', gap: 8, marginTop: 16 },
  suggestion: { padding: '10px 16px', background: '#fff', border: '1px solid #ddd', borderRadius: 8, cursor: 'pointer', textAlign: 'left', fontSize: '0.9rem' },
  userMsg: { marginBottom: 16, textAlign: 'right' },
  assistantMsg: { marginBottom: 16 },
  msgLabel: { fontSize: '0.75rem', color: '#666', marginBottom: 4 },
  msgContent: { display: 'inline-block', padding: '12px 16px', borderRadius: 12, maxWidth: '80%', textAlign: 'left', background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', lineHeight: 1.6 },
  typing: { color: '#666', fontStyle: 'italic' },
  inputArea: { padding: '16px 20px', borderTop: '1px solid #eee', display: 'flex', gap: 8, maxWidth: 800, margin: '0 auto', width: '100%' },
  input: { flex: 1, padding: '12px 16px', border: '1px solid #ddd', borderRadius: 10, fontSize: '1rem', outline: 'none' },
  sendBtn: { padding: '12px 24px', background: '#6c63ff', color: '#fff', border: 'none', borderRadius: 10, fontWeight: 600, cursor: 'pointer' },
}
