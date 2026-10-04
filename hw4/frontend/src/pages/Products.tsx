import { useEffect, useMemo, useState } from 'react'
import ProductCard from '../components/ProductCard'
import { fetchProducts } from '../api'
import { useChatResults } from '../chatResults'
import type { Product } from '../types'

// garment_type in the catalogue is free text ("t-shirt", "short-sleeve T-shirt",
// "heavyweight short-sleeve t-shirt" are all separate values), so the filter buckets
// products by keyword instead of matching the column exactly.
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

const CATEGORIES: { label: string; match: (t: string) => boolean }[] = [
  { label: 'All items', match: () => true },
  { label: 'Crewnecks', match: (t) => t.includes('crewneck') || t.includes('crew-neck') },
  { label: 'Hoodies', match: (t) => t.includes('hood') },
  { label: 'Quarter-zips', match: (t) => t.includes('quarter-zip') },
  { label: 'T-shirts', match: (t) => t.includes('t-shirt') },
  { label: 'Jackets', match: (t) => t.includes('jacket') },
]

export default function Products() {
  const { products: chatMatches, query: chatQuery, clear: clearChatMatches } = useChatResults()
  const [products, setProducts] = useState<Product[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('All items')
  const [size, setSize] = useState('Any size')

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false))
  }, [])

  const visible = useMemo(() => {
    const term = query.trim().toLowerCase()
    const bucket = CATEGORIES.find((c) => c.label === category) ?? CATEGORIES[0]
    return products.filter((p) => {
      if (!bucket.match(p.garment_type.toLowerCase())) return false
      // "My size" is the filter a clothing shopper actually wants: show me only what I
      // could buy today in the size I wear.
      if (size !== 'Any size' && !p.sizes_in_stock.includes(size)) return false
      if (!term) return true
      const haystack = [p.name, p.description, p.garment_type, ...p.colors, ...p.search_tags]
        .join(' ')
        .toLowerCase()
      return haystack.includes(term)
    })
  }, [products, query, category, size])

  return (
    <div className="page">
      <h1>Products</h1>
      <p className="lede">
        Everything we currently carry. Click any item for the full description, sizes, and
        what is actually left on the shelf.
      </p>

      <div className="toolbar" style={{ marginTop: 24 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name, colour, school, or sport…"
          aria-label="Search products"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          aria-label="Filter by category"
        >
          {CATEGORIES.map((c) => (
            <option key={c.label}>{c.label}</option>
          ))}
        </select>
        <select
          value={size}
          onChange={(e) => setSize(e.target.value)}
          aria-label="Filter by size in stock"
        >
          {['Any size', ...SIZES].map((s) => (
            // Explicit value: without it the option's value is its label text, so the
            // filter compares "Available in XS" against the size list and matches nothing.
            <option key={s} value={s}>
              {s === 'Any size' ? s : `Available in ${s}`}
            </option>
          ))}
        </select>
        {!loading && !error && (
          <span className="result-count">
            {visible.length} {visible.length === 1 ? 'item' : 'items'}
          </span>
        )}
      </div>

      {/* What the shop assistant just matched, pinned above the full catalogue. These
          are ProductCards like any other, so clicking one opens the same detail page. */}
      {chatMatches.length > 0 && (
        <section className="chat-matches">
          <div className="chat-matches-head">
            <div>
              <span className="eyebrow-blue">From your chat</span>
              <h2>{chatMatches.length} {chatMatches.length === 1 ? 'match' : 'matches'} for “{chatQuery}”</h2>
            </div>
            <button type="button" className="chat-matches-clear" onClick={clearChatMatches}>
              Clear
            </button>
          </div>
          <div className="grid">
            {chatMatches.map((p) => (
              <ProductCard key={`chat-${p.product_id}`} product={p} />
            ))}
          </div>
        </section>
      )}

      {chatMatches.length > 0 && <h2 className="all-items-heading">All items</h2>}

      {loading && <p className="state">Loading the catalogue…</p>}
      {error && (
        <p className="state err">
          Could not load products ({error}). Is the backend running on port 8001?
        </p>
      )}
      {!loading && !error && visible.length === 0 && (
        <p className="state">
          Nothing matches that{size !== 'Any size' ? ` in ${size}` : ''}. Try a broader term
          {size !== 'Any size' ? ' or another size' : ''}.
        </p>
      )}

      <div className="grid">
        {visible.map((p) => (
          <ProductCard key={p.product_id} product={p} />
        ))}
      </div>
    </div>
  )
}
