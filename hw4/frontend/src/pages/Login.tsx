import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Login() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!email || !password) {
      setError('Enter your email and password to continue.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      await signIn(email, password)
      navigate('/products')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not sign you in.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <div className="form-wrap">
        <h1 style={{ textAlign: 'center' }}>Welcome back</h1>
        <p className="lede" style={{ textAlign: 'center', margin: '0 auto 24px' }}>
          Sign in to pick up your chat history where you left it.
        </p>
        <div className="form-card">
          {error && <p className="error">{error}</p>}
          <form onSubmit={onSubmit}>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email" type="email" autoComplete="email"
                value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="you@yale.edu"
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password" type="password" autoComplete="current-password"
                value={password} onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
          <p className="form-foot">
            New here? <Link to="/create-account">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
