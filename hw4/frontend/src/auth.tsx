import {
  createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode,
} from 'react'
import { fetchMe, login as loginRequest, signup as signupRequest } from './api'
import type { User } from './types'

const TOKEN_KEY = 'campus-customs-token'

type AuthState = {
  user: User | null
  ready: boolean
  signIn: (email: string, password: string) => Promise<void>
  register: (input: {
    first_name: string; last_name: string; email: string; password: string
  }) => Promise<void>
  signOut: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [ready, setReady] = useState(false)

  // On load, check whether the saved token still names a real user.
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setReady(true)
      return
    }
    fetchMe(token)
      .then(setUser)
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setReady(true))
  }, [])

  const signIn = useCallback(async (email: string, password: string) => {
    const { token, user: signedIn } = await loginRequest({ email, password })
    localStorage.setItem(TOKEN_KEY, token)
    setUser(signedIn)
  }, [])

  const register = useCallback(async (input: {
    first_name: string; last_name: string; email: string; password: string
  }) => {
    const { token, user: created } = await signupRequest(input)
    localStorage.setItem(TOKEN_KEY, token)
    setUser(created)
  }, [])

  const signOut = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, ready, signIn, register, signOut }),
    [user, ready, signIn, register, signOut],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}

/** The stored token, for callers that need to authenticate a request themselves. */
export const getToken = () => localStorage.getItem(TOKEN_KEY)
