import type { EntityId } from './product'

export type OrderStatus = 'CREATED' | 'PAID' | 'SHIPPED' | 'RECEIVED' | 'CANCELLED'

export interface OrderItem {
  id: EntityId
  productId: EntityId
  promotionProductId?: EntityId
  productName: string
  productImage: string
  price: number
  quantity: number
  totalAmount: number
}

export interface Order {
  id: EntityId
  orderNo: string
  userId: EntityId
  username?: string
  nickname?: string
  totalAmount: number
  status: OrderStatus
  receiverName: string
  receiverPhone: string
  receiverAddress: string
  createdAt: string
  paidAt?: string
  items: OrderItem[]
}

export interface CreateOrderPayload {
  cartItemIds: EntityId[]
  receiverName: string
  receiverPhone: string
  receiverAddress: string
}
