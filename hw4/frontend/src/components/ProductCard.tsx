import { Link } from 'react-router-dom'
import { formatPrice } from '../api'
import type { CardProduct } from '../types'

const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

export default function ProductCard({ product }: { product: CardProduct }) {
  const inStock = product.sizes_in_stock
  const soldOut = product.sizes_sold_out
  // Cards the agent puts on the page carry no stock data, so the strip is simply omitted
  // rather than rendered as "everything sold out".
  const hasStockData = Boolean(inStock && soldOut)
  const allGone = hasStockData && inStock!.length === 0

  return (
    <Link to={`/products/${product.product_id}`} className="card">
      <div className="card-img">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {allGone && <span className="card-badge">Sold out</span>}
      </div>
      <div className="card-body">
        <span className="card-type">{product.garment_type}</span>
        <span className="card-name">{product.name}</span>
        <span className="card-desc">{product.short_description}</span>

        {hasStockData && !allGone && (
          <div className="card-sizes" aria-label="Sizes available">
            {SIZES.filter((s) => inStock!.includes(s) || soldOut!.includes(s)).map((s) => (
              <span
                key={s}
                className={inStock!.includes(s) ? 'size-pip' : 'size-pip gone'}
                title={inStock!.includes(s) ? `${s} available` : `${s} sold out`}
              >
                {s}
              </span>
            ))}
          </div>
        )}

        <span className="card-price">{formatPrice(product.price)}</span>
      </div>
    </Link>
  )
}
