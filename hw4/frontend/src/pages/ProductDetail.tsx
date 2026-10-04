import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice } from '../api'
import type { ProductDetail as Detail } from '../types'

export default function ProductDetail() {
  const { productId } = useParams<{ productId: string }>()
  const [product, setProduct] = useState<Detail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!productId) return
    setLoading(true)
    setError(null)
    fetchProduct(productId)
      .then(setProduct)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false))
  }, [productId])

  if (loading) return <div className="page"><p className="state">Loading…</p></div>
  if (error || !product) {
    return (
      <div className="page">
        <p className="state err">We could not find that item ({error}).</p>
        <p style={{ textAlign: 'center' }}><Link to="/products">Back to all products</Link></p>
      </div>
    )
  }

  const available = product.sizes.filter((s) => s.in_stock)

  return (
    <div className="page">
      <p className="crumb">
        <Link to="/products">Products</Link> <span>/</span> {product.name}
      </p>

      <div className="detail">
        <div className="detail-img">
          <img src={product.image_url} alt={product.name} />
        </div>

        <div>
          <span className="card-type">{product.garment_type}</span>
          <h1>{product.name}</h1>
          <p className="detail-price">{formatPrice(product.price)}</p>
          <p className="detail-desc">{product.description}</p>

          <div className="spec">
            <h3>Colours</h3>
            <div className="chips">
              {product.colors.map((c) => <span key={c} className="chip">{c}</span>)}
            </div>
          </div>

          <div className="spec">
            <h3>Sizes &amp; stock</h3>
            <div className="sizes">
              {product.sizes.map((s) => (
                <div key={s.size} className={s.in_stock ? 'size' : 'size out'}>
                  <div className="size-label">{s.size}</div>
                  <div className="size-stock">
                    {s.in_stock ? `${s.quantity} left` : 'Sold out'}
                  </div>
                </div>
              ))}
            </div>
            <p className="stock-note">
              {available.length === 0
                ? 'Every size is sold out right now.'
                : `${product.total_stock} in stock across ${available.length} of ${product.sizes.length} sizes.`}
            </p>
          </div>

          <div className="spec">
            <h3>Tags</h3>
            <div className="chips">
              {product.search_tags.map((t) => <span key={t} className="chip">{t}</span>)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
