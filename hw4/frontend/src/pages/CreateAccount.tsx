import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const MIN_PASSWORD_LENGTH = 8

export default function CreateAccount() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    firstName: '', lastName: '', email: '', password: '', confirm: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const update = (key: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!form.firstName || !form.lastName || !form.email || !form.password) {
      setError('Please fill in every field.')
      return
    }
    if (form.password !== form.confirm) {
      setError('Those two passwords do not match.')
      return
    }
    if (form.password.length < MIN_PASSWORD_LENGTH) {
      setError(`Use at least ${MIN_PASSWORD_LENGTH} characters for your password.`)
      return
    }
    setBusy(true)
    setError(null)
    try {
      await register({
        first_name: form.firstName,
        last_name: form.lastName,
        email: form.email,
        password: form.password,
      })
      navigate('/products')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create that account.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <div className="form-wrap">
        <h1 style={{ textAlign: 'center' }}>Create an account</h1>
        <p className="lede" style={{ textAlign: 'center', margin: '0 auto 24px' }}>
          Save your conversations and come back to the items you were looking at.
        </p>
        <div className="form-card">
          {error && <p className="error">{error}</p>}
          <form onSubmit={onSubmit}>
            <div className="row">
              <div className="field">
                <label htmlFor="first">First name</label>
                <input id="first" value={form.firstName} onChange={update('firstName')} />
              </div>
              <div className="field">
                <label htmlFor="last">Last name</label>
                <input id="last" value={form.lastName} onChange={update('lastName')} />
              </div>
            </div>
            <div className="field">
              <label htmlFor="newemail">Email</label>
              <input
                id="newemail" type="email" autoComplete="email"
                value={form.email} onChange={update('email')} placeholder="you@yale.edu"
              />
            </div>
            <div className="field">
              <label htmlFor="newpass">Password</label>
              <input
                id="newpass" type="password" autoComplete="new-password"
                value={form.password} onChange={update('password')}
              />
            </div>
            <div className="field">
              <label htmlFor="confirm">Confirm password</label>
              <input
                id="confirm" type="password" autoComplete="new-password"
                value={form.confirm} onChange={update('confirm')}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? 'Creating…' : 'Create account'}
            </button>
          </form>
          <p className="form-foot">
            Already have one? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
