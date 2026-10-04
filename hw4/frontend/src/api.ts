import { getToken } from './auth'
import type {
  AuthResponse, ChatMessage, ChatResponse, PageContext, Product, ProductDetail, User,
} from './types'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export const fetchProducts = () => get<Product[]>('/api/products')

export const fetchProduct = (id: string) =>
  get<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

/** Pull the human-readable message out of a FastAPI error body. */
async function errorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json()
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail) && body.detail[0]?.msg) {
      return String(body.detail[0].msg).replace(/^Value error,\s*/, '')
    }
  } catch {
    /* fall through to the generic message */
  }
  return fallback
}

async function post<T>(path: string, body: unknown, fallback: string): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await errorMessage(res, fallback))
  return res.json() as Promise<T>
}

export const signup = (input: {
  first_name: string
  last_name: string
  email: string
  password: string
}) => post<AuthResponse>('/api/auth/signup', input, 'Could not create that account.')

export const login = (input: { email: string; password: string }) =>
  post<AuthResponse>('/api/auth/login', input, 'Could not sign you in.')

export async function fetchMe(token: string): Promise<User> {
  const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error('Session expired')
  return res.json() as Promise<User>
}

export const formatPrice = (price: number) =>
  price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })

/** Send one shopper message to the agent and get its reply plus matching products. */
export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  page: PageContext,
): Promise<ChatMessage> {
  const token = getToken()
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // Signing in lets the server read and write this conversation in chat_messages.
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      message,
      // Only used when signed out; the server prefers its own saved history.
      history: history.map((m) => ({ role: m.role, content: m.content })),
      // Lets "do you have this in pink?" resolve to the item on screen.
      page,
    }),
  })
  if (!res.ok) throw new Error(await errorMessage(res, 'The assistant is unavailable.'))
  const data = (await res.json()) as ChatResponse
  return { role: 'assistant', content: data.reply, products: data.products }
}

/** Saved conversation for the signed-in shopper, oldest first. */
export async function fetchChatHistory(): Promise<ChatMessage[]> {
  const token = getToken()
  if (!token) return []
  const res = await fetch('/api/chat/history', {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) return []
  return (await res.json()) as ChatMessage[]
}
