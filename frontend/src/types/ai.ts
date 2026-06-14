import type { EntityId } from './product'

export interface AiResponse {
  scene: string
  content: string
  model: string
  fallback: boolean
  recommendedProductIds: EntityId[]
}

export interface ProductCopywritingPayload {
  productName: string
  sellingPoints: string[]
  targetUser: string
}
