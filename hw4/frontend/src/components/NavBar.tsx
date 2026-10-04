import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import HandsomeDan from './HandsomeDan'

const PAGES = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const { user, ready, signOut } = useAuth()
  const navigate = useNavigate()

  function onSignOut() {
    signOut()
    navigate('/')
  }

  const linkClass = (cta?: boolean) => ({ isActive }: { isActive: boolean }) =>
    [cta ? 'cta' : '', isActive ? 'active' : ''].filter(Boolean).join(' ')

  return (
    <nav className="nav">
      <div className="nav-inner">
        <NavLink to="/" className="brand">
          <HandsomeDan size={34} />
          <span className="brand-text">
            <span className="brand-name">Campus Customs</span>
            <span className="brand-sub">Yale Bulldog Blue</span>
          </span>
        </NavLink>
        <div className="nav-links">
          {PAGES.map((page) => (
            <NavLink key={page.to} to={page.to} end={page.end} className={linkClass()}>
              {page.label}
            </NavLink>
          ))}

          {/* Hold the account links back until we know whether there is a session, so the
              nav does not flash "Log in" at someone who is already signed in. */}
          {ready && !user && (
            <>
              <NavLink to="/login" className={linkClass()}>Log in</NavLink>
              <NavLink to="/create-account" className={linkClass(true)}>Create Account</NavLink>
            </>
          )}
          {ready && user && (
            <>
              <span className="nav-user">
                Hi, {user.first_name?.trim() || user.name.split(' ')[0]}
              </span>
              <button type="button" className="nav-signout" onClick={onSignOut}>
                Log out
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
