import type { EntityId } from './product'

export interface CartItem {
  id: EntityId
  productId: EntityId
  productName: string
  subtitle: string
  mainImage: string
  price: number
  stock: number
  quantity: number
  subtotal: number
  productStatus: number
}

export interface CartItemPayload {
  productId: EntityId
  quantity: number
}
