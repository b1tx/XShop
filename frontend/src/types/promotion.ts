import type { EntityId } from './product'

export interface PromotionProduct {
  id: EntityId
  activityId: EntityId
  productId: EntityId
  productName: string
  subtitle: string
  mainImage: string
  originalPrice: number
  promotionPrice: number
  promotionStock: number
  remainingStock: number
  limitPerUser: number
}

export interface Promotion {
  id: EntityId
  name: string
  startTime: string
  endTime: string
  status: number
  timeStatus: 'NOT_STARTED' | 'ACTIVE' | 'ENDED' | 'DISABLED'
  createdAt?: string
  products: PromotionProduct[]
}

export interface PromotionPayload {
  name: string
  startTime: string
  endTime: string
  status: number
  products: Array<{
    productId: EntityId
    promotionPrice: number
    promotionStock: number
    limitPerUser: number
  }>
}

export interface PromotionOrderPayload {
  promotionProductId: EntityId
  quantity: number
  receiverName: string
  receiverPhone: string
  receiverAddress: string
}
