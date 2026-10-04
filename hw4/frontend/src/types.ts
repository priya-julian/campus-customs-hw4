export type Product = {
  product_id: string
  name: string
  garment_type: string
  description: string
  short_description: string
  colors: string[]
  search_tags: string[]
  price: number
  image_url: string
  sizes_in_stock: string[]
  sizes_sold_out: string[]
  total_stock: number
}

/** The fields a product card needs. Both Product and ProductCard satisfy this. */
export type CardProduct = {
  product_id: string
  name: string
  garment_type: string
  short_description: string
  price: number
  image_url: string
  /** Absent on cards the agent returns, which carry no stock data. */
  sizes_in_stock?: string[]
  sizes_sold_out?: string[]
}

export type SizeStock = {
  size: string
  quantity: number
  in_stock: boolean
}

export type ProductDetail = Product & {
  sizes: SizeStock[]
  total_stock: number
}

export type ProductCard = {
  product_id: string
  name: string
  price: number
  image_url: string
  garment_type: string
  short_description: string
}

export type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
  products?: ProductCard[]
}

export type PageContext = {
  path: string
  product_id: string | null
}

export type ChatResponse = {
  reply: string
  products: ProductCard[]
  saved: boolean
}

export type User = {
  id: number
  name: string
  first_name: string | null
  last_name: string | null
  email: string
}

export type AuthResponse = {
  token: string
  user: User
}
