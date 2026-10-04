import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import type { ProductCard } from './types'

/**
 * The products the agent surfaced in its most recent reply.
 *
 * Chat lives in a floating panel and the product grid lives in a route, so the two cannot
 * talk through props. This context is the seam: the panel writes what the agent matched,
 * the Products page reads it and renders it above the full catalogue.
 */
type ChatResultsState = {
  products: ProductCard[]
  query: string
  show: (query: string, products: ProductCard[]) => void
  clear: () => void
}

const ChatResultsContext = createContext<ChatResultsState | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [products, setProducts] = useState<ProductCard[]>([])
  const [query, setQuery] = useState('')

  const show = useCallback((nextQuery: string, nextProducts: ProductCard[]) => {
    setQuery(nextQuery)
    setProducts(nextProducts)
  }, [])

  const clear = useCallback(() => {
    setProducts([])
    setQuery('')
  }, [])

  const value = useMemo(() => ({ products, query, show, clear }), [products, query, show, clear])
  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

export function useChatResults(): ChatResultsState {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used inside ChatResultsProvider')
  return ctx
}
